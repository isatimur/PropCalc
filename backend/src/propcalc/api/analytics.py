import logging

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from ..core.ai_workers.enhanced_scoring import (
    calculate_enhanced_vantage_score,
    get_feature_importance,
    get_prediction_confidence,
)
from ..core.ai_workers.scoring_logic import calculate_vantage_score
from ..core.metrics import track_request_metrics
from ..infrastructure.database.postgres_db import get_db_instance

router = APIRouter()
logger = logging.getLogger(__name__)
USE_POSTGRES = True

@router.get("/api/v1/analytics/vantage-scores")
async def get_top_performers(limit: int = Query(5, ge=1, le=20)):
    """Get top performing projects by vantage score"""
    try:
        db = await get_db_instance()
        performers = await db.get_top_performers(limit)

        return performers
    except Exception as e:
        logger.error(f"Error fetching top performers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch top performers")

@router.get("/api/v1/projects/{project_id}/vantage-score")
async def get_vantage_score(project_id: int):
    """Get vantage score for a specific project"""
    try:
        # Get project data
        db = await get_db_instance()
        project = await db.get_project_by_id(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Calculate vantage score
        vantage_score = calculate_vantage_score(project)

        # Enhanced scoring if available
        try:
            enhanced_score = calculate_enhanced_vantage_score(project)
            confidence = get_prediction_confidence(project)
            feature_importance = get_feature_importance(project)
        except Exception as e:
            logger.warning(f"Enhanced scoring failed for project {project_id}: {e}")
            enhanced_score = vantage_score
            confidence = 0.8
            feature_importance = {}

        return {
            "vantage_score": enhanced_score,
            "score_breakdown": {
                "developer_score": project.get("developer_score", 0),
                "location_score": project.get("location_score", 0),
                "project_quality_score": project.get("project_quality_score", 0),
                "market_sentiment_score": project.get("market_sentiment_score", 0)
            },
            "risk_assessment": "Low" if enhanced_score > 70 else "Medium" if enhanced_score > 50 else "High",
            "recommendation": "Strong Buy" if enhanced_score > 80 else "Buy" if enhanced_score > 60 else "Hold" if enhanced_score > 40 else "Sell",
            "key_factors": list(feature_importance.keys())[:5] if feature_importance else ["Developer track record", "Location", "Project quality"],
            "confidence": confidence
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating vantage score for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate vantage score")

@router.post("/api/v1/dld/upload")
async def upload_dld_transactions(file: UploadFile = File(...)):
    """Upload DLD transaction data"""
    try:
        track_request_metrics("upload_dld_transactions")

        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # Validate required columns
        required_columns = ['transaction_id', 'property_type', 'location', 'transaction_date', 'price_aed', 'area_sqft']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")

        # Process transactions
        transactions_processed = 0
        if USE_POSTGRES:
            with postgres_db.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    for _, row in df.iterrows():
                        try:
                            cursor.execute("""
                                INSERT INTO dld_transactions (
                                    transaction_id, property_type, location, transaction_date,
                                    price_aed, area_sqft, developer_name
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (transaction_id) DO NOTHING
                            """, (
                                str(row['transaction_id']),
                                row['property_type'],
                                row['location'],
                                pd.to_datetime(row['transaction_date']).date(),
                                float(row['price_aed']),
                                float(row['area_sqft']),
                                row.get('developer_name')
                            ))
                            transactions_processed += 1
                        except Exception as e:
                            logger.warning(f"Error processing transaction {row['transaction_id']}: {e}")
                            continue
                    conn.commit()
        else:
            transactions_processed = await postgres_db.upload_dld_transactions(df)

        return {
            "message": "DLD transactions uploaded successfully",
            "transactions_processed": transactions_processed,
            "total_transactions": len(df)
        }

    except Exception as e:
        logger.error(f"Error uploading DLD transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
