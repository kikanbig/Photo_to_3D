"""
Photo to 3D - Main FastAPI application
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
# Optional imports for Railway
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    # Mock structlog
    class MockLogger:
        def info(self, msg, **kwargs): print(f"INFO: {msg}")
        def error(self, msg, **kwargs): print(f"ERROR: {msg}")
        def warning(self, msg, **kwargs): print(f"WARNING: {msg}")
    
    class MockStructlog:
        @staticmethod
        def configure(**kwargs): pass
        @staticmethod 
        def get_logger(name): return MockLogger()
    structlog = MockStructlog()

from app.api.v1.api import api_router
from app.core.config_v1 import settings
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.services.trellis_service import TrellisService

# Configure structured logging if available
if STRUCTLOG_AVAILABLE:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger(__name__)

# Global services
trellis_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global trellis_service
    
    # Startup
    logger.info("Starting Photo to 3D application - Railway mode")
    
    # Skip database and Redis for Railway deployment
    logger.info("Skipping database and Redis initialization for Railway")
    
    # Initialize TRELLIS service in mock mode
    try:
        trellis_service = TrellisService()
        await trellis_service.initialize()
        app.state.trellis_service = trellis_service
        logger.info("TRELLIS service initialized in mock mode")
    except Exception as e:
        logger.warning("Failed to initialize TRELLIS service, continuing without it", error=str(e))
        # Don't raise - continue without TRELLIS
        trellis_service = None
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Photo to 3D application")
    if trellis_service:
        await trellis_service.cleanup()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered photo to 3D model generation service",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["your-domain.com"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "mode": "railway_demo",
            "trellis_loaded": trellis_service is not None
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy", 
            "error": str(e)
        }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
