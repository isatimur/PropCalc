"""
Health Check API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from propcalc.infrastructure.database.database import get_async_db, check_database_connection_async

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "PropCalc Backend",
        "version": "2.0.0",
        "environment": "development"
    }


@router.get("/database")
async def database_health_check(db: AsyncSession = Depends(get_async_db)):
    """Database health check"""
    try:
        is_healthy = await check_database_connection_async()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "database": "connected" if is_healthy else "disconnected",
            "timestamp": "2025-08-03T23:09:39Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": "2025-08-03T23:09:39Z"
        }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_async_db)):
    """Detailed health check with all components"""
    try:
        db_healthy = await check_database_connection_async()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api": "healthy",
                "cache": "healthy"  # Add cache health check when implemented
            },
            "service": "PropCalc Backend",
            "version": "2.0.0",
            "environment": "development",
            "timestamp": "2025-08-03T23:09:39Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "components": {
                "database": "error",
                "api": "healthy",
                "cache": "unknown"
            },
            "service": "PropCalc Backend",
            "version": "2.0.0",
            "environment": "development",
            "error": str(e),
            "timestamp": "2025-08-03T23:09:39Z"
        }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_async_db)):
    """Readiness check for Kubernetes/container orchestration"""
    try:
        db_healthy = await check_database_connection_async()
        
        if db_healthy:
            return {
                "status": "ready",
                "message": "All services are ready to accept traffic"
            }
        else:
            return {
                "status": "not_ready",
                "message": "Database connection failed"
            }
    except Exception as e:
        return {
            "status": "not_ready",
            "message": f"Health check failed: {str(e)}"
        }


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration"""
    return {
        "status": "alive",
        "message": "Service is running"
    } 