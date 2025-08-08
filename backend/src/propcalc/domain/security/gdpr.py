"""GDPR compliance module.

This module provides a very small in-memory style GDPR manager that is
initialised with a Redis client.  The implementation is intentionally
minimal – it only demonstrates how a manager instance can be created and
retrieved by other parts of the application.  Real GDPR handling logic
should replace these placeholders in production.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class GDPRManager:
    """Simple GDPR manager backed by Redis.

    The manager offers very small helper methods that interact with Redis
    using a ``gdpr:user:<id>`` key pattern.  In a full implementation these
    methods would include proper data modelling, validation and auditing.
    """

    def __init__(self, redis_client):
        self._redis = redis_client

    # ------------------------------------------------------------------
    # User data helpers
    # ------------------------------------------------------------------
    def get_user_data(self, user_id: str) -> Dict[str, Any] | None:
        """Retrieve stored user data.

        Returns a dictionary of values if the user exists or ``None`` if
        no data is found or an error occurs.
        """

        try:
            data = self._redis.hgetall(f"gdpr:user:{user_id}")
            return data or None
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to get GDPR user data: %s", exc)
            return None

    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a user.

        The method returns ``True`` if at least one key was removed.
        """

        try:
            return bool(self._redis.delete(f"gdpr:user:{user_id}"))
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to delete GDPR user data: %s", exc)
            return False

    def get_gdpr_report(self) -> Dict[str, Any]:
        """Return a minimal GDPR report.

        The report currently contains only the number of stored users.  It
        serves as a placeholder for more detailed compliance reporting.
        """

        try:
            keys = self._redis.keys("gdpr:user:*")
            return {"total_users": len(keys)}
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to generate GDPR report: %s", exc)
            return {"error": str(exc)}


# Global GDPR manager instance
_gdpr_manager: GDPRManager | None = None


def init_gdpr_manager(redis_client) -> None:
    """Initialise the global GDPR manager.

    Parameters
    ----------
    redis_client:
        Redis client used for all GDPR related storage operations.
    """

    global _gdpr_manager
    _gdpr_manager = GDPRManager(redis_client)
    logger.info("GDPR manager initialized")


def get_gdpr_manager() -> GDPRManager:
    """Return the global GDPR manager instance.

    Raises
    ------
    RuntimeError
        If the GDPR manager has not been initialised.
    """

    if _gdpr_manager is None:
        raise RuntimeError("GDPR manager is not initialized")
    return _gdpr_manager

