"""
A/B testing and experiment management
"""

import logging
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

class ExperimentManager:
    """A/B testing and experiment management"""

    def __init__(self):
        self.experiments = {}
        self.active_experiments = {}

    def create_experiment(self, config: dict[str, Any]) -> str:
        """Create a new experiment"""
        try:
            experiment_id = str(uuid.uuid4())

            experiment = {
                "id": experiment_id,
                "name": config.get("name", "Default Experiment"),
                "description": config.get("description", ""),
                "variants": config.get("variants", []),
                "traffic_split": config.get("traffic_split", 0.5),
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }

            self.experiments[experiment_id] = experiment
            self.active_experiments[experiment_id] = experiment

            logger.info(f"Created experiment: {experiment_id}")
            return experiment_id

        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            raise

    def get_experiment(self, experiment_id: str) -> dict[str, Any]:
        """Get experiment details"""
        return self.experiments.get(experiment_id, {})

    def get_all_experiments(self) -> list[dict[str, Any]]:
        """Get all experiments"""
        return list(self.experiments.values())

    def run_experiment(self, experiment_id: str, user_id: str) -> dict[str, Any]:
        """Run experiment for a user"""
        try:
            experiment = self.experiments.get(experiment_id)
            if not experiment:
                return {"error": "Experiment not found"}

            # Simple A/B testing logic
            import random
            variant = random.choice(experiment.get("variants", ["control", "treatment"]))

            return {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error running experiment: {e}")
            return {"error": str(e)}

# Global experiment manager instance
experiment_manager = ExperimentManager()
