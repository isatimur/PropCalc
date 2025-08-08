"""
Advanced Vantage Score™ Implementation with ML/AI
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """ML model types for Vantage Score"""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"
    NEURAL_NETWORK = "neural_network"

class FeatureImportance(Enum):
    """Feature importance categories"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class VantageScoreResult:
    """Vantage Score calculation result"""
    score: float
    confidence: float
    risk_level: str
    recommendation: str
    feature_contributions: dict[str, float]
    model_version: str
    prediction_timestamp: datetime
    data_quality_score: float
    model_accuracy: float

@dataclass
class ModelPerformance:
    """Model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    mae: float
    r2_score: float
    cross_val_score: float
    training_time: float
    prediction_latency: float

class EnhancedVantageScore:
    """
    Advanced Vantage Score™ implementation with ML/AI capabilities
    """

    def __init__(self, model_type: ModelType = ModelType.ENSEMBLE):
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        self.last_training = None
        self.model_version = "2.0.0"

        # Feature engineering
        self.feature_columns = [
            'price_aed', 'area_sqft', 'price_per_sqft',
            'bedrooms', 'bathrooms', 'parking_spaces',
            'floor_number', 'days_since_transaction',
            'developer_reputation_score', 'location_score',
            'property_type_score', 'market_sentiment_score',
            'amenities_score', 'view_score', 'maintenance_score'
        ]

        # Target variable
        self.target_column = 'vantage_score'

        # Initialize models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models"""
        if self.model_type == ModelType.RANDOM_FOREST:
            self.models['primary'] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == ModelType.GRADIENT_BOOSTING:
            self.models['primary'] = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        elif self.model_type == ModelType.ENSEMBLE:
            self.models['random_forest'] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.models['gradient_boosting'] = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )

        # Initialize scalers and encoders
        self.scalers['features'] = StandardScaler()
        self.label_encoders['developer'] = LabelEncoder()
        self.label_encoders['location'] = LabelEncoder()
        self.label_encoders['property_type'] = LabelEncoder()

    def _engineer_features(self, transactions: list[dict]) -> pd.DataFrame:
        """Engineer features from transaction data"""
        df = pd.DataFrame(transactions)

        # Basic features
        df['price_per_sqft'] = df['price_aed'] / df['area_sqft']
        df['days_since_transaction'] = (datetime.now() - pd.to_datetime(df['transaction_date'])).dt.days

        # Developer reputation score (placeholder - would be calculated from historical data)
        df['developer_reputation_score'] = self._calculate_developer_score(df['developer_name'])

        # Location score (placeholder - would be calculated from market data)
        df['location_score'] = self._calculate_location_score(df['location'])

        # Property type score
        df['property_type_score'] = self._calculate_property_type_score(df['property_type'])

        # Market sentiment score (placeholder)
        df['market_sentiment_score'] = self._calculate_market_sentiment(df)

        # Amenities score
        df['amenities_score'] = self._calculate_amenities_score(df)

        # View score
        df['view_score'] = self._calculate_view_score(df['view'])

        # Maintenance score (placeholder)
        df['maintenance_score'] = self._calculate_maintenance_score(df)

        # Encode categorical variables
        for col in ['developer_name', 'location', 'property_type']:
            if col in df.columns:
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].fillna('Unknown'))

        return df

    def _calculate_developer_score(self, developer_names: pd.Series) -> pd.Series:
        """Calculate developer reputation score"""
        # Placeholder implementation - would use historical data
        developer_scores = {
            'Emaar Properties': 9.5,
            'Nakheel': 8.8,
            'Meraas': 8.2,
            'Dubai Properties': 8.0,
            'Sobha': 7.8
        }

        return developer_names.map(developer_scores).fillna(7.0)

    def _calculate_location_score(self, locations: pd.Series) -> pd.Series:
        """Calculate location desirability score"""
        # Placeholder implementation - would use market data
        location_scores = {
            'Dubai Marina': 9.2,
            'Palm Jumeirah': 9.0,
            'Downtown Dubai': 8.8,
            'Business Bay': 8.5,
            'Dubai Hills Estate': 8.3,
            'Jumeirah Beach Residence': 8.7,
            'Dubai Silicon Oasis': 7.5,
            'Dubai Sports City': 7.8
        }

        return locations.map(location_scores).fillna(7.0)

    def _calculate_property_type_score(self, property_types: pd.Series) -> pd.Series:
        """Calculate property type score"""
        property_scores = {
            'Apartment': 8.0,
            'Villa': 9.0,
            'Townhouse': 8.5,
            'Penthouse': 9.5,
            'Office': 7.5,
            'Retail': 7.0
        }

        return property_types.map(property_scores).fillna(7.5)

    def _calculate_market_sentiment(self, df: pd.DataFrame) -> pd.Series:
        """Calculate market sentiment score"""
        # Placeholder - would use market indicators
        return pd.Series([8.0] * len(df))

    def _calculate_amenities_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate amenities score"""
        # Placeholder - would calculate based on nearby amenities
        return pd.Series([7.5] * len(df))

    def _calculate_view_score(self, views: pd.Series) -> pd.Series:
        """Calculate view score"""
        view_scores = {
            'Sea View': 9.0,
            'Marina View': 8.5,
            'City View': 7.5,
            'Garden View': 7.0,
            'Street View': 6.0
        }

        return views.map(view_scores).fillna(7.0)

    def _calculate_maintenance_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate maintenance score"""
        # Placeholder - would use building age and maintenance history
        return pd.Series([8.0] * len(df))

    def _generate_vantage_scores(self, df: pd.DataFrame) -> pd.Series:
        """Generate Vantage Scores for training data"""
        # Complex scoring algorithm
        base_score = 50.0

        # Price factor (20% weight)
        price_factor = np.clip(df['price_per_sqft'] / 2000, 0.5, 2.0)

        # Location factor (25% weight)
        location_factor = df['location_score'] / 10.0

        # Developer factor (15% weight)
        developer_factor = df['developer_reputation_score'] / 10.0

        # Property type factor (10% weight)
        property_factor = df['property_type_score'] / 10.0

        # Amenities factor (10% weight)
        amenities_factor = df['amenities_score'] / 10.0

        # Market sentiment factor (10% weight)
        sentiment_factor = df['market_sentiment_score'] / 10.0

        # View factor (5% weight)
        view_factor = df['view_score'] / 10.0

        # Maintenance factor (5% weight)
        maintenance_factor = df['maintenance_score'] / 10.0

        # Calculate weighted score
        vantage_score = (
            base_score +
            (price_factor * 20) +
            (location_factor * 25) +
            (developer_factor * 15) +
            (property_factor * 10) +
            (amenities_factor * 10) +
            (sentiment_factor * 10) +
            (view_factor * 5) +
            (maintenance_factor * 5)
        )

        # Normalize to 0-100 range
        vantage_score = np.clip(vantage_score, 0, 100)

        return vantage_score

    async def train_model(self, transactions: list[dict]) -> ModelPerformance:
        """Train the Vantage Score model"""
        logger.info("Starting Vantage Score model training...")
        start_time = datetime.now()

        try:
            # Engineer features
            df = self._engineer_features(transactions)

            # Generate Vantage Scores for training
            df[self.target_column] = self._generate_vantage_scores(df)

            # Prepare features
            feature_cols = [col for col in self.feature_columns if col in df.columns]
            X = df[feature_cols].fillna(0)
            y = df[self.target_column]

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            X_train_scaled = self.scalers['features'].fit_transform(X_train)
            X_test_scaled = self.scalers['features'].transform(X_test)

            # Train models
            if self.model_type == ModelType.ENSEMBLE:
                for name, model in self.models.items():
                    logger.info(f"Training {name} model...")
                    model.fit(X_train_scaled, y_train)

                    # Make predictions
                    y_pred = model.predict(X_test_scaled)

                    # Calculate performance metrics
                    performance = self._calculate_performance_metrics(y_test, y_pred)
                    self.model_performance[name] = performance

                    # Feature importance
                    if hasattr(model, 'feature_importances_'):
                        self.feature_importance[name] = dict(zip(feature_cols, model.feature_importances_, strict=False))
            else:
                model = self.models['primary']
                model.fit(X_train_scaled, y_train)

                y_pred = model.predict(X_test_scaled)
                performance = self._calculate_performance_metrics(y_test, y_pred)
                self.model_performance['primary'] = performance

                if hasattr(model, 'feature_importances_'):
                    self.feature_importance['primary'] = dict(zip(feature_cols, model.feature_importances_, strict=False))

            # Cross-validation
            cv_scores = cross_val_score(
                self.models['primary'] if self.model_type != ModelType.ENSEMBLE else self.models['random_forest'],
                X_train_scaled, y_train, cv=5, scoring='r2'
            )

            # Update performance with cross-validation
            if self.model_type == ModelType.ENSEMBLE:
                self.model_performance['random_forest'].cross_val_score = cv_scores.mean()
            else:
                self.model_performance['primary'].cross_val_score = cv_scores.mean()

            # Save models
            await self._save_models()

            training_time = (datetime.now() - start_time).total_seconds()

            # Update last training timestamp
            self.last_training = datetime.now()

            logger.info(f"Model training completed in {training_time:.2f} seconds")

            return self.model_performance['primary'] if self.model_type != ModelType.ENSEMBLE else self.model_performance['random_forest']

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise

    def _calculate_performance_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> ModelPerformance:
        """Calculate model performance metrics"""
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Calculate accuracy (within 5 points)
        accuracy = np.mean(np.abs(y_true - y_pred) <= 5)

        # Calculate precision and recall (for classification-like metrics)
        # Convert to classification problem: high score = good investment
        y_true_binary = (y_true >= 70).astype(int)
        y_pred_binary = (y_pred >= 70).astype(int)

        tp = np.sum((y_true_binary == 1) & (y_pred_binary == 1))
        fp = np.sum((y_true_binary == 0) & (y_pred_binary == 1))
        fn = np.sum((y_true_binary == 1) & (y_pred_binary == 0))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return ModelPerformance(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            mse=mse,
            mae=mae,
            r2_score=r2,
            cross_val_score=0.0,  # Will be updated later
            training_time=0.0,
            prediction_latency=0.0
        )

    async def predict_vantage_score(self, transaction: dict) -> VantageScoreResult:
        """Predict Vantage Score for a single transaction"""
        start_time = datetime.now()

        try:
            # Engineer features for single transaction
            df = self._engineer_features([transaction])

            # Prepare features
            feature_cols = [col for col in self.feature_columns if col in df.columns]
            X = df[feature_cols].fillna(0)

            # Scale features
            X_scaled = self.scalers['features'].transform(X)

            # Make predictions
            if self.model_type == ModelType.ENSEMBLE:
                predictions = []
                for _name, model in self.models.items():
                    pred = model.predict(X_scaled)[0]
                    predictions.append(pred)

                # Ensemble prediction (weighted average)
                score = np.mean(predictions)
                confidence = 1.0 - np.std(predictions) / 100.0  # Higher std = lower confidence
            else:
                model = self.models['primary']
                score = model.predict(X_scaled)[0]
                confidence = 0.85  # Placeholder confidence

            # Calculate feature contributions
            feature_contributions = self._calculate_feature_contributions(X_scaled[0], feature_cols)

            # Determine risk level
            risk_level = self._determine_risk_level(score, confidence)

            # Generate recommendation
            recommendation = self._generate_recommendation(score, risk_level)

            # Calculate prediction latency
            prediction_latency = (datetime.now() - start_time).total_seconds()

            # Update model performance
            if self.model_performance:
                primary_model = list(self.model_performance.keys())[0]
                self.model_performance[primary_model].prediction_latency = prediction_latency

            return VantageScoreResult(
                score=float(score),
                confidence=float(confidence),
                risk_level=risk_level,
                recommendation=recommendation,
                feature_contributions=feature_contributions,
                model_version=self.model_version,
                prediction_timestamp=datetime.now(),
                data_quality_score=95.0,  # Placeholder
                model_accuracy=self.model_performance[primary_model].accuracy if self.model_performance else 0.0
            )

        except Exception as e:
            logger.error(f"Vantage Score prediction failed: {e}")
            raise

    def _calculate_feature_contributions(self, X_scaled: np.ndarray, feature_cols: list[str]) -> dict[str, float]:
        """Calculate feature contributions to the prediction"""
        if not self.feature_importance:
            return {}

        primary_model = list(self.feature_importance.keys())[0]
        importance = self.feature_importance[primary_model]

        # Normalize importance scores
        total_importance = sum(importance.values())
        if total_importance > 0:
            normalized_importance = {k: v / total_importance for k, v in importance.items()}
        else:
            normalized_importance = {k: 0.0 for k in importance.keys()}

        return normalized_importance

    def _determine_risk_level(self, score: float, confidence: float) -> str:
        """Determine risk level based on score and confidence"""
        if score >= 80 and confidence >= 0.8:
            return "LOW"
        elif score >= 70 and confidence >= 0.7:
            return "MEDIUM"
        elif score >= 60 and confidence >= 0.6:
            return "MODERATE"
        else:
            return "HIGH"

    def _generate_recommendation(self, score: float, risk_level: str) -> str:
        """Generate investment recommendation"""
        if score >= 85:
            return "STRONG BUY - Excellent investment opportunity with high potential returns"
        elif score >= 75:
            return "BUY - Good investment with solid fundamentals"
        elif score >= 65:
            return "HOLD - Moderate investment, consider market conditions"
        elif score >= 55:
            return "CAUTION - Higher risk, thorough due diligence recommended"
        else:
            return "AVOID - High risk investment, not recommended"

    async def _save_models(self):
        """Save trained models to disk"""
        try:
            models_dir = "models"
            os.makedirs(models_dir, exist_ok=True)

            # Save models
            for name, model in self.models.items():
                joblib.dump(model, f"{models_dir}/{name}_model.pkl")

            # Save scalers
            for name, scaler in self.scalers.items():
                joblib.dump(scaler, f"{models_dir}/{name}_scaler.pkl")

            # Save encoders
            for name, encoder in self.label_encoders.items():
                joblib.dump(encoder, f"{models_dir}/{name}_encoder.pkl")

            # Save metadata
            metadata = {
                'model_version': self.model_version,
                'model_type': self.model_type.value,
                'last_training': self.last_training.isoformat() if self.last_training else None,
                'feature_importance': self.feature_importance,
                'model_performance': {
                    name: {
                        'accuracy': perf.accuracy,
                        'precision': perf.precision,
                        'recall': perf.recall,
                        'f1_score': perf.f1_score,
                        'mse': perf.mse,
                        'mae': perf.mae,
                        'r2_score': perf.r2_score,
                        'cross_val_score': perf.cross_val_score
                    }
                    for name, perf in self.model_performance.items()
                }
            }

            with open(f"{models_dir}/metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info("Models saved successfully")

        except Exception as e:
            logger.error(f"Failed to save models: {e}")
            raise

    async def load_models(self):
        """Load trained models from disk"""
        try:
            models_dir = "models"

            # Load models
            for name in self.models.keys():
                model_path = f"{models_dir}/{name}_model.pkl"
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)

            # Load scalers
            for name in self.scalers.keys():
                scaler_path = f"{models_dir}/{name}_scaler.pkl"
                if os.path.exists(scaler_path):
                    self.scalers[name] = joblib.load(scaler_path)

            # Load encoders
            for name in self.label_encoders.keys():
                encoder_path = f"{models_dir}/{name}_encoder.pkl"
                if os.path.exists(encoder_path):
                    self.label_encoders[name] = joblib.load(encoder_path)

            # Load metadata
            metadata_path = f"{models_dir}/metadata.json"
            if os.path.exists(metadata_path):
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    self.model_version = metadata.get('model_version', self.model_version)
                    self.last_training = datetime.fromisoformat(metadata['last_training']) if metadata.get('last_training') else None
                    self.feature_importance = metadata.get('feature_importance', {})

            logger.info("Models loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise

    def get_model_status(self) -> dict[str, Any]:
        """Get current model status"""
        return {
            'model_type': self.model_type.value,
            'model_version': self.model_version,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'models_trained': len(self.models),
            'performance_metrics': {
                name: {
                    'accuracy': perf.accuracy,
                    'precision': perf.precision,
                    'recall': perf.recall,
                    'f1_score': perf.f1_score,
                    'r2_score': perf.r2_score,
                    'cross_val_score': perf.cross_val_score
                }
                for name, perf in self.model_performance.items()
            },
            'feature_importance': self.feature_importance
        }
