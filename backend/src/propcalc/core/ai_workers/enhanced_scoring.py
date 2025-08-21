"""
Enhanced Vantage Score calculation with ML
"""

import logging
from typing import Any

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# Global model and scaler
_model = None
_scaler = None

def calculate_enhanced_vantage_score(project_data: dict[str, Any]) -> tuple[float, float]:
    """Calculate enhanced Vantage Score using ML"""
    global _model, _scaler

    if _model is None:
        # Initialize model if not exists
        _model = RandomForestRegressor(n_estimators=100, random_state=42)
        _scaler = StandardScaler()
        logger.info("Enhanced Vantage Score model initialized")
        
        # Train model with dummy data for now (in production, this would be real training data)
        dummy_features = [
            [1000000, 1000, 80, 75, 0.05, 85, 70, 80, 75, 70],  # High-end property
            [500000, 800, 60, 65, 0.02, 70, 60, 65, 60, 55],     # Mid-range property
            [200000, 500, 40, 55, -0.01, 55, 50, 55, 50, 45],    # Affordable property
            [800000, 1200, 70, 70, 0.03, 75, 65, 70, 65, 60],   # Good property
            [300000, 600, 45, 60, 0.01, 60, 55, 60, 55, 50],    # Average property
        ]
        dummy_scores = [95, 75, 45, 80, 55]  # Corresponding scores
        
        # Fit scaler and transform features
        features_scaled = _scaler.fit_transform(dummy_features)
        
        # Train model
        _model.fit(features_scaled, dummy_scores)
        logger.info("Enhanced Vantage Score model trained with dummy data")

    try:
        # Extract features
        features = extract_features(project_data)

        # Scale features (use transform, not fit_transform)
        features_scaled = _scaler.transform([features])

        # Make prediction
        score = _model.predict(features_scaled)[0]

        # Ensure score is within reasonable bounds
        score = max(0, min(100, score))

        # Calculate confidence
        confidence = get_prediction_confidence(project_data)

        return float(score), float(confidence)
    except Exception as e:
        logger.error(f"Error calculating enhanced Vantage Score: {e}")
        return 50.0, 0.5  # Default score and confidence

def get_prediction_confidence(project_data: dict[str, Any]) -> float:
    """Get prediction confidence for Vantage Score"""
    try:
        # Simple confidence calculation based on data quality
        features = extract_features(project_data)
        missing_features = sum(1 for f in features if f is None or f == 0)
        total_features = len(features)

        confidence = max(0.1, 1.0 - (missing_features / total_features))
        return float(confidence)
    except Exception as e:
        logger.error(f"Error calculating prediction confidence: {e}")
        return 0.5  # Default confidence

def get_feature_importance() -> dict[str, float]:
    """Get feature importance for Vantage Score model"""
    if _model is None:
        return {}

    try:
        feature_names = [
            'price', 'area', 'location_score', 'developer_score',
            'market_trend', 'completion_date', 'property_type',
            'amenities_score', 'transport_score', 'school_score'
        ]

        importance = _model.feature_importances_ if hasattr(_model, 'feature_importances_') else []

        return dict(zip(feature_names, importance, strict=False))
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        return {}

def extract_features(project_data: dict[str, Any]) -> list[float]:
    """Extract features from project data"""
    features = []

    # Basic features
    features.append(float(project_data.get('price', 0)))
    features.append(float(project_data.get('area', 0)))
    features.append(float(project_data.get('location_score', 0)))
    features.append(float(project_data.get('developer_score', 0)))
    features.append(float(project_data.get('market_trend', 0)))
    features.append(float(project_data.get('completion_date_score', 0)))
    features.append(float(project_data.get('property_type_score', 0)))
    features.append(float(project_data.get('amenities_score', 0)))
    features.append(float(project_data.get('transport_score', 0)))
    features.append(float(project_data.get('school_score', 0)))

    return features
