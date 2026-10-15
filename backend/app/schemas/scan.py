"""Pydantic Request and Response Schemas."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ScanRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Short text message to analyze (SMS, WhatsApp/Telegram chat)"
    )
    sender_id: Optional[str] = Field(
        "",
        max_length=50,
        description="Optional sender identifier / telecom header (e.g., 'AX-HDFCBK', '+919876543210')"
    )
    user_id: Optional[str] = Field(
        "anonymous",
        max_length=64,
        description="Anonymous client identifier for rate-limiting"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Your SBI account has been blocked due to pending KYC. Update immediately at http://192.168.1.10/sbi-kyc to avoid suspension.",
                "sender_id": "+919876543210",
                "user_id": "app_user_123"
            }
        }
    )


class ScanResponse(BaseModel):
    label: str = Field(..., description="'SPAM', 'SUSPICIOUS', or 'SAFE'")
    confidence: float = Field(..., description="Calibrated confidence score between 0.0 and 1.0")
    risk_score: float = Field(..., description="Overall risk score between 0.0 (safe) and 1.0 (malicious)")
    reasons: List[str] = Field(..., description="Explainable human-readable reasons for detection")
    layers_used: List[str] = Field(..., description="List of detection layers triggered")
    latency_ms: float = Field(..., description="End-to-end classification latency in milliseconds")
    layer_breakdown: Optional[Dict[str, Any]] = Field(None, description="Detailed diagnostic breakdown per layer")


class BatchScanRequest(BaseModel):
    messages: List[ScanRequest] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of messages to scan in batch (max 50)"
    )


class BatchScanResponse(BaseModel):
    results: List[ScanResponse] = Field(..., description="Individual scan results")
    total: int = Field(..., description="Total messages processed")
    spam_count: int = Field(..., description="Number of SPAM messages")
    suspicious_count: int = Field(..., description="Number of SUSPICIOUS messages")
    safe_count: int = Field(..., description="Number of SAFE messages")
    total_latency_ms: float = Field(..., description="Total batch processing latency in ms")


class FeedbackRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="The scanned message text")
    predicted_label: str = Field(..., description="Label predicted by Spam Shield")
    user_correction: str = Field(
        ...,
        pattern="^(SPAM|SUSPICIOUS|SAFE)$",
        description="User's corrected label: SPAM, SUSPICIOUS, or SAFE"
    )
    comments: Optional[str] = Field("", max_length=500, description="Optional details or context")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Your electricity will be disconnected tonight at 9:30 PM. Call officer 9876543210 immediately.",
                "predicted_label": "SAFE",
                "user_correction": "SPAM",
                "comments": "This is a widespread electricity bill disconnection scam."
            }
        }
    )


class FeedbackResponse(BaseModel):
    status: str = Field("success", description="Status string")
    message: str = Field(..., description="Result message")
    feedback_id: str = Field(..., description="Feedback UUID")


class StatsResponse(BaseModel):
    total_scans: int
    spam_detected: int
    suspicious_flagged: int
    safe_verified: int
    feedback_count: int
    avg_latency_ms: float
    storage: str
    recent_scans: List[Dict[str, Any]]
