"""Stats API Endpoint."""
from fastapi import APIRouter
from backend.app.schemas.scan import StatsResponse
from backend.app.db.supabase_client import db_service

router = APIRouter()

@router.get("/stats", response_model=StatsResponse, summary="Get detection metrics and scan statistics")
def get_stats():
    """
    Returns aggregated detection statistics: total scans, spam counts, safe counts,
    average latency, and recent scan history.
    """
    data = db_service.get_stats()
    return StatsResponse(**data)
