import logging

from fastapi import APIRouter, HTTPException, Query

from ..core.metrics import track_request_metrics
from ..infrastructure.cache.redis_cache import cache_developers_list
from ..infrastructure.database import postgres_db, simple_db

router = APIRouter()
logger = logging.getLogger(__name__)
USE_POSTGRES = True

@router.get("/api/v1/developers")
async def get_developers(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get developers with pagination"""
    try:
        track_request_metrics("get_developers")

        if USE_POSTGRES:
            with postgres_db.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            id, name, established_year, track_record_score,
                            financial_stability_score, customer_satisfaction_score,
                            completed_projects_count, total_project_value
                        FROM developers
                        WHERE is_active = true
                        ORDER BY track_record_score DESC
                        LIMIT %s OFFSET %s
                    """, (limit, offset))

                    developers = []
                    for row in cursor.fetchall():
                        developers.append({
                            "id": row[0],
                            "name": row[1],
                            "established_year": row[2],
                            "track_record_score": float(row[3]) if row[3] else 0.0,
                            "financial_stability_score": float(row[4]) if row[4] else 0.0,
                            "customer_satisfaction_score": float(row[5]) if row[5] else 0.0,
                            "completed_projects_count": row[6] or 0,
                            "total_project_value": float(row[7]) if row[7] else 0.0
                        })

                    # Cache the developers data
                    result = {"developers": developers, "total": len(developers)}
                    result = cache_developers_list(result)
                    return result
        else:
            return simple_db.get_developers(limit, offset)

    except Exception as e:
        logger.error(f"Error getting developers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/developers/{developer_id}")
async def get_developer(developer_id: int):
    """Get a specific developer by ID"""
    try:
        if USE_POSTGRES:
            developer = postgres_db.get_developer_by_id(developer_id)
        else:
            developer = simple_db.get_developer_by_id(developer_id)

        if not developer:
            raise HTTPException(status_code=404, detail="Developer not found")

        return developer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching developer {developer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch developer")
