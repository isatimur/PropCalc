"""
DLD API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from propcalc.infrastructure.database.database import get_async_db
from propcalc.infrastructure.repositories.dld_repository import (
    dld_area_repo, dld_transaction_repo
)

router = APIRouter()


@router.get("/areas")
async def get_areas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Get DLD areas with optional search"""
    try:
        if search:
            return await dld_area_repo.search_areas_async(db, search, limit)
        return await dld_area_repo.get_multi_async(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving areas: {str(e)}")


@router.get("/areas/{area_id}")
async def get_area(
    area_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get specific DLD area"""
    try:
        area = await dld_area_repo.get_by_area_id_async(db, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        return area
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving area: {str(e)}")


@router.get("/transactions")
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    area_id: Optional[int] = Query(None),
    property_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Get DLD transactions with filtering"""
    try:
        filters = {}
        if area_id:
            filters["area_id"] = area_id
        if property_type:
            filters["property_type"] = property_type
        
        return await dld_transaction_repo.get_multi_async(
            db, skip=skip, limit=limit, filters=filters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transactions: {str(e)}")


@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get specific DLD transaction"""
    try:
        transaction = await dld_transaction_repo.get_by_transaction_id_async(db, transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transaction: {str(e)}")


@router.get("/areas/{area_id}/transactions")
async def get_area_transactions(
    area_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """Get transactions for a specific area"""
    try:
        return await dld_transaction_repo.get_by_area_async(db, area_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving area transactions: {str(e)}")


@router.get("/market-statistics")
async def get_market_statistics(
    area_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Get market statistics"""
    try:
        return await dld_transaction_repo.get_market_statistics_async(db, area_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving market statistics: {str(e)}")


@router.get("/areas/{area_id}/statistics")
async def get_area_statistics(
    area_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get comprehensive statistics for a specific area"""
    try:
        # Get area details
        area = await dld_area_repo.get_by_area_id_async(db, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        
        # Get market statistics
        market_stats = await dld_transaction_repo.get_market_statistics_async(db, area_id)
        
        # Get recent transactions
        recent_transactions = await dld_transaction_repo.get_by_area_async(db, area_id, 10)
        
        return {
            "area": area,
            "market_statistics": market_stats,
            "recent_transactions": recent_transactions,
            "total_transactions": len(recent_transactions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving area statistics: {str(e)}") 