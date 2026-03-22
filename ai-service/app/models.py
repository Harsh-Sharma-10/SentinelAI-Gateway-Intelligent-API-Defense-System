from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RequestStats(BaseModel):
    """
    Request statistics from gateway
    Matches the RequestStats DTO from gateway-service
    """

    # Client Information
    ip_address: str = Field(..., alias="ipAddress", description="Client IP address")
    user_agent: str = Field(..., alias="userAgent", description="User agent string")

    # Request Details
    method: str = Field(..., description="HTTP method")
    endpoint: str = Field(..., description="API endpoint")
    request_path: str = Field(..., alias="requestPath", description="Full request path")

    # Frequency & Timing
    request_count: int = Field(..., alias="requestCount", description="Requests in last minute")
    timestamp: datetime = Field(..., description="Request timestamp")
    response_time_ms: Optional[int] = Field(None, alias="responseTimeMs", description="Response time in ms")

    # Response Information
    status_code: Optional[int] = Field(None, alias="statusCode", description="HTTP status code")

    # AI Decision (optional - may be set by gateway)
    ai_decision: Optional[str] = Field(None, alias="aiDecision", description="AI decision")
    ai_confidence: Optional[float] = Field(None, alias="aiConfidence", description="Confidence score")
    ai_reason: Optional[str] = Field(None, alias="aiReason", description="Decision reason")

    class Config:
        populate_by_name = True  # Allow both camelCase and snake_case


class AIDecision(BaseModel):
    """
    AI decision response sent back to gateway
    """

    action: str = Field(..., description="ALLOW or BLOCK")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reason: str = Field(..., description="Human-readable reason")
    threat_level: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")

    # Additional metadata
    analysis_details: Optional[dict] = Field(None, description="Detailed analysis")
    recommended_action: Optional[str] = Field(None, description="Recommended mitigation")


class HealthResponse(BaseModel):
    """
    Health check response
    """
    status: str = Field(default="healthy")
    service: str = Field(default="ai-decision-service")
    version: str
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "ai-decision-service",
                "version": "1.0.0",
                "timestamp": "2025-03-21T10:30:00"
            }
        }