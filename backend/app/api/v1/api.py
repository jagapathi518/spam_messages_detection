"""V1 API Router Aggregator."""
from fastapi import APIRouter
from backend.app.api.v1.endpoints import scan, feedback, stats, health

api_router = APIRouter()

api_router.include_router(scan.router, tags=["Detection"])
api_router.include_router(feedback.router, tags=["Feedback"])
api_router.include_router(stats.router, tags=["Stats"])
