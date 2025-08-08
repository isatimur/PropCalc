"""
Analytics API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from propcalc.infrastructure.database.database import get_async_db
from propcalc.infrastructure.repositories.dld_repository import (
    area_market_stats_repo, dld_transaction_repo, dld_area_repo
)

router = APIRouter()


@router.get("/top-areas")
async def get_top_performing_areas(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """Get top performing areas by transaction volume"""
    try:
        return await area_market_stats_repo.get_top_performing_areas_async(db, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top areas: {str(e)}")


@router.get("/area/{area_id}/statistics")
async def get_area_statistics(
    area_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get market statistics for a specific area"""
    try:
        stats = await area_market_stats_repo.get_by_area_id_async(db, area_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Area statistics not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving area statistics: {str(e)}")


@router.get("/market-overview")
async def get_market_overview(
    db: AsyncSession = Depends(get_async_db)
):
    """Get overall market overview and statistics"""
    try:
        # Get overall market statistics
        overall_stats = await dld_transaction_repo.get_market_statistics_async(db)
        
        # Get top performing areas
        top_areas = await area_market_stats_repo.get_top_performing_areas_async(db, 5)
        
        # Get total areas with transactions
        areas_with_transactions = await dld_area_repo.get_areas_with_transactions_async(db, 1000)
        
        return {
            "overall_market_statistics": overall_stats,
            "top_performing_areas": top_areas,
            "total_areas_with_transactions": len(areas_with_transactions),
            "market_health": "healthy" if overall_stats.get("total_transactions", 0) > 0 else "no_data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving market overview: {str(e)}")


@router.get("/property-type-analysis")
async def get_property_type_analysis(
    area_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Get property type distribution analysis"""
    try:
        # Get transactions for analysis
        if area_id:
            transactions = await dld_transaction_repo.get_by_area_async(db, area_id, 1000)
        else:
            transactions = await dld_transaction_repo.get_multi_async(db, limit=1000)
        
        # Analyze property types
        property_types = {}
        total_transactions = len(transactions)
        
        for transaction in transactions:
            prop_type = transaction.property_type
            if prop_type in property_types:
                property_types[prop_type] += 1
            else:
                property_types[prop_type] = 1
        
        # Calculate percentages
        property_type_analysis = {}
        for prop_type, count in property_types.items():
            percentage = (count / total_transactions) * 100 if total_transactions > 0 else 0
            property_type_analysis[prop_type] = {
                "count": count,
                "percentage": round(percentage, 2)
            }
        
        return {
            "total_transactions": total_transactions,
            "property_type_distribution": property_type_analysis,
            "area_id": area_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving property type analysis: {str(e)}")


@router.get("/price-analysis")
async def get_price_analysis(
    area_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Get price analysis and trends"""
    try:
        # Get market statistics
        market_stats = await dld_transaction_repo.get_market_statistics_async(db, area_id)
        
        # Get recent transactions for price range analysis
        if area_id:
            recent_transactions = await dld_transaction_repo.get_by_area_async(db, area_id, 100)
        else:
            recent_transactions = await dld_transaction_repo.get_multi_async(db, limit=100)
        
        # Calculate price ranges
        prices = [t.price_aed for t in recent_transactions if t.price_aed > 0]
        prices.sort()
        
        if prices:
            price_analysis = {
                "min_price": min(prices),
                "max_price": max(prices),
                "median_price": prices[len(prices) // 2],
                "price_range": max(prices) - min(prices),
                "total_transactions_analyzed": len(prices)
            }
        else:
            price_analysis = {
                "min_price": 0,
                "max_price": 0,
                "median_price": 0,
                "price_range": 0,
                "total_transactions_analyzed": 0
            }
        
        return {
            "market_statistics": market_stats,
            "price_analysis": price_analysis,
            "area_id": area_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving price analysis: {str(e)}")


@router.get("/developer-analysis")
async def get_developer_analysis(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_db)
):
    """Get developer performance analysis"""
    try:
        # Get all transactions
        transactions = await dld_transaction_repo.get_multi_async(db, limit=1000)
        
        # Group by developer
        developer_stats = {}
        for transaction in transactions:
            if transaction.developer_name:
                dev_name = transaction.developer_name
                if dev_name not in developer_stats:
                    developer_stats[dev_name] = {
                        "total_transactions": 0,
                        "total_volume": 0,
                        "avg_price": 0,
                        "property_types": set()
                    }
                
                developer_stats[dev_name]["total_transactions"] += 1
                developer_stats[dev_name]["total_volume"] += transaction.price_aed
                developer_stats[dev_name]["property_types"].add(transaction.property_type)
        
        # Calculate averages and format
        for dev_name, stats in developer_stats.items():
            stats["avg_price"] = stats["total_volume"] / stats["total_transactions"] if stats["total_transactions"] > 0 else 0
            stats["property_types"] = list(stats["property_types"])
        
        # Sort by total volume
        sorted_developers = sorted(
            developer_stats.items(),
            key=lambda x: x[1]["total_volume"],
            reverse=True
        )[:limit]
        
        return {
            "top_developers": [
                {
                    "developer_name": dev_name,
                    "statistics": stats
                }
                for dev_name, stats in sorted_developers
            ],
            "total_developers_analyzed": len(developer_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving developer analysis: {str(e)}") 