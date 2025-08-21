#!/usr/bin/env python3
"""
Area Mapping API Routes for PropCalc
Provides endpoints for area mapping and region analytics
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from ..domain.security.oauth2 import User, get_current_user
from ..core.area_mapping_service import AreaMappingService
from ..infrastructure.database.models import AreaMapping, AreaAnalytics, RegionOverview

router = APIRouter(prefix="/api/v1/areas", tags=["area-mapping"])

# Initialize services
area_service = AreaMappingService()

@router.get("/mapping/{area_name}")
async def get_area_mapping(
    area_name: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get area mapping by DLD area name or internet name"""
    try:
        mapping = await area_service.get_area_mapping(area_name)
        if not mapping:
            raise HTTPException(status_code=404, detail="Area not found")
        
        return {
            "success": True,
            "data": mapping,
            "timestamp": "2025-08-19T22:50:00"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get area mapping: {str(e)}")

@router.get("/popular")
async def get_popular_areas(
    limit: int = Query(10, ge=1, le=50, description="Number of areas to return")
) -> dict:
    """Get most popular areas by transaction volume and popularity score"""
    try:
        areas = await area_service.get_popular_areas(limit)
        
        return {
            "success": True,
            "data": areas,
            "total": len(areas),
            "timestamp": "2025-08-19T22:50:00"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get popular areas: {str(e)}")

@router.get("/analytics/{region_name}")
async def get_region_analytics(
    region_name: str,
    days: int = Query(30, ge=1, le=365, description="Analysis period in days")
) -> dict:
    """Get comprehensive analytics for a specific region"""
    try:
        analytics = await area_service.get_region_analytics(region_name, days)
        
        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])
        
        return {
            "success": True,
            "data": analytics,
            "timestamp": "2025-08-19T22:50:00"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get region analytics: {str(e)}")

@router.get("/search")
async def search_areas(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return")
) -> dict:
    """Search areas by name (DLD, internet, or normalized)"""
    try:
        areas = await area_service.search_areas(q, limit)
        
        return {
            "success": True,
            "data": areas,
            "query": q,
            "total": len(areas),
            "timestamp": "2025-08-19T22:50:00"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search areas: {str(e)}")

@router.get("/comparison")
async def compare_regions(
    regions: str = Query(..., description="Comma-separated list of region names"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Compare multiple regions side by side"""
    try:
        region_list = [r.strip() for r in regions.split(",") if r.strip()]
        
        if len(region_list) < 2:
            raise HTTPException(status_code=400, detail="At least 2 regions required for comparison")
        
        if len(region_list) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 regions allowed for comparison")
        
        comparison = await area_service.get_region_comparison(region_list)
        
        if "error" in comparison:
            raise HTTPException(status_code=500, detail=comparison["error"])
        
        return {
            "success": True,
            "data": comparison,
            "timestamp": "2025-08-19T22:50:00"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare regions: {str(e)}")

@router.get("/overview")
async def get_areas_overview(
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get overview of all mapped areas with basic analytics"""
    try:
        # Get popular areas as overview
        popular_areas = await area_service.get_popular_areas(20)
        
        # Get total count
        total_areas = len(popular_areas)
        
        # Calculate summary statistics
        total_transactions = sum(area.get("total_transactions", 0) for area in popular_areas)
        avg_popularity = sum(area.get("popularity_score", 0) for area in popular_areas) / total_areas if total_areas > 0 else 0
        
        # Group by region category
        categories = {}
        for area in popular_areas:
            category = area.get("region_category", "Unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(area)
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_areas": total_areas,
                    "total_transactions": total_transactions,
                    "average_popularity_score": round(avg_popularity, 2)
                },
                "categories": categories,
                "top_areas": popular_areas[:10]
            },
            "timestamp": "2025-08-19T22:50:00"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get areas overview: {str(e)}")

@router.get("/trends")
async def get_market_trends(
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get market trends across all regions"""
    try:
        # Get popular areas for trend analysis
        popular_areas = await area_service.get_popular_areas(15)
        
        trends = {
            "price_trends": {
                "rising": [],
                "stable": [],
                "declining": []
            },
            "popular_regions": [],
            "market_sentiment": "neutral"
        }
        
        # Analyze trends for each area
        for area in popular_areas:
            area_name = area.get("internet_name", area.get("dld_area_name", "Unknown"))
            
            # Get analytics for the area
            analytics = await area_service.get_region_analytics(area_name, 30)
            if "error" not in analytics:
                price_trend = analytics.get("analytics", {}).get("price_trend", "stable")
                trends["price_trends"][price_trend].append({
                    "name": area_name,
                    "popularity_score": area.get("popularity_score", 0),
                    "avg_price": analytics.get("analytics", {}).get("avg_price_aed", 0)
                })
            
            # Add to popular regions
            trends["popular_regions"].append({
                "name": area_name,
                "popularity_score": area.get("popularity_score", 0),
                "transaction_volume": area.get("transaction_volume", 0)
            })
        
        # Determine overall market sentiment
        rising_count = len(trends["price_trends"]["rising"])
        declining_count = len(trends["price_trends"]["declining"])
        
        if rising_count > declining_count * 1.5:
            trends["market_sentiment"] = "bullish"
        elif declining_count > rising_count * 1.5:
            trends["market_sentiment"] = "bearish"
        else:
            trends["market_sentiment"] = "neutral"
        
        return {
            "success": True,
            "data": trends,
            "timestamp": "2025-08-19T22:50:00"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market trends: {str(e)}")

@router.get("/categories/{category}")
async def get_areas_by_category(
    category: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get all areas in a specific category (Downtown, Marina, Suburban, etc.)"""
    try:
        # This would need to be implemented in the service
        # For now, return a placeholder
        return {
            "success": True,
            "data": {
                "category": category,
                "areas": [],
                "message": "Category filtering will be implemented in the next iteration"
            },
            "timestamp": "2025-08-19T22:50:00"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get areas by category: {str(e)}")
