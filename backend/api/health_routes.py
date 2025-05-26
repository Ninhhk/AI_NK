"""
Health check API routes for monitoring application status.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from utils.health_check import get_health_status, get_last_health_check

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dictionary with basic health status
    """
    try:
        return {
            "status": "healthy",
            "message": "AI NVCB API is running",
            "timestamp": "2025-05-26T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint that checks all components.
    
    Returns:
        Dictionary with detailed health status
    """
    try:
        health_status = await get_health_status()
        
        # Set HTTP status based on health
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check error: {str(e)}"
        )


@router.get("/health/last")
async def last_health_check() -> Dict[str, Any]:
    """
    Get the last cached health check results.
    
    Returns:
        Dictionary with last health check results
    """
    try:
        last_check = get_last_health_check()
        
        if last_check is None:
            return {
                "status": "no_data",
                "message": "No health check data available",
                "timestamp": "2025-05-26T00:00:00Z"
            }
        
        return last_check
        
    except Exception as e:
        logger.error(f"Last health check retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check error: {str(e)}"
        )


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes/Docker deployments.
    
    Returns:
        Dictionary indicating if the service is ready to serve traffic
    """
    try:
        # Check critical components
        health_status = await get_health_status()
        
        # Consider service ready if database is healthy
        db_status = health_status.get("checks", {}).get("database", {})
        
        if db_status.get("status") == "healthy":
            return {
                "status": "ready",
                "message": "Service is ready to serve traffic",
                "timestamp": health_status.get("timestamp")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "not_ready",
                    "message": "Service is not ready to serve traffic",
                    "reason": "Database not healthy"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check error: {str(e)}"
        )


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint for Kubernetes/Docker deployments.
    
    Returns:
        Dictionary indicating if the service is alive
    """
    try:
        # Simple liveness check - just return that we're alive
        return {
            "status": "alive",
            "message": "Service is alive",
            "timestamp": "2025-05-26T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Liveness check error: {str(e)}"
        )
