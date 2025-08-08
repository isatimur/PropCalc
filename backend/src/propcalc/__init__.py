"""
PropCalc Backend - Advanced Real Estate Analytics Platform

A production-ready FastAPI application providing AI-powered real estate analytics,
market insights, and investment decision support for the Dubai real estate market.
"""

__version__ = "2.0.0"
__author__ = "PropCalc Team"
__email__ = "team@propcalc.ai"
__description__ = "Advanced Real Estate Analytics Platform with AI-powered insights"

from .config.settings import get_settings

__all__ = ["get_settings"]
