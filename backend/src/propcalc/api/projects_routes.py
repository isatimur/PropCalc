#!/usr/bin/env python3
"""
Projects Routes - Real estate project management and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..domain.security.oauth2 import User, get_current_user
from ..infrastructure.database.postgres_db import get_db_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["projects"])

@router.get("/projects", response_model=Dict[str, Any])
async def get_projects(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    location: Optional[str] = Query(None, description="Filter by location"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Get real projects data from database with pagination and filters"""
    try:
        db_instance = await get_db_instance()
        conn = await db_instance.get_connection()
        try:
            # Build query with filters
            query = """
                SELECT
                    id,
                    transaction_id as dld_id,
                    location,
                    property_type,
                    price_aed as price,
                    area_sqft as area,
                    developer_name as developer,
                    transaction_date as created_at
                FROM dld_transactions
                WHERE 1=1
            """
            params = []
            param_count = 0

            if location:
                param_count += 1
                query += f" AND location ILIKE ${param_count}"
                params.append(f"%{location}%")

            if property_type:
                param_count += 1
                query += f" AND property_type ILIKE ${param_count}"
                params.append(f"%{property_type}%")

            if min_price is not None:
                param_count += 1
                query += f" AND price_aed >= ${param_count}"
                params.append(min_price)

            if max_price is not None:
                param_count += 1
                query += f" AND price_aed <= ${param_count}"
                params.append(max_price)

            # Get total count
            count_query = query.replace("SELECT id,", "SELECT COUNT(*)")
            total_count = await conn.fetchval(count_query, *params)

            # Add pagination and ordering
            query += " ORDER BY transaction_date DESC LIMIT $%d OFFSET $%d" % (param_count + 1, param_count + 2)
            params.extend([limit, offset])

            # Execute query
            projects_data = await conn.fetch(query, *params)

            # Format projects
            projects = []
            for project in projects_data:
                # Calculate Vantage Score (placeholder - would be calculated)
                vantage_score = 80.0  # This would be calculated from real Vantage Score data

                projects.append({
                    "id": f"proj-{project['id']:03d}",
                    "name": f"{project['location']} {project['property_type']}",
                    "location": project['location'] or "Unknown",
                    "property_type": project['property_type'] or "Unknown",
                    "price": project['price'] or 0,
                    "area": project['area'] or 0,
                    "vantage_score": vantage_score,
                    "developer": project['developer'] or "Private Developer",
                    "bedrooms": None,  # Not available in current schema
                    "bathrooms": None,  # Not available in current schema
                    "parking_spaces": None,  # Not available in current schema
                    "floor": None,  # Not available in current schema
                    "view": None,  # Not available in current schema
                    "completion_date": None,  # Not available in current schema
                    "dld_id": project['dld_id'],
                    "created_at": project['created_at'].isoformat() if project['created_at'] else None
                })

            return {
                "projects": projects,
                "total": total_count or 0,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < (total_count or 0)
            }
        finally:
            await db_instance.release_connection(conn)

    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch projects")

@router.get("/projects/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Get specific project details from database"""
    try:
        db_instance = await get_db_instance()
        conn = await db_instance.get_connection()
        try:
            # Extract numeric ID from project_id
            try:
                numeric_id = int(project_id.replace("proj-", ""))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid project ID format")

            # Get project data
            project_data = await conn.fetchrow(
                """
                SELECT
                    id,
                    transaction_id as dld_id,
                    location,
                    property_type,
                    price_aed as price,
                    area_sqft as area,
                    developer_name as developer,
                    transaction_date as created_at
                FROM dld_transactions
                WHERE id = $1
                """,
                numeric_id
            )

            if not project_data:
                raise HTTPException(status_code=404, detail="Project not found")

            # Calculate Vantage Score (placeholder - would be calculated)
            vantage_score = 80.0  # This would be calculated from real Vantage Score data

            project = {
                "id": f"proj-{project_data['id']:03d}",
                "name": f"{project_data['location']} {project_data['property_type']}",
                "location": project_data['location'] or "Unknown",
                "property_type": project_data['property_type'] or "Unknown",
                "price": project_data['price'] or 0,
                "area": project_data['area'] or 0,
                "vantage_score": vantage_score,
                "developer": project_data['developer'] or "Private Developer",
                "bedrooms": None,  # Not available in current schema
                "bathrooms": None,  # Not available in current schema
                "parking_spaces": None,  # Not available in current schema
                "floor": None,  # Not available in current schema
                "view": None,  # Not available in current schema
                "completion_date": None,  # Not available in current schema
                "dld_id": project_data['dld_id'],
                "created_at": project_data['created_at'].isoformat() if project_data['created_at'] else None
            }

            return project
        finally:
            await db_instance.release_connection(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch project")

@router.get("/projects/{project_id}/analytics")
async def get_project_analytics(project_id: str, current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Get project analytics and insights"""
    try:
        db_instance = await get_db_instance()
        conn = await db_instance.get_connection()
        try:
            # Extract numeric ID from project_id
            try:
                numeric_id = int(project_id.replace("proj-", ""))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid project ID format")

            # Get project data for analytics
            project_data = await conn.fetchrow(
                """
                SELECT
                    location,
                    property_type,
                    price_aed,
                    area_sqft,
                    developer_name
                FROM dld_transactions
                WHERE id = $1
                """,
                numeric_id
            )

            if not project_data:
                raise HTTPException(status_code=404, detail="Project not found")

            # Get market comparison data
            market_comparison = await conn.fetchrow(
                """
                SELECT
                    AVG(price_aed) as market_avg_price,
                    AVG(area_sqft) as market_avg_area,
                    COUNT(*) as market_total_properties
                FROM dld_transactions
                WHERE location = $1 AND property_type = $2
                """,
                project_data['location'], project_data['property_type']
            )

            # Calculate price per sqft
            project_price_per_sqft = project_data['price_aed'] / project_data['area_sqft'] if project_data['area_sqft'] else 0
            market_price_per_sqft = market_comparison['market_avg_price'] / market_comparison['market_avg_area'] if market_comparison['market_avg_area'] else 0

            # Calculate price positioning
            price_positioning = "above_market"
            if project_price_per_sqft <= market_price_per_sqft * 0.9:
                price_positioning = "below_market"
            elif project_price_per_sqft <= market_price_per_sqft * 1.1:
                price_positioning = "market_rate"

            analytics = {
                "project_id": project_id,
                "price_analysis": {
                    "project_price": project_data['price_aed'],
                    "project_price_per_sqft": round(project_price_per_sqft, 2),
                    "market_avg_price": round(market_comparison['market_avg_price'] or 0, 2),
                    "market_avg_price_per_sqft": round(market_price_per_sqft, 2),
                    "price_positioning": price_positioning
                },
                "market_context": {
                    "location": project_data['location'],
                    "property_type": project_data['property_type'],
                    "total_properties_in_area": market_comparison['market_total_properties'] or 0
                },
                "recommendations": [
                    "Consider market timing for optimal pricing",
                    "Analyze comparable properties in the area",
                    "Monitor market trends for price adjustments"
                ]
            }

            return analytics
        finally:
            await db_instance.release_connection(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch project analytics")
