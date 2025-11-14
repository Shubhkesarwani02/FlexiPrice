from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import connect_db, disconnect_db
from app.api.v1.api import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    await connect_db()
    yield
    # Shutdown
    await disconnect_db()


app = FastAPI(
    title="FlexiPrice API",
    description="Expiry-Based Dynamic Pricing System",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "flexiprice-api",
        "version": settings.VERSION
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FlexiPrice API - Expiry-Based Dynamic Pricing System",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }
