"""
PropCalc Backend - Advanced Real Estate Analytics Platform

A production-ready FastAPI application providing AI-powered real estate analytics,
market insights, and investment decision support for the Dubai real estate market.
"""

__version__ = "2.0.0"
__author__ = "PropCalc Team"
__email__ = "team@propcalc.ai"
__description__ = "Advanced Real Estate Analytics Platform with AI-powered insights"


def get_settings():
    """Lazily import and return application settings.

    This avoids importing optional dependencies (e.g. pydantic) during
    module import, which is useful for lightweight test environments.
    """
    from .config.settings import get_settings as _get_settings

    return _get_settings()


__all__ = ["get_settings"]
