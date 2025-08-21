"""AI workers module (imports are guarded to avoid heavy deps at import time)."""

from typing import Any, Dict

# Safe import: lightweight
from .scoring_logic import calculate_vantage_score, VantageScoringEngine

# Guard heavy optional ML dependencies
try:  # pragma: no cover
    from .enhanced_scoring import (
        calculate_enhanced_vantage_score,
        get_feature_importance,
        get_prediction_confidence,
    )
except Exception:  # Provide graceful fallbacks if sklearn is missing
    def calculate_enhanced_vantage_score(project_data: Dict[str, Any]) -> tuple[float, float]:  # type: ignore
        score = float(calculate_vantage_score(project_data))
        return score, 0.8  # Return tuple with score and default confidence

    def get_feature_importance() -> Dict[str, float]:  # type: ignore
        return {}

    def get_prediction_confidence(project_data: Dict[str, Any]) -> float:  # type: ignore
        return 0.8

# Additional utilities (guard in case optional tooling missing)
try:  # pragma: no cover
    from .experiment_manager import experiment_manager
except Exception:
    experiment_manager = None  # type: ignore

try:  # pragma: no cover
    from .model_monitoring import model_monitor
except Exception:
    model_monitor = None  # type: ignore

try:  # pragma: no cover
    from .train_model import train_and_evaluate_model
except Exception:
    def train_and_evaluate_model(*_args, **_kwargs):  # type: ignore
        return None

__all__ = [
    'calculate_enhanced_vantage_score',
    'get_prediction_confidence',
    'get_feature_importance',
    'calculate_vantage_score',
    'VantageScoringEngine',
    'train_and_evaluate_model',
    'model_monitor',
    'experiment_manager'
]
