"""
Logging configuration for PropCalc backend.

This module provides structured logging with different levels and formats
for development and production environments.
"""

import logging
import sys
from datetime import datetime
from typing import Any

try:
    from loguru import logger  # type: ignore
except Exception:  # pragma: no cover - provide fallback if loguru is unavailable
    class _StdLoggerAdapter:
        def __init__(self) -> None:
            self._logger = logging.getLogger("propcalc")
            if not self._logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
                )
                handler.setFormatter(formatter)
                self._logger.addHandler(handler)
                self._logger.setLevel(logging.INFO)

        # Compatibility methods used in this module
        def add(self, *_args, **_kwargs):
            return 0

        def remove(self, *_args, **_kwargs):
            pass

        def bind(self, **_kwargs):
            return self

        def level(self, name):  # noqa: D401
            return type("L", (), {"name": name})

        def opt(self, **_kwargs):
            return self

        # Logging methods
        def info(self, *args, **kwargs):
            self._logger.info(*args, **kwargs)

        def warning(self, *args, **kwargs):
            self._logger.warning(*args, **kwargs)

        def error(self, *args, **kwargs):
            self._logger.error(*args, **kwargs)

        def log(self, _level, message, **_kwargs):
            self._logger.info(message)

    logger = _StdLoggerAdapter()  # type: ignore


class InterceptHandler(logging.Handler):
    """Intercept standard logging and route to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    level: str = "INFO",
    format: str = "json",
    enable_console: bool = True,
    enable_file: bool = False,
    log_file: str = "logs/app.log"
) -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log format (json, text)
        enable_console: Enable console logging
        enable_file: Enable file logging
        log_file: Path to log file
    """
    # Remove default loguru handler
    logger.remove()

    # Configure log format
    if format == "json":
        log_format = (
            "{"
            '"timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level: <8}", '
            '"name": "{name}", '
            '"function": "{function}", '
            '"line": {line}, '
            '"message": "{message}", '
            '"extra": {extra}'
            "}"
        )
    else:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add console handler
    if enable_console:
        logger.add(
            sys.stdout,
            format=log_format,
            level=level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )

    # Add file handler
    if enable_file:
        logger.add(
            log_file,
            format=log_format,
            level=level,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set loguru as the default logger for uvicorn
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True


def get_logger(name: str) -> logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)


def log_request(
    method: str,
    url: str,
    status_code: int,
    duration: float,
    user_id: str | None = None,
    **kwargs: Any
) -> None:
    """
    Log HTTP request details.

    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code
        duration: Request duration in seconds
        user_id: User ID if authenticated
        **kwargs: Additional context
    """
    logger.info(
        "HTTP Request",
        method=method,
        url=url,
        status_code=status_code,
        duration=f"{duration:.3f}s",
        user_id=user_id,
        **kwargs
    )


def log_error(
    error: Exception,
    context: dict[str, Any] | None = None,
    user_id: str | None = None
) -> None:
    """
    Log error with context.

    Args:
        error: Exception to log
        context: Additional context
        user_id: User ID if available
    """
    logger.error(
        "Application Error",
        error_type=type(error).__name__,
        error_message=str(error),
        user_id=user_id,
        context=context or {}
    )


def log_performance(
    operation: str,
    duration: float,
    success: bool = True,
    **kwargs: Any
) -> None:
    """
    Log performance metrics.

    Args:
        operation: Operation name
        duration: Duration in seconds
        success: Whether operation was successful
        **kwargs: Additional metrics
    """
    logger.info(
        "Performance Metric",
        operation=operation,
        duration=f"{duration:.3f}s",
        success=success,
        **kwargs
    )


def log_security_event(
    event_type: str,
    user_id: str | None = None,
    ip_address: str | None = None,
    **kwargs: Any
) -> None:
    """
    Log security events.

    Args:
        event_type: Type of security event
        user_id: User ID if available
        ip_address: IP address
        **kwargs: Additional security context
    """
    logger.warning(
        "Security Event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )
