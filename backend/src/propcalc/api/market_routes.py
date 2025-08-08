"""
Market Overview API Routes
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..domain.security.oauth2 import User, get_current_user
from ..infrastructure.database.postgres_db import get_db_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["market"])

@router.get("/market/overview")
async def get_market_overview() -> dict[str, Any]:
    """Get real market overview data from database"""
    try:
        db_pool = get_db_pool()

        async with db_pool.acquire() as conn:
            # Get total transactions
            total_transactions = await conn.fetchval(
                "SELECT COUNT(*) FROM dld_transactions"
            )

            # Get average price
            avg_price = await conn.fetchval(
                "SELECT AVG(price_aed) FROM dld_transactions WHERE price_aed > 0"
            )

            # Get average Vantage Score (placeholder - would be calculated)
            avg_vantage_score = 78.5  # This would be calculated from real Vantage Score data

            # Get top locations by transaction count
            top_locations = await conn.fetch(
                """
                SELECT
                    location,
                    COUNT(*) as transactions,
                    AVG(price_aed) as avg_price
                FROM dld_transactions
                WHERE location IS NOT NULL
                GROUP BY location
                ORDER BY COUNT(*) DESC
                LIMIT 5
                """
            )

            # Get property types distribution
            property_types = await conn.fetch(
                """
                SELECT
                    property_type,
                    COUNT(*) as count,
                    AVG(price_aed) as avg_price
                FROM dld_transactions
                WHERE property_type IS NOT NULL
                GROUP BY property_type
                ORDER BY COUNT(*) DESC
                """
            )

            # Calculate market trends (last 30 days vs previous 30 days)
            trends = await conn.fetchrow(
                """
                WITH current_period AS (
                    SELECT
                        AVG(price_aed) as current_avg_price,
                        COUNT(*) as current_transactions
                    FROM dld_transactions
                    WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                ),
                previous_period AS (
                    SELECT
                        AVG(price_aed) as previous_avg_price,
                        COUNT(*) as previous_transactions
                    FROM dld_transactions
                    WHERE transaction_date >= CURRENT_DATE - INTERVAL '60 days'
                    AND transaction_date < CURRENT_DATE - INTERVAL '30 days'
                )
                SELECT
                    CASE
                        WHEN previous_avg_price > 0
                        THEN ((current_avg_price - previous_avg_price) / previous_avg_price) * 100
                        ELSE 0
                    END as price_change_30d,
                    CASE
                        WHEN previous_transactions > 0
                        THEN ((current_transactions - previous_transactions) / previous_transactions) * 100
                        ELSE 0
                    END as volume_change_30d
                FROM current_period, previous_period
                """
            )

            # Determine market sentiment based on trends
            price_change = trends['price_change_30d'] if trends else 0
            volume_change = trends['volume_change_30d'] if trends else 0

            if price_change > 2 and volume_change > 5:
                market_sentiment = "bullish"
            elif price_change > 0 and volume_change > 0:
                market_sentiment = "positive"
            elif price_change < -2 or volume_change < -5:
                market_sentiment = "bearish"
            else:
                market_sentiment = "neutral"

            # Format top locations
            formatted_locations = []
            for loc in top_locations:
                formatted_locations.append({
                    "name": loc['location'],
                    "transactions": loc['transactions'],
                    "avg_price": round(loc['avg_price'] or 0, 0)
                })

            # Format property types
            formatted_property_types = []
            for prop_type in property_types:
                formatted_property_types.append({
                    "type": prop_type['property_type'],
                    "count": prop_type['count'],
                    "avg_price": round(prop_type['avg_price'] or 0, 0)
                })

            market_overview = {
                "total_properties": total_transactions or 0,
                "total_transactions": total_transactions or 0,
                "average_price": round(avg_price or 0, 0),
                "average_vantage_score": avg_vantage_score,
                "market_sentiment": market_sentiment,
                "top_locations": formatted_locations,
                "property_types": formatted_property_types,
                "market_trends": {
                    "price_change_30d": round(price_change, 1),
                    "volume_change_30d": round(volume_change, 1),
                    "vantage_score_change_30d": 1.8  # Placeholder - would be calculated
                },
                "last_updated": datetime.now().isoformat()
            }

            return market_overview

    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market overview")

@router.get("/market/trends")
async def get_market_trends(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Get real market trends data from database"""
    try:
        db_pool = get_db_pool()

        async with db_pool.acquire() as conn:
            # Get monthly trends for the last 6 months
            monthly_trends = await conn.fetch(
                """
                SELECT
                    DATE_TRUNC('month', transaction_date) as month,
                    AVG(price_aed) as avg_price,
                    COUNT(*) as transaction_count
                FROM dld_transactions
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY month
                ORDER BY month DESC
                LIMIT 6
                """
            )

            # Format data for charts
            labels = []
            price_data = []
            volume_data = []

            for trend in reversed(monthly_trends):
                month_name = trend['month'].strftime('%b')
                labels.append(month_name)
                price_data.append(round(trend['avg_price'] or 0, 0))
                volume_data.append(trend['transaction_count'])

            # Calculate Vantage Score trends (placeholder)
            vantage_score_data = [75.2, 76.1, 77.3, 78.0, 78.5, 79.2]

            trends = {
                "price_trends": {
                    "labels": labels,
                    "data": price_data
                },
                "volume_trends": {
                    "labels": labels,
                    "data": volume_data
                },
                "vantage_score_trends": {
                    "labels": labels,
                    "data": vantage_score_data
                }
            }

            return trends

    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market trends")

@router.get("/market/locations")
async def get_market_locations(current_user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    """Get real market locations data from database"""
    try:
        db_pool = get_db_pool()

        async with db_pool.acquire() as conn:
            # Get location statistics
            locations = await conn.fetch(
                """
                SELECT
                    location,
                    COUNT(*) as total_properties,
                    AVG(price_aed) as avg_price,
                    AVG(area_sqft) as avg_area,
                    COUNT(*) as transaction_volume
                FROM dld_transactions
                WHERE location IS NOT NULL
                GROUP BY location
                ORDER BY COUNT(*) DESC
                LIMIT 10
                """
            )

            # Format locations data
            formatted_locations = []
            for loc in locations:
                avg_price = loc['avg_price'] or 0
                avg_area = loc['avg_area'] or 1000
                price_per_sqft = avg_price / avg_area if avg_area > 0 else 0

                formatted_locations.append({
                    "name": loc['location'],
                    "total_properties": loc['total_properties'],
                    "avg_price": round(avg_price, 0),
                    "avg_vantage_score": 80.0,  # Placeholder - would be calculated
                    "transaction_volume": loc['transaction_volume'],
                    "price_per_sqft": round(price_per_sqft, 0)
                })

            return formatted_locations

    except Exception as e:
        logger.error(f"Error getting market locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market locations")
