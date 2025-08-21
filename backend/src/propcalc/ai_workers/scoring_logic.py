"""Compatibility shim module for tests expecting `ai_workers.scoring_logic`."""

from ..core.ai_workers.scoring_logic import VantageScoringEngine  # noqa: F401

__all__ = ["VantageScoringEngine"]



