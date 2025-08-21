#!/usr/bin/env python3
"""
Unified DLD Routes - Comprehensive DLD data management and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import json

from ..core.comprehensive_dld_loader import ComprehensiveDldLoader
from ..core.enhanced_analytics import DldAnalyticsService as EnhancedAnalytics
from ..core.dld_kml_integration import DLDKMLIntegration as DldKmlIntegration
from ..infrastructure.repositories.dld_repository import DldRepository
from ..domain.schemas import (
    DldDataRequest,
    DldAnalyticsResponse,
    MarketTrendsResponse,
    PortfolioAnalysisResponse,
    TransactionSummaryResponse,
    GeospatialAnalysisResponse
)
from ..core.logging import get_logger
from ..core.metrics import track_request_metrics as record_api_call
from ..domain.schemas import User
from ..domain.security.oauth2 import get_current_user
from ..core.enhanced_analytics import DldAnalyticsService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/dld", tags=["DLD"])

# Dependency injection
def get_dld_loader() -> ComprehensiveDldLoader:
    """Get DLD loader instance"""
    return ComprehensiveDldLoader()

def get_analytics() -> EnhancedAnalytics:
    """Get analytics instance"""
    return EnhancedAnalytics()

def get_dld_repository() -> DldRepository:
    """Get DLD repository instance"""
    return DldRepository()

@router.post("/load", response_model=Dict[str, Any])
async def load_dld_data(
    request: DldDataRequest,
    background_tasks: BackgroundTasks,
    dld_loader: ComprehensiveDldLoader = Depends(get_dld_loader)
):
    """
    Load DLD data from various sources with comprehensive processing
    """
    try:
        record_api_call("dld_load")
        logger.info(f"Starting DLD data load for source: {request.source}")
        
        # Add to background tasks for large data loads
        if request.bulk_load:
            background_tasks.add_task(
                dld_loader.load_bulk_data,
                source=request.source,
                filters=request.filters,
                options=request.options
            )
            return {
                "status": "accepted",
                "message": "Bulk data load started in background",
                "task_id": f"dld_load_{datetime.now().isoformat()}"
            }
        
        # Immediate load for smaller datasets
        result = await dld_loader.load_data(
            source=request.source,
            filters=request.filters,
            options=request.options
        )
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error loading DLD data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load DLD data: {str(e)}")

@router.get("/analytics", response_model=DldAnalyticsResponse)
async def get_dld_analytics(
    current_user: User = Depends(get_current_user),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    property_usage: Optional[str] = Query(None, description="Property usage filter"),
    property_subtype: Optional[str] = Query(None, description="Property subtype filter"),
    registration_type: Optional[str] = Query(None, description="Registration type filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    area: Optional[str] = Query(None, description="Area filter"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    developer_name: Optional[str] = Query(None, description="Developer name filter"),
    project_name: Optional[str] = Query(None, description="Project name filter"),
    buyer_nationality: Optional[str] = Query(None, description="Buyer nationality filter"),
    seller_nationality: Optional[str] = Query(None, description="Seller nationality filter")
):
    """Get comprehensive DLD analytics with filters"""
    try:
        # Record API call for analytics
        await record_api_call(current_user.id, "dld_analytics", "GET")
        
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # If no dates provided, default to last 30 days
        if not start_dt and not end_dt:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        elif not start_dt:
            start_dt = end_dt - timedelta(days=30)
        elif not end_dt:
            end_dt = start_dt + timedelta(days=30)
        
        # Build filters
        filters = {
            "property_type": property_type,
            "property_usage": property_usage,
            "property_subtype": property_subtype,
            "registration_type": registration_type,
            "location": location,
            "area": area,
            "min_price": min_price,
            "max_price": max_price,
            "developer_name": developer_name,
            "project_name": project_name,
            "buyer_nationality": buyer_nationality,
            "seller_nationality": seller_nationality,
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        analytics_service = DldAnalyticsService()
        analytics_data = await analytics_service.generate_dld_analytics(
            start_date=start_dt,
            end_date=end_dt,
            filters=filters
        )
        
        return analytics_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting DLD analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market-trends", response_model=MarketTrendsResponse)
async def get_market_trends(
    timeframe: str = Query("1y", description="Timeframe: 1m, 3m, 6m, 1y, 3y, 5y"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    region: Optional[str] = Query(None, description="Region filter"),
    analytics: EnhancedAnalytics = Depends(get_analytics)
):
    """
    Get market trends and analysis
    """
    try:
        record_api_call("dld_market_trends")
        
        result = await analytics.analyze_market_trends(
            timeframe=timeframe,
            property_type=property_type,
            region=region
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing market trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze market trends: {str(e)}")

@router.get("/portfolio", response_model=PortfolioAnalysisResponse)
async def get_portfolio_analysis(
    portfolio_id: str = Query(..., description="Portfolio identifier"),
    include_geospatial: bool = Query(False, description="Include geospatial analysis"),
    analytics: EnhancedAnalytics = Depends(get_analytics)
):
    """
    Get portfolio analysis and performance metrics
    """
    try:
        record_api_call("dld_portfolio_analysis")
        
        result = await analytics.analyze_portfolio(
            portfolio_id=portfolio_id,
            include_geospatial=include_geospatial
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")

@router.get("/transactions", response_model=TransactionSummaryResponse)
async def get_transaction_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    transaction_type: Optional[str] = Query(None, description="Transaction type filter"),
    min_value: Optional[float] = Query(None, description="Minimum transaction value"),
    max_value: Optional[float] = Query(None, description="Maximum transaction value"),
    repository: DldRepository = Depends(get_dld_repository)
):
    """
    Get transaction summary and statistics
    """
    try:
        record_api_call("dld_transactions")
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        result = await repository.get_transaction_summary(
            start_date=start_dt,
            end_date=end_dt,
            transaction_type=transaction_type,
            min_value=min_value,
            max_value=max_value
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting transaction summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get transaction summary: {str(e)}")

@router.get("/geospatial", response_model=GeospatialAnalysisResponse)
async def get_geospatial_analysis(
    bounds: str = Query(..., description="Geographic bounds (min_lat,min_lng,max_lat,max_lng)"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    time_period: Optional[str] = Query(None, description="Time period filter"),
    dld_kml: DldKmlIntegration = Depends(lambda: DldKmlIntegration())
):
    """
    Get geospatial analysis combining DLD and KML data
    """
    try:
        record_api_call("dld_geospatial")
        
        # Parse bounds
        try:
            min_lat, min_lng, max_lat, max_lng = map(float, bounds.split(','))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid bounds format")
        
        result = await dld_kml.generate_geospatial_analysis(
            bounds=(min_lat, min_lng, max_lat, max_lng),
            property_type=property_type,
            time_period=time_period
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating geospatial analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate geospatial analysis: {str(e)}")

@router.get("/export")
async def export_dld_data(
    format: str = Query("csv", description="Export format: csv, json, excel"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    filters: Optional[str] = Query(None, description="JSON encoded filters"),
    repository: DldRepository = Depends(get_dld_repository)
):
    """
    Export DLD data in various formats
    """
    try:
        record_api_call("dld_export")
        
        # Parse filters
        filter_dict = json.loads(filters) if filters else {}
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        # Get data for export
        data = await repository.get_data_for_export(
            start_date=start_dt,
            end_date=end_dt,
            filters=filter_dict
        )
        
        if format.lower() == "csv":
            csv_content = repository.convert_to_csv(data)
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=dld_export_{datetime.now().strftime('%Y%m%d')}.csv"}
            )
        elif format.lower() == "json":
            return StreamingResponse(
                iter([json.dumps(data, default=str)]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=dld_export_{datetime.now().strftime('%Y%m%d')}.json"}
            )
        elif format.lower() == "excel":
            excel_content = repository.convert_to_excel(data)
            return StreamingResponse(
                iter([excel_content]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=dld_export_{datetime.now().strftime('%Y%m%d')}.xlsx"}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        logger.error(f"Error exporting DLD data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")

@router.get("/export/csv")
async def export_dld_data_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    property_usage: Optional[str] = Query(None, description="Property usage filter"),
    property_subtype: Optional[str] = Query(None, description="Property subtype filter"),
    registration_type: Optional[str] = Query(None, description="Registration type filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    area: Optional[str] = Query(None, description="Area filter"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    developer_name: Optional[str] = Query(None, description="Developer name filter"),
    project_name: Optional[str] = Query(None, description="Project name filter"),
    buyer_nationality: Optional[str] = Query(None, description="Buyer nationality filter"),
    seller_nationality: Optional[str] = Query(None, description="Seller nationality filter"),
    limit: Optional[int] = Query(10000, description="Maximum number of records to export")
):
    """Export DLD data to CSV with comprehensive filtering"""
    try:
        from fastapi.responses import StreamingResponse
        from io import StringIO
        import csv
        
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # If no dates provided, default to last 30 days
        if not start_dt and not end_dt:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        elif not start_dt:
            start_dt = end_dt - timedelta(days=30)
        elif not end_dt:
            end_dt = start_dt + timedelta(days=30)
        
        # Build filters
        filters = {
            "property_type": property_type,
            "property_usage": property_usage,
            "property_subtype": property_subtype,
            "registration_type": registration_type,
            "location": location,
            "area": area,
            "min_price": min_price,
            "max_price": max_price,
            "developer_name": developer_name,
            "project_name": project_name,
            "buyer_nationality": buyer_nationality,
            "seller_nationality": seller_nationality,
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Get data from repository
        from ..infrastructure.repositories.dld_repository import DldRepository
        repo = DldRepository()
        
        # Get filtered transactions
        transactions = await repo.get_transactions_for_export(
            start_date=start_dt,
            end_date=end_dt,
            filters=filters,
            limit=limit
        )
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        if transactions:
            writer.writerow(transactions[0].keys())
            # Write data
            for transaction in transactions:
                writer.writerow(transaction.values())
        
        output.seek(0)
        
        # Generate filename
        filename = f"dld_export_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error exporting DLD data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/export/excel")
async def export_dld_data_excel(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    property_usage: Optional[str] = Query(None, description="Property usage filter"),
    property_subtype: Optional[str] = Query(None, description="Property subtype filter"),
    registration_type: Optional[str] = Query(None, description="Registration type filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    area: Optional[str] = Query(None, description="Area filter"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    developer_name: Optional[str] = Query(None, description="Developer name filter"),
    project_name: Optional[str] = Query(None, description="Project name filter"),
    buyer_nationality: Optional[str] = Query(None, description="Buyer nationality filter"),
    seller_nationality: Optional[str] = Query(None, description="Seller nationality filter"),
    limit: Optional[int] = Query(10000, description="Maximum number of records to export")
):
    """Export DLD data to Excel with comprehensive filtering"""
    try:
        from fastapi.responses import Response
        import pandas as pd
        from io import BytesIO
        
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # If no dates provided, default to last 30 days
        if not start_dt and not end_dt:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        elif not start_dt:
            start_dt = end_dt - timedelta(days=30)
        elif not end_dt:
            end_dt = start_dt + timedelta(days=30)
        
        # Build filters
        filters = {
            "property_type": property_type,
            "property_usage": property_usage,
            "property_subtype": property_subtype,
            "registration_type": registration_type,
            "location": location,
            "area": area,
            "min_price": min_price,
            "max_price": max_price,
            "developer_name": developer_name,
            "project_name": project_name,
            "buyer_nationality": buyer_nationality,
            "seller_nationality": seller_nationality,
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Get data from repository
        from ..infrastructure.repositories.dld_repository import DldRepository
        repo = DldRepository()
        
        # Get filtered transactions
        transactions = await repo.get_transactions_for_export(
            start_date=start_dt,
            end_date=end_dt,
            filters=filters,
            limit=limit
        )
        
        # Convert to DataFrame and export to Excel
        df = pd.DataFrame(transactions)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='DLD_Transactions', index=False)
        
        output.seek(0)
        
        # Generate filename
        filename = f"dld_export_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}.xlsx"
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error exporting DLD data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def dld_health_check(
    repository: DldRepository = Depends(get_dld_repository)
):
    """
    Health check for DLD services
    """
    try:
        record_api_call("dld_health")
        
        # Check database connectivity
        db_status = await repository.check_health()
        
        # Check data freshness
        data_status = await repository.check_data_freshness()
        
        return {
            "status": "healthy" if db_status and data_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "data_freshness": "current" if data_status else "stale",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking DLD health: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/stats")
async def get_dld_statistics(
    repository: DldRepository = Depends(get_dld_repository)
):
    """
    Get DLD system statistics and metrics
    """
    try:
        record_api_call("dld_stats")
        
        stats = await repository.get_system_statistics()
        
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting DLD statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/test-db")
async def test_database_connection():
    """Test database connection and basic query"""
    try:
        from ..infrastructure.database.database import async_engine
        from sqlalchemy import text
        
        async with async_engine.connect() as conn:
            # Test basic connection
            result = await conn.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            
            # Test DLD transactions count
            result = await conn.execute(text("SELECT COUNT(*) as count FROM dld_transactions"))
            count_result = result.fetchone()
            
            return {
                "status": "success",
                "connection_test": test_result[0] if test_result else "failed",
                "dld_transactions_count": count_result[0] if count_result else "failed",
                "message": "Database connection successful"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Database connection failed"
        }

@router.get("/regions/mapping")
async def get_region_mapping():
    """Get region mapping between DLD areas and internet-friendly names"""
    try:
        from ..infrastructure.repositories.dld_repository import DldRepository
        repo = DldRepository()
        
        # Get unique areas from DLD transactions
        areas = await repo.get_unique_areas()
        
        # Create mapping suggestions
        region_mapping = []
        for area in areas:
            if area:
                # Clean the area name
                clean_name = area.strip()
                
                # Create internet-friendly version
                internet_name = clean_name
                internet_name = internet_name.replace('AL ', 'Al ')
                internet_name = internet_name.replace('AL-', 'Al-')
                internet_name = internet_name.replace('  ', ' ')
                internet_name = internet_name.replace(' - ', '-')
                internet_name = internet_name.replace(' / ', '/')
                
                region_mapping.append({
                    "dld_name": clean_name,
                    "internet_name": internet_name,
                    "suggested_keywords": [
                        clean_name,
                        internet_name,
                        clean_name.replace(' ', ''),
                        clean_name.replace(' ', '-').lower(),
                        clean_name.replace(' ', '_').lower()
                    ],
                    "search_optimization": {
                        "google_maps": f"https://www.google.com/maps/search/{clean_name}+Dubai",
                        "wikipedia": f"https://en.wikipedia.org/wiki/Special:Search?query={clean_name}+Dubai",
                        "property_finder": f"https://www.propertyfinder.ae/en/search?c=1&ob=mr&page=1&t=1&fu=0&ret=0&ro=0&ba=0&u=0&pf=0&fr=0&fs=0&q={clean_name}"
                    }
                })
        
        return {
            "total_regions": len(region_mapping),
            "mapping": region_mapping,
            "metadata": {
                "description": "DLD area names mapped to internet-friendly versions",
                "usage": "Use for search optimization, market analysis, and region-specific analytics",
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting region mapping: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/regions/analytics/{region_name}")
async def get_region_analytics(region_name: str):
    """Get detailed analytics for a specific region"""
    try:
        from ..infrastructure.repositories.dld_repository import DldRepository
        repo = DldRepository()
        
        # Get region-specific analytics
        analytics = await repo.get_region_analytics(region_name)
        
        return {
            "region_name": region_name,
            "analytics": analytics,
            "metadata": {
                "analysis_period": "Last 12 months",
                "data_source": "DLD Transactions Database",
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting region analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market/live")
async def get_live_market_analytics():
    """Get real-time market analytics and live data"""
    try:
        from ..infrastructure.repositories.dld_repository import DldRepository
        repo = DldRepository()
        
        # Get current market data
        current_data = await repo.get_live_market_data()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "market_status": "live",
            "data": current_data,
            "metadata": {
                "update_frequency": "real-time",
                "data_source": "DLD Live Transactions",
                "last_refresh": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting live market analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market/trends/realtime")
async def get_realtime_market_trends():
    """Get real-time market trends and momentum indicators"""
    try:
        from ..infrastructure.repositories.dld_repository import DldRepository
        repo = DldRepository()
        
        # Get real-time trends
        trends = await repo.get_realtime_market_trends()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "trends": trends,
            "momentum_indicators": {
                "market_velocity": "high" if trends.get("transaction_volume_trend") == "increasing" else "moderate",
                "price_momentum": "bullish" if trends.get("price_trend") == "rising" else "neutral",
                "volume_momentum": "strong" if trends.get("volume_trend") == "increasing" else "stable"
            },
            "metadata": {
                "analysis_period": "Last 24 hours",
                "update_frequency": "real-time",
                "confidence_score": 0.95
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time market trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
