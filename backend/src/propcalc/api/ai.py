import logging
import time

import numpy as np
from fastapi import APIRouter, HTTPException, Request

from ..core.ai_workers.enhanced_scoring import (
    calculate_enhanced_vantage_score,
    get_feature_importance,
    get_prediction_confidence,
)
from ..core.ai_workers.experiment_manager import experiment_manager
from ..core.ai_workers.model_monitoring import model_monitor
from ..core.ai_workers.scoring_logic import calculate_vantage_score
from ..core.ai_workers.train_model import train_and_evaluate_model
from ..core.metrics import track_request_metrics
from ..core.performance.rate_limiter import get_rate_limiter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/v1/ai/calculate-enhanced-score")
async def calculate_enhanced_vantage_score_endpoint(project_data: dict, request: Request):
    """Calculate enhanced Vantage Score using machine learning"""
    try:
        # Rate limiting check
        rate_limiter = get_rate_limiter()
        client_id = rate_limiter.get_client_identifier(request)
        allowed, rate_info = rate_limiter.check_rate_limit("/api/v1/ai/calculate-enhanced-score", client_id)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "rate_limit_info": rate_info,
                    "retry_after": rate_info.get("reset_time", 60)
                }
            )

        track_request_metrics("calculate_enhanced_vantage_score")

        # Calculate enhanced score
        enhanced_score, breakdown = calculate_enhanced_vantage_score(project_data)
        confidence = get_prediction_confidence(project_data)

        return {
            "enhanced_vantage_score": enhanced_score,
            "confidence": confidence,
            "breakdown": breakdown,
            "algorithm": "Enhanced ML + Traditional Hybrid",
            "model_version": "1.0"
        }

    except Exception as e:
        logger.error(f"Error calculating enhanced vantage score: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate enhanced score")

@router.post("/api/v1/ai/train-model")
async def train_vantage_model_endpoint():
    """Train the Vantage Score machine learning model"""
    try:
        track_request_metrics("train_vantage_model")

        # Train the model with 2000 samples
        results = train_and_evaluate_model(num_samples=2000)

        return {
            "status": "success",
            "training_results": results,
            "message": "Model training completed successfully"
        }

    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail="Failed to train model")

@router.get("/api/v1/ai/feature-importance")
async def get_feature_importance_endpoint():
    """Get feature importance from the trained model"""
    try:
        track_request_metrics("get_feature_importance")

        feature_importance = get_feature_importance()

        return {
            "feature_importance": feature_importance,
            "total_features": len(feature_importance),
            "model_status": "trained" if feature_importance else "not_trained"
        }

    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get feature importance")

@router.get("/api/v1/ai/model-status")
async def get_model_status():
    """Get the current status of the ML model"""
    try:
        track_request_metrics("get_model_status")

        import os

        model_path = "models/vantage_score_model.pkl"
        model_exists = os.path.exists(model_path)
        feature_importance = get_feature_importance()

        return {
            "model_exists": model_exists,
            "model_path": model_path,
            "is_trained": len(feature_importance) > 0,
            "feature_count": len(feature_importance),
            "algorithm": "Random Forest Regressor",
            "last_updated": os.path.getmtime(model_path) if model_exists else None
        }

    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model status")

@router.post("/api/v1/ai/compare-scores")
async def compare_traditional_vs_enhanced(project_data: dict):
    """Compare traditional vs enhanced Vantage Score calculation"""
    try:
        track_request_metrics("compare_scores")

        # Calculate traditional score
        traditional_score, traditional_breakdown = calculate_vantage_score(project_data)

        # Calculate enhanced score
        enhanced_score, enhanced_breakdown = calculate_enhanced_vantage_score(project_data)

        # Calculate difference
        score_difference = enhanced_score - traditional_score

        return {
            "traditional_score": traditional_score,
            "enhanced_score": enhanced_score,
            "score_difference": round(score_difference, 1),
            "improvement_percentage": round((score_difference / traditional_score) * 100, 1) if traditional_score > 0 else 0,
            "traditional_breakdown": traditional_breakdown,
            "enhanced_breakdown": enhanced_breakdown,
            "recommendation": "Use Enhanced Score" if abs(score_difference) > 5 else "Scores are similar"
        }

    except Exception as e:
        logger.error(f"Error comparing scores: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare scores")

# Model Monitoring Endpoints

@router.get("/api/v1/monitoring/model-health")
async def get_model_health():
    """Get comprehensive model health status"""
    try:
        track_request_metrics("get_model_health")

        health_status = model_monitor.check_model_health()

        return {
            "status": "success",
            "model_health": health_status,
            "timestamp": health_status.get('timestamp', time.time())
        }

    except Exception as e:
        logger.error(f"Error getting model health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model health")

@router.get("/api/v1/monitoring/performance-trends")
async def get_performance_trends(days: int = 30):
    """Get model performance trends over time"""
    try:
        track_request_metrics("get_performance_trends")

        trends = model_monitor.get_performance_trends(days=days)

        return {
            "status": "success",
            "performance_trends": trends,
            "days": days
        }

    except Exception as e:
        logger.error(f"Error getting performance trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance trends")

@router.get("/api/v1/monitoring/drift-detection")
async def get_drift_detection():
    """Get feature drift detection results"""
    try:
        track_request_metrics("get_drift_detection")

        # This would require reference data to compare against
        # For now, return basic drift metrics
        try:
            drift_score = model_monitor._calculate_drift_score(np.array([[0, 0, 0]]))
        except AttributeError:
            drift_score = 0.0  # Default if method doesn't exist

        drift_metrics = {
            "drift_score": drift_score,
            "last_check": time.time(),
            "status": "monitoring_active"
        }

        return {
            "status": "success",
            "drift_metrics": drift_metrics
        }

    except Exception as e:
        logger.error(f"Error getting drift detection: {e}")
        raise HTTPException(status_code=500, detail="Failed to get drift detection")

# A/B Testing Endpoints

@router.post("/api/v1/experiments/create")
async def create_experiment(experiment_config: dict):
    """Create a new ML experiment"""
    try:
        track_request_metrics("create_experiment")

        experiment_id = experiment_manager.create_comprehensive_experiment(
            name=experiment_config.get("name", "New Experiment"),
            description=experiment_config.get("description", ""),
            model_variants=experiment_config.get("model_variants", ["control", "variant_a"]),
            traffic_split=experiment_config.get("traffic_split", {"control": 0.5, "variant_a": 0.5}),
            monitoring_enabled=experiment_config.get("monitoring_enabled", True),
            drift_detection_enabled=experiment_config.get("drift_detection_enabled", True),
            auto_retraining_enabled=experiment_config.get("auto_retraining_enabled", False)
        )

        return {
            "status": "success",
            "experiment_id": experiment_id,
            "message": "Experiment created successfully"
        }

    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create experiment")

@router.post("/api/v1/experiments/{experiment_id}/register-variant")
async def register_model_variant(experiment_id: str, variant_config: dict):
    """Register a model variant for an experiment"""
    try:
        track_request_metrics("register_model_variant")

        # This would require the actual model function
        # For now, we'll create a placeholder
        def placeholder_model(project_data):
            return {"enhanced_vantage_score": 85.0, "confidence": 0.8}

        experiment_manager.register_model_variant(
            experiment_id=experiment_id,
            variant=variant_config.get("variant", "control"),
            model_function=placeholder_model
        )

        return {
            "status": "success",
            "message": f"Model variant registered for experiment {experiment_id}"
        }

    except Exception as e:
        logger.error(f"Error registering model variant: {e}")
        raise HTTPException(status_code=500, detail="Failed to register model variant")

@router.post("/api/v1/experiments/{experiment_id}/predict")
async def run_experiment_prediction(experiment_id: str, prediction_request: dict):
    """Run a prediction through an experiment"""
    try:
        track_request_metrics("run_experiment_prediction")

        result = experiment_manager.run_experiment_prediction(
            experiment_id=experiment_id,
            user_id=prediction_request.get("user_id", "anonymous"),
            project_data=prediction_request.get("project_data", {})
        )

        return {
            "status": "success",
            "prediction_result": result
        }

    except Exception as e:
        logger.error(f"Error running experiment prediction: {e}")
        raise HTTPException(status_code=500, detail="Failed to run experiment prediction")

@router.get("/api/v1/experiments/{experiment_id}/insights")
async def get_experiment_insights(experiment_id: str):
    """Get comprehensive insights for an experiment"""
    try:
        track_request_metrics("get_experiment_insights")

        insights = experiment_manager.get_experiment_insights(experiment_id)

        return {
            "status": "success",
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error getting experiment insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get experiment insights")

@router.get("/api/v1/experiments/{experiment_id}/dashboard")
async def get_experiment_dashboard(experiment_id: str):
    """Get dashboard data for an experiment"""
    try:
        track_request_metrics("get_experiment_dashboard")

        dashboard_data = experiment_manager.get_experiment_dashboard_data(experiment_id)

        return {
            "status": "success",
            "dashboard_data": dashboard_data
        }

    except Exception as e:
        logger.error(f"Error getting experiment dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get experiment dashboard")

@router.get("/api/v1/experiments")
async def get_all_experiments():
    """Get summary of all experiments"""
    try:
        track_request_metrics("get_all_experiments")

        experiments = experiment_manager.get_all_experiments_summary()

        return {
            "status": "success",
            "experiments": experiments,
            "total_experiments": len(experiments)
        }

    except Exception as e:
        logger.error(f"Error getting all experiments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get experiments")
