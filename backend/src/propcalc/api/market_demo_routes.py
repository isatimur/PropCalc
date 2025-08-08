from datetime import datetime

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])

@router.get("/market/overview")
async def get_demo_market_overview():
    """Demo market overview without authentication"""
    try:
        # Mock data for demo
        return {
            "total_transactions": 1511882,
            "average_price": 2850000,
            "market_sentiment": "bullish",
            "average_vantage_score": 78.5,
            "total_properties": 12500,
            "top_locations": [
                {"name": "Dubai Marina", "transactions": 12500, "avg_price": 3200000},
                {"name": "Palm Jumeirah", "transactions": 8900, "avg_price": 4500000},
                {"name": "Downtown Dubai", "transactions": 7600, "avg_price": 3800000},
                {"name": "JBR", "transactions": 6800, "avg_price": 2900000},
                {"name": "Business Bay", "transactions": 5200, "avg_price": 2600000}
            ],
            "property_types": [
                {"type": "Apartment", "count": 8500, "avg_price": 2200000},
                {"type": "Villa", "count": 3200, "avg_price": 4500000},
                {"type": "Townhouse", "count": 800, "avg_price": 3200000}
            ],
            "market_trends": {
                "price_change_30d": 2.5,
                "volume_change_30d": 8.2,
                "sentiment_score": 0.75
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting demo market overview: {str(e)}")

@router.get("/market/trends")
async def get_demo_market_trends():
    """Demo market trends without authentication"""
    try:
        return {
            "price_change_30d": 2.5,
            "price_change_90d": 5.8,
            "volume_change_30d": 8.2,
            "volume_change_90d": 12.5,
            "sentiment_score": 0.75,
            "trend_direction": "upward",
            "confidence_level": 0.85
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting demo market trends: {str(e)}")

@router.get("/projects")
async def get_demo_projects(limit: int = 10, offset: int = 0):
    """Demo projects without authentication"""
    try:
        # Mock projects data
        projects = [
            {
                "id": "1",
                "name": "Marina Heights",
                "location": "Dubai Marina",
                "developer": "Emaar Properties",
                "property_type": "Apartment",
                "price": 2800000,
                "area": 1200,
                "bedrooms": 2,
                "bathrooms": 2,
                "parking_spaces": 1,
                "floor": 15,
                "view": "Marina View",
                "completion_date": "2024-06-15",
                "vantage_score": 82.5
            },
            {
                "id": "2",
                "name": "Palm Vista",
                "location": "Palm Jumeirah",
                "developer": "Nakheel",
                "property_type": "Villa",
                "price": 5200000,
                "area": 2800,
                "bedrooms": 4,
                "bathrooms": 3,
                "parking_spaces": 2,
                "floor": 1,
                "view": "Sea View",
                "completion_date": "2024-08-20",
                "vantage_score": 89.2
            },
            {
                "id": "3",
                "name": "Downtown Elite",
                "location": "Downtown Dubai",
                "developer": "Emaar Properties",
                "property_type": "Apartment",
                "price": 3800000,
                "area": 1400,
                "bedrooms": 3,
                "bathrooms": 2,
                "parking_spaces": 1,
                "floor": 25,
                "view": "Burj Khalifa View",
                "completion_date": "2024-07-10",
                "vantage_score": 85.7
            },
            {
                "id": "4",
                "name": "JBR Paradise",
                "location": "JBR",
                "developer": "Meraas",
                "property_type": "Apartment",
                "price": 2900000,
                "area": 1100,
                "bedrooms": 2,
                "bathrooms": 2,
                "parking_spaces": 1,
                "floor": 12,
                "view": "Beach View",
                "completion_date": "2024-09-05",
                "vantage_score": 78.9
            },
            {
                "id": "5",
                "name": "Business Bay Tower",
                "location": "Business Bay",
                "developer": "Damac Properties",
                "property_type": "Apartment",
                "price": 2600000,
                "area": 1000,
                "bedrooms": 2,
                "bathrooms": 2,
                "parking_spaces": 1,
                "floor": 18,
                "view": "City View",
                "completion_date": "2024-10-15",
                "vantage_score": 76.3
            }
        ]

        return {
            "projects": projects[offset:offset+limit],
            "total": len(projects),
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting demo projects: {str(e)}")

@router.get("/vantage-score/stats")
async def get_demo_vantage_score_stats():
    """Demo Vantage Score statistics without authentication"""
    try:
        return {
            "data": {
                "total_transactions": 1511882,
                "average_price": 2850000,
                "data_source": "Real DLD Data",
                "model_accuracy": 0.89,
                "last_updated": datetime.now().isoformat(),
                "score_distribution": {
                    "excellent": 0.25,
                    "good": 0.45,
                    "average": 0.20,
                    "poor": 0.10
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting demo Vantage Score stats: {str(e)}")

@router.get("/data-quality")
async def get_demo_data_quality():
    """Demo data quality metrics without authentication"""
    try:
        return {
            "data_freshness": {
                "last_update": datetime.now().isoformat(),
                "update_frequency": "4 hours",
                "data_age_hours": 2.5
            },
            "data_completeness": {
                "total_records": 1511882,
                "complete_records": 1485000,
                "completeness_rate": 0.98
            },
            "data_accuracy": {
                "validation_score": 0.95,
                "error_rate": 0.02,
                "confidence_level": 0.89
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting demo data quality: {str(e)}")
