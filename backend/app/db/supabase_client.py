"""Database / Supabase Client with graceful in-memory fallback."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

logger = logging.getLogger("spam_shield.db")

class DatabaseService:
    def __init__(self):
        self.client = None
        self._init_supabase()
        
        # In-memory storage fallback
        self._local_scan_logs: List[Dict[str, Any]] = []
        self._local_user_feedback: List[Dict[str, Any]] = []
        self._max_local_logs = 1000

    def _init_supabase(self):
        if settings.SUPABASE_URL and (settings.SUPABASE_SECRET_KEY or settings.SUPABASE_PUBLISHABLE_KEY):
            try:
                from supabase import create_client
                key = settings.SUPABASE_SECRET_KEY or settings.SUPABASE_PUBLISHABLE_KEY
                self.client = create_client(settings.SUPABASE_URL, key)
                logger.info("Supabase client successfully initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}. Using in-memory fallback.")
                self.client = None
        else:
            logger.info("No Supabase credentials provided; using in-memory store.")

    def log_scan(
        self,
        text_preview: str,
        label: str,
        confidence: float,
        risk_score: float,
        layers_used: List[str],
        latency_ms: float,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """Logs an anonymous scan result for telemetry and metrics."""
        record = {
            "id": str(uuid.uuid4()),
            "text_preview": text_preview[:120],
            "label": label,
            "confidence": round(confidence, 3),
            "risk_score": round(risk_score, 3),
            "layers_used": layers_used,
            "latency_ms": round(latency_ms, 2),
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # 1. Try Supabase
        if self.client:
            try:
                self.client.table("scan_logs").insert(record).execute()
                return record
            except Exception as e:
                logger.debug(f"Supabase log_scan fallback to memory: {e}")

        # 2. Local fallback
        self._local_scan_logs.insert(0, record)
        if len(self._local_scan_logs) > self._max_local_logs:
            self._local_scan_logs.pop()
        return record

    def save_feedback(
        self,
        text: str,
        predicted_label: str,
        user_correction: str,
        comments: str = ""
    ) -> Dict[str, Any]:
        """Stores user feedback for continuous learning and retraining."""
        record = {
            "id": str(uuid.uuid4()),
            "text": text,
            "predicted_label": predicted_label.upper(),
            "user_correction": user_correction.upper(),
            "comments": comments.strip(),
            "is_verified": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # 1. Try Supabase
        if self.client:
            try:
                res = self.client.table("user_feedback").insert(record).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
                return record
            except Exception as e:
                logger.debug(f"Supabase save_feedback fallback to memory: {e}")

        # 2. Local fallback
        self._local_user_feedback.insert(0, record)
        return record

    def get_stats(self) -> Dict[str, Any]:
        """Returns aggregated telemetry statistics."""
        # Check Supabase first
        if self.client:
            try:
                # Count queries
                logs_res = self.client.table("scan_logs").select("label, latency_ms", count="exact").execute()
                feedback_res = self.client.table("user_feedback").select("id", count="exact").execute()
                
                rows = logs_res.data or []
                total_scans = logs_res.count if logs_res.count is not None else len(rows)
                
                spam_count = sum(1 for r in rows if r.get("label") == "SPAM")
                suspicious_count = sum(1 for r in rows if r.get("label") == "SUSPICIOUS")
                safe_count = sum(1 for r in rows if r.get("label") == "SAFE")
                avg_latency = (
                    sum(r.get("latency_ms", 0.0) for r in rows) / len(rows)
                    if rows else 0.0
                )
                
                # Fetch recent scans
                recent_res = self.client.table("scan_logs").select(
                    "id, text_preview, label, confidence, risk_score, latency_ms, created_at"
                ).order("created_at", desc=True).limit(15).execute()

                return {
                    "total_scans": total_scans,
                    "spam_detected": spam_count,
                    "suspicious_flagged": suspicious_count,
                    "safe_verified": safe_count,
                    "feedback_count": feedback_res.count if feedback_res.count is not None else len(self._local_user_feedback),
                    "avg_latency_ms": round(avg_latency, 2),
                    "storage": "supabase",
                    "recent_scans": recent_res.data or []
                }
            except Exception as e:
                logger.debug(f"Supabase stats query fallback: {e}")

        # Local in-memory stats
        total = len(self._local_scan_logs)
        spam = sum(1 for l in self._local_scan_logs if l["label"] == "SPAM")
        suspicious = sum(1 for l in self._local_scan_logs if l["label"] == "SUSPICIOUS")
        safe = sum(1 for l in self._local_scan_logs if l["label"] == "SAFE")
        avg_lat = (
            sum(l["latency_ms"] for l in self._local_scan_logs) / total
            if total > 0 else 0.0
        )

        return {
            "total_scans": total,
            "spam_detected": spam,
            "suspicious_flagged": suspicious,
            "safe_verified": safe,
            "feedback_count": len(self._local_user_feedback),
            "avg_latency_ms": round(avg_lat, 2),
            "storage": "in_memory",
            "recent_scans": self._local_scan_logs[:15]
        }

# Global singleton
db_service = DatabaseService()
