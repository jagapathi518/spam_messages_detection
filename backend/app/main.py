"""Spam Shield FastAPI Main Application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1.api import api_router
from backend.app.api.v1.endpoints import health
from backend.app.api.v1.endpoints.scan import get_detector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("spam_shield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager: pre-warms ML and Rule models on startup."""
    logger.info("Initializing Spam Shield engines...")
    detector = get_detector()
    # Warm up inference with a test scan
    warmup = detector.scan("Test warmup message")
    logger.info(f"Engines warmed up in background (warmup label: {warmup['label']}).")
    yield
    logger.info("Shutting down Spam Shield API.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "High-performance, 3-layer mobile short text message scam detection API. "
        "Protects users against SMS phishing, bank scams, UPI fraud, fake delivery links, "
        "job scams, and extortion messages with sub-5ms ML inference and Groq LLM second opinions."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from pathlib import Path
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

# Include Routers
app.include_router(health.router, tags=["Health & Telemetry"])
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Static Web App
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", tags=["Web Application"])
def root(request: Request):
    """Serves the interactive Spam Shield web application or JSON metadata."""
    accept = request.headers.get("accept", "")
    index_file = STATIC_DIR / "index.html"
    if index_file.exists() and "application/json" not in accept:
        return FileResponse(index_file)
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "api_v1": settings.API_V1_STR
    }


@app.get("/api", tags=["API Root"])
def api_info():
    """Returns API service discovery metadata."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "api_v1": settings.API_V1_STR
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

