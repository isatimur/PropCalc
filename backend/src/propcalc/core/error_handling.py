"""
Comprehensive error handling and logging middleware for PropCalc
"""

import logging
import traceback
import time
from typing import Any, Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from ..domain.models import ErrorResponse

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling for the application"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_validation_error(self, exc: RequestValidationError, request: Request) -> JSONResponse:
        """Handle Pydantic validation errors"""
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        error_response = ErrorResponse(
            error="Validation Error",
            detail="Request data validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            timestamp=time.time(),
            request_id=request.headers.get("X-Request-ID")
        )
        
        self.logger.warning(
            f"Validation error for {request.method} {request.url}: {error_details}",
            extra={
                "request_id": error_response.request_id,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "validation_errors": error_details
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump()
        )
    
    def handle_http_exception(self, exc: HTTPException, request: Request) -> JSONResponse:
        """Handle HTTP exceptions"""
        error_response = ErrorResponse(
            error=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            detail=str(exc.detail) if not isinstance(exc.detail, str) else None,
            status_code=exc.status_code,
            timestamp=time.time(),
            request_id=request.headers.get("X-Request-ID")
        )
        
        self.logger.warning(
            f"HTTP {exc.status_code} error for {request.method} {request.url}: {exc.detail}",
            extra={
                "request_id": error_response.request_id,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "status_code": exc.status_code
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    def handle_generic_exception(self, exc: Exception, request: Request) -> JSONResponse:
        """Handle generic exceptions"""
        error_response = ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            timestamp=time.time(),
            request_id=request.headers.get("X-Request-ID")
        )
        
        # Log the full error with traceback
        self.logger.error(
            f"Unhandled exception for {request.method} {request.url}: {str(exc)}",
            extra={
                "request_id": error_response.request_id,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )
    
    def handle_starlette_http_exception(self, exc: StarletteHTTPException, request: Request) -> JSONResponse:
        """Handle Starlette HTTP exceptions"""
        return self.handle_http_exception(
            HTTPException(status_code=exc.status_code, detail=exc.detail),
            request
        )


# Global error handler instance
error_handler = ErrorHandler()


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """FastAPI exception handler for validation errors"""
    return error_handler.handle_validation_error(exc, request)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """FastAPI exception handler for HTTP exceptions"""
    return error_handler.handle_http_exception(exc, request)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI exception handler for generic exceptions"""
    return error_handler.handle_generic_exception(exc, request)


def setup_error_handlers(app) -> None:
    """Setup error handlers for the FastAPI application"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add security headers
            async def send_with_headers(message):
                if message["type"] == "http.response.start":
                    headers = message.get("headers", [])
                    headers.extend([
                        (b"X-Content-Type-Options", b"nosniff"),
                        (b"X-Frame-Options", b"DENY"),
                        (b"X-XSS-Protection", b"1; mode=block"),
                        (b"Referrer-Policy", b"strict-origin-when-cross-origin"),
                        (b"Content-Security-Policy", b"default-src 'self'"),
                    ])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_with_headers)
        else:
            await self.app(scope, receive, send)


def log_request_middleware(app):
    """Middleware to log all requests for monitoring"""
    
    async def log_request(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url}",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_id": request.headers.get("X-Request-ID")
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
                "request_id": request.headers.get("X-Request-ID")
            }
        )
        
        return response
    
    return log_request


def setup_middleware(app) -> None:
    """Setup middleware for the FastAPI application"""
    app.middleware("http")(log_request_middleware)
    app.add_middleware(SecurityMiddleware)
