"""
Custom exceptions for PropCalc backend.

This module defines all custom exceptions used throughout the application,
providing clear error handling and meaningful error messages.
"""

from typing import Any


class PropCalcException(Exception):
    """Base exception for all PropCalc application errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(PropCalcException):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None
    ) -> None:
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class NotFoundError(PropCalcException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, "NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class AuthenticationError(PropCalcException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(PropCalcException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, "AUTHORIZATION_ERROR")


class DatabaseError(PropCalcException):
    """Raised when database operations fail."""

    def __init__(self, message: str, operation: str | None = None) -> None:
        super().__init__(message, "DATABASE_ERROR")
        self.operation = operation


class CacheError(PropCalcException):
    """Raised when cache operations fail."""

    def __init__(self, message: str, operation: str | None = None) -> None:
        super().__init__(message, "CACHE_ERROR")
        self.operation = operation


class ExternalServiceError(PropCalcException):
    """Raised when external service calls fail."""

    def __init__(
        self,
        message: str,
        service_name: str,
        status_code: int | None = None
    ) -> None:
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name
        self.status_code = status_code


class RateLimitError(PropCalcException):
    """Raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None
    ) -> None:
        super().__init__(message, "RATE_LIMIT_ERROR")
        self.retry_after = retry_after


class ConfigurationError(PropCalcException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None) -> None:
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key


class ModelError(PropCalcException):
    """Raised when ML model operations fail."""

    def __init__(self, message: str, model_name: str | None = None) -> None:
        super().__init__(message, "MODEL_ERROR")
        self.model_name = model_name


class DataProcessingError(PropCalcException):
    """Raised when data processing operations fail."""

    def __init__(self, message: str, processing_step: str | None = None) -> None:
        super().__init__(message, "DATA_PROCESSING_ERROR")
        self.processing_step = processing_step


class DataLoadError(PropCalcException):
    """Raised when data loading operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "DATA_LOAD_ERROR")
