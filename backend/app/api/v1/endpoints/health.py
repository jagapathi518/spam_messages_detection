"""Health & Telemetry Endpoints."""
import os
import time
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.db.supabase_client import db_service

router = APIRouter()
START_TIME = time.time()


def _get_ram_usage_mb() -> float:
    """Safely retrieves process memory without requiring external dependencies."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / (1024 * 1024), 2)
    except Exception:
        pass

    # Windows ctypes fallback
    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return round(counters.WorkingSetSize / (1024 * 1024), 2)
    except Exception:
        pass

    return 45.0  # Estimated baseline RAM


@router.get("/health", summary="Service Health Check")
def health_check():
    """Returns service operational status, model readiness, and system uptime."""
    from backend.app.api.v1.endpoints.scan import get_detector
    uptime_sec = round(time.time() - START_TIME, 2)
    try:
        detector = get_detector()
        ml_ready = detector.ml_engine.is_ready()
    except Exception:
        ml_ready = False

    return {
        "status": "healthy" if ml_ready else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime_seconds": uptime_sec,
        "ml_engine_loaded": ml_ready,
        "llm_engine_configured": bool(settings.GROQ_API_KEY),
        "database_storage": "supabase" if db_service.client else "in_memory"
    }


@router.get("/metrics", summary="Performance & Telemetry Metrics")
def metrics():
    """Returns system memory, scan statistics, and throughput."""
    ram_mb = _get_ram_usage_mb()
    stats_data = db_service.get_stats()

    return {
        "ram_usage_mb": ram_mb,
        "total_scans_processed": stats_data["total_scans"],
        "spam_ratio": round(stats_data["spam_detected"] / max(stats_data["total_scans"], 1), 3),
        "average_scan_latency_ms": stats_data["avg_latency_ms"],
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }
