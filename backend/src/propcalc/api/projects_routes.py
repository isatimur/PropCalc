"""
Projects API Routes
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from ..domain.security.oauth2 import User, get_current_user
from ..infrastructure.database.postgres_db import get_db_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["projects"])

@router.get("/projects")
async def get_projects(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    location: str | None = None,
    property_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None
) -> dict[str, Any]:
    """Get real projects data from database with pagination and filters"""
    try:
        db_pool = get_db_pool()

        async with db_pool.acquire() as conn:
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

    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch projects")

@router.get("/projects/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Get specific project details from database"""
    try:
        db_pool = get_db_pool()

        async with db_pool.acquire() as conn:
            # Extract numeric ID from project_id
            try:
                numeric_id = int(project_id.replace("proj-", ""))
            except ValueError:
                raise HTTPException(status_code=404, detail="Project not found")

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

            # Calculate Vantage Score (placeholder)
            vantage_score = 80.0

            # Get similar properties
            similar_properties = await conn.fetch(
                """
                SELECT
                    id,
                    location,
                    property_type,
                    price_aed as price
                FROM dld_transactions
                WHERE location = $1 AND id != $2
                ORDER BY transaction_date DESC
                LIMIT 3
                """,
                project_data['location'], numeric_id
            )

            # Format similar properties
            similar = []
            for prop in similar_properties:
                similar.append({
                    "id": f"proj-{prop['id']:03d}",
                    "name": f"{prop['location']} {prop['property_type']}",
                    "price": prop['price'] or 0
                })

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
                "created_at": project_data['created_at'].isoformat() if project_data['created_at'] else None,
                "amenities": [
                    "Swimming Pool",
                    "Gym",
                    "Concierge",
                    "Parking",
                    "Security"
                ],
                "description": f"Property in {project_data['location']} with {project_data['property_type']} type",
                "floor_plan": f"{project_data['property_type']}-{project_data['area']}sqft",
                "payment_plan": "80/20",
                "maintenance_fee": 12000,
                "similar_properties": similar
            }

            return project

    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch project")

@router.get("/projects/search")
async def search_projects(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Search real projects by name, location, or developer"""
    try:
        db_pool = get_db_pool()

        async with db_pool.acquire() as conn:
            # Search in location, property_type, and developer_name
            search_results = await conn.fetch(
                """
                SELECT
                    id,
                    location,
                    property_type,
                    price_aed as price,
                    developer_name as developer
                FROM dld_transactions
                WHERE
                    location ILIKE $1 OR
                    property_type ILIKE $1 OR
                    developer_name ILIKE $1
                ORDER BY transaction_date DESC
                LIMIT $2
                """,
                f"%{q}%", limit
            )

            # Format results
            results = []
            for result in search_results:
                vantage_score = 80.0  # Placeholder

                results.append({
                    "id": f"proj-{result['id']:03d}",
                    "name": f"{result['location']} {result['property_type']}",
                    "location": result['location'] or "Unknown",
                    "property_type": result['property_type'] or "Unknown",
                    "price": result['price'] or 0,
                    "vantage_score": vantage_score
                })

            return {
                "results": results,
                "total": len(results),
                "query": q
            }

    except Exception as e:
        logger.error(f"Error searching projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to search projects")
