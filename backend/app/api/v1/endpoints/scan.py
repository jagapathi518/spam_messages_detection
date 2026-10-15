"""Scan API Endpoints: Single and Batch text message detection."""
import time
from fastapi import APIRouter, HTTPException, Depends
from backend.app.schemas.scan import (
    ScanRequest,
    ScanResponse,
    BatchScanRequest,
    BatchScanResponse
)
from backend.app.services.detector import SpamDetector
from backend.app.db.supabase_client import db_service

router = APIRouter()

# Global detector instance (initialized on startup)
_detector_instance = None

def get_detector() -> SpamDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SpamDetector()
    return _detector_instance


@router.post("/scan", response_model=ScanResponse, summary="Scan a single short message")
def scan_message(
    payload: ScanRequest,
    detector: SpamDetector = Depends(get_detector)
):
    """
    Analyzes a short mobile text message (SMS/Chat) across 3 detection layers:
    1. **Layer 1: Rules & Heuristics** (Phishing URLs, IP links, lookalikes, regex, obfuscation)
    2. **Layer 2: Calibrated Machine Learning** (Fast word & char n-grams with calibrated probability)
    3. **Layer 3: Groq LLM Second Opinion** (Triggered if ML confidence is borderline 0.35-0.65)
    
    Returns label (`SPAM`, `SUSPICIOUS`, or `SAFE`), risk score, confidence, and human-readable reasons.
    """
    t0 = time.perf_counter()
    result = detector.scan(
        text=payload.text,
        sender_id=payload.sender_id or "",
        user_id=payload.user_id or "anonymous"
    )
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    result["latency_ms"] = latency_ms

    # Log telemetry asynchronously/safely
    db_service.log_scan(
        text_preview=payload.text,
        label=result["label"],
        confidence=result["confidence"],
        risk_score=result["risk_score"],
        layers_used=result["layers_used"],
        latency_ms=latency_ms,
        user_id=payload.user_id or "anonymous"
    )

    return result


@router.post("/scan/batch", response_model=BatchScanResponse, summary="Scan up to 50 short messages in batch")
def scan_batch(
    payload: BatchScanRequest,
    detector: SpamDetector = Depends(get_detector)
):
    """
    Scans a batch of up to 50 short text messages simultaneously (e.g. mobile inbox scan).
    """
    if len(payload.messages) > 50:
        raise HTTPException(status_code=400, detail="Batch size limit is 50 messages.")

    t0 = time.perf_counter()
    results = []
    spam_count = 0
    suspicious_count = 0
    safe_count = 0

    for item in payload.messages:
        item_t0 = time.perf_counter()
        scan_res = detector.scan(
            text=item.text,
            sender_id=item.sender_id or "",
            user_id=item.user_id or "anonymous"
        )
        item_lat = round((time.perf_counter() - item_t0) * 1000.0, 2)
        scan_res["latency_ms"] = item_lat
        results.append(scan_res)

        # Update stats
        if scan_res["label"] == "SPAM":
            spam_count += 1
        elif scan_res["label"] == "SUSPICIOUS":
            suspicious_count += 1
        else:
            safe_count += 1

        # Log individual scan
        db_service.log_scan(
            text_preview=item.text,
            label=scan_res["label"],
            confidence=scan_res["confidence"],
            risk_score=scan_res["risk_score"],
            layers_used=scan_res["layers_used"],
            latency_ms=item_lat,
            user_id=item.user_id or "anonymous"
        )

    total_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    return BatchScanResponse(
        results=results,
        total=len(results),
        spam_count=spam_count,
        suspicious_count=suspicious_count,
        safe_count=safe_count,
        total_latency_ms=total_latency_ms
    )
