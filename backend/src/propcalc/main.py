import logging
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .api.ai import router as ai_router
from .api.analytics import router as analytics_router
from .api.auth import router as auth_router
from .api.unified_dld_routes import router as unified_dld_router
from .api.developer import router as developer_router
from .api.gdpr import router as gdpr_router
# Import new API modules
from .api.market_routes import router as market_router
from .api.normalization_routes import router as normalization_router
from .api.pipeline_routes import router as pipeline_router
from .api.projects_routes import router as projects_router
from .api.system import router as system_router
from .api.area_mapping_routes import router as area_mapping_router

# Import AI and monitoring modules
from .core.exceptions import *
from .core.performance.connection_pool import init_connection_pools, close_connection_pools

# Import performance optimization modules
from .core.performance.rate_limiter import get_rate_limiter, init_rate_limiter
from .domain.schemas import *

# Import security modules
from .domain.security.gdpr import init_gdpr_manager
from .infrastructure.cache.redis_cache import (
    close_redis,
    init_redis,
)
from .infrastructure.database.postgres_db import (
    close_db,
    get_db_instance,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration - Always use PostgreSQL for production
logger.info("Using PostgreSQL database")

# Initialize Redis cache (optional for development)
try:
    init_redis()
    logger.info("Redis cache initialized")
except Exception as e:
    logger.warning(f"Redis cache not available: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Vantage AI application...")

    # Initialize PostgreSQL connection pool
    try:
        init_connection_pools()
        logger.info("✅ PostgreSQL connection pools initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize PostgreSQL connection pools: {e}")
        raise

    # Initialize Redis cache
    try:
        init_redis()
        logger.info("✅ Redis cache initialized")
    except Exception as e:
        logger.warning(f"⚠️ Redis cache not available: {e}")

    # Initialize OAuth manager with Redis client
    try:
        from .infrastructure.cache.redis_cache import redis_client
        # OAuth manager is already initialized in the module
        logger.info("✅ OAuth manager initialized")
    except Exception as e:
        logger.warning(f"⚠️ OAuth manager not available: {e}")

    # Initialize GDPR manager with Redis client
    try:
        init_gdpr_manager(redis_client)
        logger.info("✅ GDPR manager initialized")
    except Exception as e:
        logger.warning(f"⚠️ GDPR manager not available: {e}")

    # Initialize rate limiter with Redis client
    try:
        init_rate_limiter(redis_client)
        logger.info("✅ Rate limiter initialized")
    except Exception as e:
        logger.warning(f"⚠️ Rate limiter not available: {e}")

    logger.info("✅ Vantage AI application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Vantage AI application...")

    # Close PostgreSQL connections
    try:
        await close_connection_pools()
        logger.info("✅ PostgreSQL connection pools closed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Error closing database connection pools: {e}")

    # Close database connections
    try:
        await close_db()
        logger.info("✅ PostgreSQL connections closed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Error closing database connections: {e}")

    # Close Redis connections
    try:
        close_redis()
        logger.info("✅ Redis connections closed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Error closing Redis connections: {e}")

    logger.info("✅ Vantage AI application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Vantage AI - Advanced Real Estate Analytics",
    description="AI-powered real estate analytics platform with advanced ML features",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
        "http://localhost",
        "http://127.0.0.1",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers_and_rate_limiting(request: Request, call_next):
    """Add security headers and rate limiting to all responses."""

    # Rate limiting check
    try:
        rate_limiter = get_rate_limiter()
        client_id = rate_limiter.get_client_identifier(request)
        endpoint = request.url.path

        # Skip rate limiting for health checks and metrics
        if endpoint in ["/", "/api/v1/health", "/metrics"]:
            pass
        else:
            is_allowed, rate_limit_info = rate_limiter.check_rate_limit(endpoint, client_id)

            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Too many requests for {endpoint}",
                        "rate_limit_info": rate_limit_info
                    }
                )
    except Exception as e:
        logger.warning(f"Rate limiting check failed: {e}")
        # Continue without rate limiting if there's an error

    # Process request
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # More permissive CSP to allow Swagger UI and ReDoc to work
    response.headers["Content-Security-Policy"] = "default-src 'self' https:; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' https: data:; font-src 'self' https: data:"

    # Remove server information
    if "server" in response.headers:
        del response.headers["server"]

    return response

# Include unified DLD routes
app.include_router(unified_dld_router)
app.include_router(pipeline_router)

# Include new API routes
app.include_router(market_router)
app.include_router(projects_router)
app.include_router(normalization_router)
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(gdpr_router)
app.include_router(developer_router)
app.include_router(ai_router)
app.include_router(analytics_router)
app.include_router(area_mapping_router)


# Configure Sentry only if DSN is provided
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )
        logger.info("Sentry initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Sentry: {e}")
else:
    logger.info("Sentry DSN not provided, skipping Sentry initialization")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
