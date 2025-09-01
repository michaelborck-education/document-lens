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

from app.api.routes import academic_analysis, analysis, future_endpoints, health, text_analysis
from app.core.config import settings

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="DocumentLens API",
    description="Multi-Modal Document Analysis Microservice - Transform any content into actionable insights",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
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

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])

# New modular endpoints
app.include_router(text_analysis.router, prefix="/api/analyze", tags=["text-analysis"])
app.include_router(academic_analysis.router, prefix="/api/analyze", tags=["academic-analysis"])
app.include_router(future_endpoints.router, prefix="/api/analyze", tags=["future-features"])

@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint"""
    return {
        "service": "DocumentLens",
        "description": "Multi-Modal Document Analysis Microservice",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "current": ["/api/health", "/api/analyze"],
            "planned": ["/api/analyze/text", "/api/analyze/academic", "/api/analyze/files"]
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
