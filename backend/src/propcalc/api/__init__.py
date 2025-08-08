"""
API routes module
"""

from .comprehensive_dld_routes import router as comprehensive_dld_router
from .dld_routes import router as dld_router
from .pipeline_routes import router as pipeline_router
from .real_dld_routes import router as real_dld_router
from .realtime_dld_routes import router as realtime_dld_router

__all__ = [
    'dld_router',
    'real_dld_router',
    'realtime_dld_router',
    'pipeline_router',
    'comprehensive_dld_router'
]
