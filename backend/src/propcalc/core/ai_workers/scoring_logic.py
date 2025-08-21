"""
Basic Vantage Score calculation logic and compatibility class used by tests.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def calculate_vantage_score(project_data: dict[str, Any]) -> float:
    """Calculate basic Vantage Score based on real data only"""
    try:
        score = 0.0

        price = float(project_data.get('price', 1000000))
        price_score = min(100, max(0, (price / 1000000) * 20))
        score += price_score * 0.3

        location_score = float(project_data.get('location_score', 80))
        score += location_score * 0.25

        developer_score = float(project_data.get('developer_score', 80))
        score += developer_score * 0.20

        area = float(project_data.get('area', 1200))
        area_score = min(100, max(0, (area / 2000) * 50))
        score += area_score * 0.15

        market_trend = float(project_data.get('market_trend', 1))
        trend_score = max(0, min(100, 50 + market_trend * 10))
        score += trend_score * 0.10

        return float(score)
    except Exception as e:
        logger.error(f"Error calculating Vantage Score: {e}")
        raise ValueError(f"Invalid data for Vantage Score calculation: {e}")


class VantageScoringEngine:
    """Compatibility class for tests/test_main.py"""

    def calculate_vantage_score(self, project_data: Dict[str, Any]) -> float:  # noqa: D401
        return calculate_vantage_score(project_data)

    def assess_risk_factors(self, project_data: Dict[str, Any]) -> List[str]:
        score = self.calculate_vantage_score(project_data)
        risks: List[str] = []
        if score < 50:
            risks.append("High market risk")
        if project_data.get("sales_velocity", 0) < 50:
            risks.append("Slow sales velocity")
        return risks or ["Low risk"]

    def generate_recommendations(self, project_data: Dict[str, Any]) -> List[str]:
        score = self.calculate_vantage_score(project_data)
        if score >= 85:
            return ["STRONG BUY"]
        if score >= 70:
            return ["BUY"]
        if score >= 55:
            return ["HOLD"]
        return ["AVOID"]
