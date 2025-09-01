"""
DocumentLens FastAPI Service
Multi-Modal Document Analysis Microservice
"""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routes import academic_analysis, future_endpoints, health, text_analysis
from app.core.config import settings

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="DocumentLens API",
    description="Australian Document Analysis Microservice - Transform any content into actionable insights",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers - Clean Australian microservice URLs
app.include_router(health.router, tags=["health"])
app.include_router(text_analysis.router, tags=["text-analysis"])
app.include_router(academic_analysis.router, tags=["academic-analysis"])
app.include_router(future_endpoints.router, tags=["file-processing"])

@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint"""
    return {
        "service": "DocumentLens",
        "description": "Multi-Modal Document Analysis Microservice",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "available": {
                "health": "/health",
                "text_analysis": "/text",
                "academic_analysis": "/academic",
                "file_processing": "/files"
            },
            "description": {
                "text_analysis": "Analyse raw text (JSON input)",
                "academic_analysis": "Academic analysis of raw text (JSON input)",
                "file_processing": "Upload and analyse files (form data)"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
