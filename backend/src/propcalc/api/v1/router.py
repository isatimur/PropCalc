"""
API v1 Router - All PropCalc API endpoints
"""

from fastapi import APIRouter

from .endpoints import dld, kml, analytics, health

router = APIRouter()

# Include all endpoint routers
router.include_router(dld.router, prefix="/dld", tags=["DLD"])
router.include_router(kml.router, prefix="/kml", tags=["KML"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(health.router, prefix="/health", tags=["Health"]) 