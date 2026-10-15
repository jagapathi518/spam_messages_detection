"""User Feedback API Endpoint."""
from fastapi import APIRouter
from backend.app.schemas.scan import FeedbackRequest, FeedbackResponse
from backend.app.db.supabase_client import db_service

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse, summary="Submit user feedback or correction")
def submit_feedback(payload: FeedbackRequest):
    """
    Submits user correction (e.g. false alarm report or missed spam).
    These feedback records feed into `ml/src/retrain.py` for continuous learning.
    """
    saved = db_service.save_feedback(
        text=payload.text,
        predicted_label=payload.predicted_label,
        user_correction=payload.user_correction,
        comments=payload.comments or ""
    )
    return FeedbackResponse(
        status="success",
        message="Thank you for your feedback! Your correction helps improve Spam Shield's detection accuracy.",
        feedback_id=saved.get("id", "recorded")
    )
