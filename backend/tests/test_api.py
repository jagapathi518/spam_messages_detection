"""Comprehensive FastAPI Backend Test Suite."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint metadata."""
    response = client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "documentation" in data
    assert "api_v1" in data


def test_root_html_serves_web_app():
    """Verify root endpoint serves interactive HTML web application to browsers."""
    response = client.get("/", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert "Spam Shield" in response.text
    assert "Live Scanner" in response.text



def test_health_endpoint():
    """Verify system health check and model loading."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ml_engine_loaded"] is True
    assert data["uptime_seconds"] >= 0


def test_metrics_endpoint():
    """Verify performance metrics telemetry."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "ram_usage_mb" in data
    assert data["ram_usage_mb"] > 0
    assert "total_scans_processed" in data


def test_scan_safe_transaction():
    """Verify legitimate bank debit alert is classified as SAFE."""
    payload = {
        "text": "Dear SBI Customer, INR 5,000.00 debited from A/c XX1234 on 15-Oct-26. Avail Bal: INR 42,350.00. Call 1800112211 if not you.",
        "sender_id": "VM-SBINB"
    }
    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "SAFE"
    assert data["risk_score"] < 0.25
    assert data["confidence"] >= 0.80
    assert len(data["layers_used"]) > 0


def test_scan_safe_otp():
    """Verify transactional OTP message is classified as SAFE."""
    payload = {
        "text": "Your Swiggy verification code is 492810. Valid for 10 minutes. Do not share this OTP with anyone.",
        "sender_id": "AX-SWIGGY"
    }
    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "SAFE"
    assert data["risk_score"] < 0.20


def test_scan_phishing_spam():
    """Verify credential harvesting and APK download scam is flagged as SPAM."""
    payload = {
        "text": "URGENT: Your SBI account has been suspended due to incomplete PAN KYC. Download and verify at http://192.168.1.100/sbi-verify.apk immediately.",
        "sender_id": "+919876543210"
    }
    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "SPAM"
    assert data["risk_score"] >= 0.70
    assert any("apk" in r.lower() or "ip address" in r.lower() or "kyc" in r.lower() for r in data["reasons"])


def test_scan_upi_lottery_fraud():
    """Verify lottery & advance fee fraud is flagged as SPAM."""
    payload = {
        "text": "Congratulations! You won Rs 50,000 cash bonus in lucky draw. Pay 499 processing fee via UPI to claim prize: upi://pay?pa=fraud@upi",
        "sender_id": "+918888888888"
    }
    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "SPAM"
    assert data["risk_score"] >= 0.65


def test_scan_empty_message():
    """Verify empty message handling."""
    payload = {"text": "   "}
    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "SAFE"
    assert data["risk_score"] == 0.0


def test_batch_scan_endpoint():
    """Verify batch scanning up to multiple messages."""
    payload = {
        "messages": [
            {
                "text": "Your Amazon order #402-9871 has been delivered. Thank you for shopping with us.",
                "sender_id": "AMAZON"
            },
            {
                "text": "Dear customer, your electricity connection will be cut off tonight at 9:30 PM due to unpaid bill. Call 9876543210 immediately.",
                "sender_id": "+919876543210"
            },
            {
                "text": "Hey bro, are we still meeting for lunch tomorrow at 1 PM?",
                "sender_id": ""
            }
        ]
    }
    response = client.post("/api/v1/scan/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["results"]) == 3
    assert data["safe_count"] >= 2
    assert data["spam_count"] >= 1
    assert data["total_latency_ms"] > 0


def test_batch_scan_size_limit():
    """Verify batch limit enforcement (> 50 returns 422 or 400)."""
    payload = {
        "messages": [{"text": f"Test message {i}"} for i in range(55)]
    }
    response = client.post("/api/v1/scan/batch", json=payload)
    assert response.status_code in [400, 422]


def test_feedback_submission():
    """Verify recording user feedback / corrections."""
    payload = {
        "text": "Work from home part-time and earn Rs 30,000 per day. Contact on Telegram @scamjob",
        "predicted_label": "SAFE",
        "user_correction": "SPAM",
        "comments": "Flagged as job scam."
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "feedback_id" in data


def test_feedback_invalid_label_validation():
    """Verify validation on user_correction enum values."""
    payload = {
        "text": "Some text message",
        "predicted_label": "SAFE",
        "user_correction": "NOT_A_VALID_LABEL"
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 422


def test_stats_endpoint():
    """Verify stats dashboard endpoint returns valid telemetry."""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "spam_detected" in data
    assert "safe_verified" in data
    assert "avg_latency_ms" in data
    assert "recent_scans" in data
    assert isinstance(data["recent_scans"], list)
