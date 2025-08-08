"""
Real DLD (Dubai Land Department) routes with comprehensive data integration
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..core.dld_ingestion import get_dld_ingestion

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/real-dld", tags=["Real DLD"])

@router.get("/health")
async def check_real_dld_health() -> dict[str, Any]:
    """Check real DLD API connection health"""
    try:
        dld_ingestion = await get_dld_ingestion()
        status = await dld_ingestion.get_ingestion_status()

        return {
            "status": "healthy" if status["api_connected"] else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Real DLD Integration",
            "last_sync": status["last_sync"],
            "data_freshness": "4 hours",
            "api_connected": status["api_connected"],
            "data_source": status["data_source"]
        }
    except Exception as e:
        logger.error(f"Real DLD health check failed: {e}")
        raise HTTPException(status_code=503, detail="Real DLD service unavailable")

@router.get("/transactions/recent")
async def get_recent_real_transactions(
    hours: int = 4,
    location: str | None = None,
    property_type: str | None = None
) -> dict[str, Any]:
    """Get recent real DLD transactions"""
    try:
        dld_ingestion = await get_dld_ingestion()

        async with dld_ingestion as ingestion:
            # Fetch real transactions
            transactions = await ingestion.fetch_recent_transactions(hours)

            # Apply filters
            if location:
                transactions = [t for t in transactions if location.lower() in t.location.lower()]
            if property_type:
                transactions = [t for t in transactions if property_type.lower() in t.property_type.lower()]

            # Convert to dict for JSON response
            transaction_data = []
            for tx in transactions:
                transaction_data.append({
                    "transaction_id": tx.transaction_id,
                    "property_type": tx.property_type,
                    "location": tx.location,
                    "transaction_date": tx.transaction_date.isoformat(),
                    "price_aed": tx.price_aed,
                    "area_sqft": tx.area_sqft,
                    "developer_name": tx.developer_name,
                    "transaction_type": tx.transaction_type,
                    "property_id": tx.property_id,
                    "unit_number": tx.unit_number,
                    "building_name": tx.building_name,
                    "project_name": tx.project_name,
                    "floor_number": tx.floor_number,
                    "bedrooms": tx.bedrooms,
                    "bathrooms": tx.bathrooms,
                    "parking_spaces": tx.parking_spaces,
                    "view": tx.view
                })

            # Calculate quality metrics
            quality_report = ingestion.calculate_data_quality(transactions)

            return {
                "transactions": transaction_data,
                "total_count": len(transaction_data),
                "filters_applied": {
                    "hours": hours,
                    "location": location,
                    "property_type": property_type
                },
                "quality_report": {
                    "total_records": quality_report.total_records,
                    "valid_records": quality_report.valid_records,
                    "quality_score": quality_report.quality_score,
                    "quality_level": quality_report.quality_level.value,
                    "processing_time_seconds": quality_report.processing_time_seconds
                }
            }
    except Exception as e:
        logger.error(f"Error fetching recent real DLD transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent transactions")

@router.get("/transactions/range")
async def get_transactions_by_date_range(
    start_date: str,
    end_date: str,
    location: str | None = None,
    property_type: str | None = None,
    limit: int = 1000
) -> dict[str, Any]:
    """Get real DLD transactions for a specific date range"""
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Validate date range
        if start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

        if (end_dt - start_dt).days > 365:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 1 year")

        dld_ingestion = await get_dld_ingestion()

        async with dld_ingestion as ingestion:
            # Fetch real transactions
            transactions = await ingestion.fetch_transactions_by_date_range(
                start_dt, end_dt, location, property_type, limit
            )

            # Convert to dict for JSON response
            transaction_data = []
            for tx in transactions:
                transaction_data.append({
                    "transaction_id": tx.transaction_id,
                    "property_type": tx.property_type,
                    "location": tx.location,
                    "transaction_date": tx.transaction_date.isoformat(),
                    "price_aed": tx.price_aed,
                    "area_sqft": tx.area_sqft,
                    "developer_name": tx.developer_name,
                    "transaction_type": tx.transaction_type,
                    "property_id": tx.property_id,
                    "unit_number": tx.unit_number,
                    "building_name": tx.building_name,
                    "project_name": tx.project_name,
                    "floor_number": tx.floor_number,
                    "bedrooms": tx.bedrooms,
                    "bathrooms": tx.bathrooms,
                    "parking_spaces": tx.parking_spaces,
                    "view": tx.view
                })

            # Calculate quality metrics
            quality_report = ingestion.calculate_data_quality(transactions)

            return {
                "transactions": transaction_data,
                "total_count": len(transaction_data),
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "filters_applied": {
                    "location": location,
                    "property_type": property_type,
                    "limit": limit
                },
                "quality_report": {
                    "total_records": quality_report.total_records,
                    "valid_records": quality_report.valid_records,
                    "quality_score": quality_report.quality_score,
                    "quality_level": quality_report.quality_level.value,
                    "processing_time_seconds": quality_report.processing_time_seconds
                }
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching transactions by date range: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")

@router.get("/transactions/{transaction_id}")
async def get_transaction_by_id(transaction_id: str) -> dict[str, Any]:
    """Get a specific real DLD transaction by ID"""
    try:
        dld_ingestion = await get_dld_ingestion()

        async with dld_ingestion as ingestion:
            # Fetch recent transactions and find the specific one
            transactions = await ingestion.fetch_recent_transactions(24)  # Last 24 hours

            # Find the specific transaction
            transaction = None
            for tx in transactions:
                if tx.transaction_id == transaction_id:
                    transaction = tx
                    break

            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            return {
                "transaction_id": transaction.transaction_id,
                "property_type": transaction.property_type,
                "location": transaction.location,
                "transaction_date": transaction.transaction_date.isoformat(),
                "price_aed": transaction.price_aed,
                "area_sqft": transaction.area_sqft,
                "developer_name": transaction.developer_name,
                "transaction_type": transaction.transaction_type,
                "property_id": transaction.property_id,
                "unit_number": transaction.unit_number,
                "building_name": transaction.building_name,
                "project_name": transaction.project_name,
                "floor_number": transaction.floor_number,
                "bedrooms": transaction.bedrooms,
                "bathrooms": transaction.bathrooms,
                "parking_spaces": transaction.parking_spaces,
                "view": transaction.view,
                "additional_details": {
                    "floor_number": transaction.floor_number,
                    "bedrooms": transaction.bedrooms,
                    "bathrooms": transaction.bathrooms,
                    "parking_spaces": transaction.parking_spaces,
                    "view": transaction.view
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transaction")

@router.get("/analytics/summary")
async def get_real_dld_analytics_summary(days: int = 30) -> dict[str, Any]:
    """Get real DLD analytics summary for the specified period"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        dld_ingestion = await get_dld_ingestion()

        async with dld_ingestion as ingestion:
            # Fetch transactions for analysis period
            transactions = await ingestion.fetch_transactions_by_date_range(
                start_date, end_date, limit=10000
            )

            # Calculate analytics
            if transactions:
                total_transactions = len(transactions)
                total_volume = sum(tx.price_aed for tx in transactions)
                average_price = total_volume / total_transactions if total_transactions > 0 else 0
                average_area = sum(tx.area_sqft for tx in transactions) / total_transactions if total_transactions > 0 else 0

                # Location analysis
                location_counts = {}
                for tx in transactions:
                    location_counts[tx.location] = location_counts.get(tx.location, 0) + 1

                top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]

                # Developer analysis
                developer_counts = {}
                for tx in transactions:
                    developer_counts[tx.developer_name] = developer_counts.get(tx.developer_name, 0) + 1

                top_developers = sorted(developer_counts.items(), key=lambda x: x[1], reverse=True)[:10]

                # Property type distribution
                property_type_counts = {}
                for tx in transactions:
                    property_type_counts[tx.property_type] = property_type_counts.get(tx.property_type, 0) + 1

                # Transaction type distribution
                transaction_type_counts = {}
                for tx in transactions:
                    transaction_type_counts[tx.transaction_type] = transaction_type_counts.get(tx.transaction_type, 0) + 1

                analytics = {
                    "total_transactions": total_transactions,
                    "total_volume_aed": total_volume,
                    "average_price_aed": average_price,
                    "average_area_sqft": average_area,
                    "top_locations": [{"location": loc, "count": count} for loc, count in top_locations],
                    "top_developers": [{"developer": dev, "count": count} for dev, count in top_developers],
                    "property_type_distribution": property_type_counts,
                    "transaction_type_distribution": transaction_type_counts
                }
            else:
                analytics = {
                    "total_transactions": 0,
                    "total_volume_aed": 0,
                    "average_price_aed": 0,
                    "average_area_sqft": 0,
                    "top_locations": [],
                    "top_developers": [],
                    "property_type_distribution": {},
                    "transaction_type_distribution": {}
                }

            # Calculate quality metrics
            quality_report = ingestion.calculate_data_quality(transactions)

            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "analytics": analytics,
                "quality_report": {
                    "total_records": quality_report.total_records,
                    "valid_records": quality_report.valid_records,
                    "quality_score": quality_report.quality_score,
                    "quality_level": quality_report.quality_level.value
                }
            }

    except Exception as e:
        logger.error(f"Error generating real DLD analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate analytics")

@router.post("/ingestion/trigger")
async def trigger_real_dld_ingestion(background_tasks: BackgroundTasks) -> dict[str, Any]:
    """Trigger manual real DLD data ingestion"""
    try:
        # Add background task for data ingestion
        background_tasks.add_task(perform_real_dld_ingestion)

        return {
            "message": "Real DLD data ingestion triggered successfully",
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error triggering real DLD ingestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger ingestion")

async def perform_real_dld_ingestion():
    """Background task to perform real DLD data ingestion"""
    try:
        logger.info("Starting real DLD data ingestion...")

        dld_ingestion = await get_dld_ingestion()

        async with dld_ingestion as ingestion:
            # Fetch recent transactions (last 4 hours)
            transactions = await ingestion.fetch_recent_transactions(hours=4)

            # Process and store transactions
            result = await ingestion.process_and_store_transactions(transactions)

            logger.info(f"Real DLD ingestion completed: {result}")

    except Exception as e:
        logger.error(f"Real DLD ingestion failed: {e}")
