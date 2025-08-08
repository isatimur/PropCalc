"""
Basic Vantage Score calculation logic
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

def calculate_vantage_score(project_data: dict[str, Any]) -> float:
    """Calculate basic Vantage Score"""
    try:
        score = 0.0

        # Price factor (30% weight)
        price = float(project_data.get('price', 0))
        if price > 0:
            price_score = min(100, max(0, (price / 1000000) * 20))  # Normalize to 0-100
            score += price_score * 0.3

        # Location factor (25% weight)
        location_score = float(project_data.get('location_score', 50))
        score += location_score * 0.25

        # Developer factor (20% weight)
        developer_score = float(project_data.get('developer_score', 50))
        score += developer_score * 0.20

        # Area factor (15% weight)
        area = float(project_data.get('area', 0))
        if area > 0:
            area_score = min(100, max(0, (area / 2000) * 50))  # Normalize to 0-100
            score += area_score * 0.15

        # Market trend factor (10% weight)
        market_trend = float(project_data.get('market_trend', 0))
        trend_score = max(0, min(100, 50 + market_trend * 10))
        score += trend_score * 0.10

        return float(score)
    except Exception as e:
        logger.error(f"Error calculating Vantage Score: {e}")
        return 50.0  # Default score
