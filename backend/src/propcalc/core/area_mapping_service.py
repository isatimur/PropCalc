#!/usr/bin/env python3
"""
Area Mapping Service for PropCalc
Handles mapping between DLD area names and internet-friendly names
Provides region analytics and insights
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json

from ..infrastructure.database.postgres_db import get_db_instance

logger = logging.getLogger(__name__)

class AreaMappingService:
    """Service for managing area mappings and region analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_area_mapping(self, area_name: str) -> Optional[Dict[str, Any]]:
        """Get area mapping by DLD area name or internet name"""
        try:
            db_instance = await get_db_instance()
            conn = await db_instance.get_connection()
            try:
                # Try to find by DLD area name first
                result = await conn.fetchrow(
                    """
                        SELECT * FROM area_mapping 
                        WHERE LOWER(dld_area_name) = LOWER($1)
                        OR LOWER(internet_name) = LOWER($1)
                        OR LOWER(normalized_name) = LOWER($1)
                    """,
                    area_name
                )
                
                if result:
                    return dict(result)
                return None
                
            finally:
                await db_instance.release_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Error getting area mapping: {e}")
            return None
    
    async def get_popular_areas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular areas by transaction volume"""
        try:
            db_instance = await get_db_instance()
            conn = await db_instance.get_connection()
            try:
                result = await conn.fetch(
                    """
                        SELECT 
                            am.id,
                            am.dld_area_name,
                            am.internet_name,
                            am.normalized_name,
                            am.region_category,
                            am.municipality,
                            am.popularity_score,
                            am.avg_price_aed,
                            am.min_price_aed,
                            am.max_price_aed,
                            am.price_trend,
                            am.transaction_volume,
                            COALESCE(aa.total_transactions, 0) as total_transactions,
                            COALESCE(aa.avg_price_aed, 0) as avg_price_aed,
                            COALESCE(aa.price_per_sqft_avg, 0) as price_per_sqft_avg
                        FROM area_mapping am
                        LEFT JOIN area_analytics aa ON am.id = aa.area_mapping_id AND aa.analysis_date = CURRENT_DATE
                        ORDER BY am.popularity_score DESC, am.transaction_volume DESC
                        LIMIT $1
                    """,
                    limit
                )
                
                return [dict(row) for row in result]
                
            finally:
                await db_instance.release_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Error getting popular areas: {e}")
            return []
    
    async def get_region_analytics(self, region_name: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific region"""
        try:
            # Get area mapping
            area_mapping = await self.get_area_mapping(region_name)
            if not area_mapping:
                return {"error": "Region not found"}
            
            db_instance = await get_db_instance()
            conn = await db_instance.get_connection()
            try:
                # Get transaction data for the period
                start_date = datetime.now() - timedelta(days=days)
                
                result = await conn.fetchrow(
                    """
                        SELECT 
                            COUNT(*) as total_transactions,
                            SUM(price_aed) as total_volume,
                            AVG(price_aed) as avg_price,
                            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_aed) as median_price,
                            MIN(price_aed) as min_price,
                            MAX(price_aed) as max_price,
                            AVG(price_per_sqft) as avg_price_per_sqft,
                            COUNT(DISTINCT property_type) as property_types_count,
                            COUNT(DISTINCT developer_name) as developers_count
                        FROM dld_transactions 
                        WHERE LOWER(location) = LOWER($1)
                        AND transaction_date >= $2
                    """,
                    area_mapping.get("dld_area_name", region_name),
                    start_date
                )
                
                if not result:
                    return {"error": "No data found for region"}
                
                # Get price trend
                price_trend = await self._calculate_price_trend(conn, region_name, days)
                
                # Get property type breakdown
                property_types = await self._get_property_type_breakdown(conn, region_name, days)
                
                # Get developer breakdown
                developers = await self._get_developer_breakdown(conn, region_name, days)
                
                return {
                    "region_info": area_mapping,
                    "analytics": {
                        "period_days": days,
                        "total_transactions": result['total_transactions'],
                        "total_volume_aed": float(result['total_volume']) if result['total_volume'] else 0,
                        "avg_price_aed": float(result['avg_price']) if result['avg_price'] else 0,
                        "median_price_aed": float(result['median_price']) if result['median_price'] else 0,
                        "min_price_aed": float(result['min_price']) if result['min_price'] else 0,
                        "max_price_aed": float(result['max_price']) if result['max_price'] else 0,
                        "avg_price_per_sqft": float(result['avg_price_per_sqft']) if result['avg_price_per_sqft'] else 0,
                        "property_types_count": result['property_types_count'],
                        "developers_count": result['developers_count'],
                        "price_trend": price_trend,
                        "property_types": property_types,
                        "top_developers": developers
                    }
                }
                
            finally:
                await db_instance.release_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Error getting region analytics: {e}")
            return {"error": str(e)}
    
    async def _calculate_price_trend(self, conn, region_name: str, days: int) -> str:
        """Calculate price trend for a region"""
        try:
            # Get price data for last 3 periods
            periods = [days, days//2, days//4]
            prices = []
            
            for period in periods:
                start_date = datetime.now() - timedelta(days=period)
                result = await conn.fetchrow(
                    """
                        SELECT AVG(price_aed) as avg_price
                        FROM dld_transactions 
                        WHERE LOWER(location) = LOWER($1)
                        AND transaction_date >= $2
                    """,
                    region_name, start_date
                )
                
                if result and result['avg_price']:
                    prices.append(float(result['avg_price']))
            
            if len(prices) >= 2:
                if prices[0] > prices[1] * 1.05:
                    return "rising"
                elif prices[0] < prices[1] * 0.95:
                    return "declining"
                else:
                    return "stable"
            
            return "stable"
            
        except Exception as e:
            self.logger.error(f"Error calculating price trend: {e}")
            return "stable"
    
    async def _get_property_type_breakdown(self, conn, region_name: str, days: int) -> List[Dict[str, Any]]:
        """Get property type breakdown for a region"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            result = await conn.fetch(
                """
                    SELECT 
                        property_type,
                        COUNT(*) as count,
                        AVG(price_aed) as avg_price
                    FROM dld_transactions 
                    WHERE LOWER(location) = LOWER($1)
                    AND transaction_date >= $2
                    GROUP BY property_type
                    ORDER BY count DESC
                    LIMIT 5
                """,
                region_name, start_date
            )
            
            return [
                {
                    "type": row['property_type'],
                    "count": row['count'],
                    "avg_price": float(row['avg_price']) if row['avg_price'] else 0
                }
                for row in result
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting property type breakdown: {e}")
            return []
    
    async def _get_developer_breakdown(self, conn, region_name: str, days: int) -> List[Dict[str, Any]]:
        """Get developer breakdown for a region"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            result = await conn.fetch(
                """
                    SELECT 
                        developer_name,
                        COUNT(*) as count,
                        AVG(price_aed) as avg_price
                    FROM dld_transactions 
                    WHERE LOWER(location) = LOWER($1)
                    AND transaction_date >= $2
                    AND developer_name IS NOT NULL
                    GROUP BY developer_name
                    ORDER BY count DESC
                    LIMIT 5
                """,
                region_name, start_date
            )
            
            return [
                {
                    "name": row['developer_name'],
                    "count": row['count'],
                    "avg_price": float(row['avg_price']) if row['avg_price'] else 0
                }
                for row in result
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting developer breakdown: {e}")
            return []
    
    async def search_areas(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search areas by name (DLD, internet, or normalized)"""
        try:
            db_instance = await get_db_instance()
            conn = await db_instance.get_connection()
            try:
                result = await conn.fetch(
                    """
                        SELECT * FROM area_mapping 
                        WHERE 
                            LOWER(dld_area_name) LIKE LOWER($1)
                            OR LOWER(internet_name) LIKE LOWER($1)
                            OR LOWER(normalized_name) LIKE LOWER($1)
                        ORDER BY popularity_score DESC
                        LIMIT $2
                    """,
                    f"%{query}%", limit
                )
                
                return [dict(row) for row in result]
                
            finally:
                await db_instance.release_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Error searching areas: {e}")
            return []
    
    async def get_region_comparison(self, regions: List[str]) -> Dict[str, Any]:
        """Compare multiple regions side by side"""
        try:
            comparison_data = {}
            
            for region in regions:
                analytics = await self.get_region_analytics(region)
                if "error" not in analytics:
                    comparison_data[region] = analytics
            
            return {
                "regions": comparison_data,
                "comparison_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting region comparison: {e}")
            return {"error": str(e)}
    
    async def update_area_popularity(self, area_id: int) -> bool:
        """Update popularity score for an area based on transaction volume"""
        try:
            db_instance = await get_db_instance()
            conn = await db_instance.get_connection()
            try:
                # Get transaction count for the area
                result = await conn.fetchrow(
                    """
                        SELECT COUNT(*) as transaction_count
                        FROM dld_transactions dt
                        JOIN area_mapping am ON LOWER(dt.location) = LOWER(am.dld_area_name)
                        WHERE am.id = $1
                    """,
                    area_id
                )
                
                if result:
                    transaction_count = result['transaction_count']
                    
                    # Calculate popularity score (0-100)
                    if transaction_count > 1000:
                        popularity_score = 100
                    elif transaction_count > 500:
                        popularity_score = 80
                    elif transaction_count > 100:
                        popularity_score = 60
                    elif transaction_count > 50:
                        popularity_score = 40
                    elif transaction_count > 10:
                        popularity_score = 20
                    else:
                        popularity_score = 10
                    
                    # Update popularity score
                    await conn.execute(
                        """
                            UPDATE area_mapping 
                            SET popularity_score = $1, transaction_volume = $2
                            WHERE id = $3
                        """,
                        popularity_score, transaction_count, area_id
                    )
                    
                    return True
                
                return False
                
            finally:
                await db_instance.release_connection(conn)
                
        except Exception as e:
            self.logger.error(f"Error updating area popularity: {e}")
            return False
