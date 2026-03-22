from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.models import RequestStats, AIDecision, HealthResponse
from app.decision_engine import decision_engine
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="AI-powered decision service for API gateway request analysis",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (allow gateway to call this service)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify gateway URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """
    Root endpoint - service information
    """
    return {
        "service": settings.app_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Used by gateway to verify service availability
    """
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.version,
        timestamp=datetime.now()
    )


@app.post("/predict", response_model=AIDecision)
async def predict(request_stats: RequestStats):
    """
    Main prediction endpoint
    Receives request statistics from gateway and returns AI decision

    Request Body: RequestStats
    Response: AIDecision (ALLOW/BLOCK + confidence + reason)
    """

    try:
        logger.info(
            f"🔍 Analyzing request: IP={request_stats.ip_address}, "
            f"Count={request_stats.request_count}, "
            f"Endpoint={request_stats.endpoint}"
        )

        # Perform AI analysis
        decision = decision_engine.analyze(request_stats)

        # Log decision
        if decision.action == "BLOCK":
            logger.warning(
                f"🚫 BLOCK decision: IP={request_stats.ip_address}, "
                f"Reason={decision.reason}, "
                f"Confidence={decision.confidence:.2f}"
            )
        else:
            logger.info(
                f"✅ ALLOW decision: IP={request_stats.ip_address}, "
                f"Confidence={decision.confidence:.2f}"
            )

        return decision

    except Exception as e:
        logger.error(f"❌ Error analyzing request: {str(e)}", exc_info=True)

        # Return safe default (ALLOW) on error
        # In production, you might want to BLOCK on error for safety
        return AIDecision(
            action="ALLOW",
            confidence=0.5,
            reason=f"Analysis error - defaulting to ALLOW: {str(e)}",
            threat_level="UNKNOWN"
        )


@app.get("/stats")
async def get_stats():
    """
    Get service statistics
    """
    return {
        "service": settings.app_name,
        "version": settings.version,
        "configuration": {
            "suspicious_request_count": settings.suspicious_request_count,
            "high_frequency_threshold": settings.high_frequency_threshold,
            "very_high_frequency_threshold": settings.very_high_frequency_threshold,
            "block_confidence_threshold": settings.block_confidence_threshold
        },
        "timestamp": datetime.now()
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting {settings.app_name} v{settings.version}")
    logger.info(f"📍 Server: http://{settings.host}:{settings.port}")
    logger.info(f"📚 Docs: http://{settings.host}:{settings.port}/docs")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )