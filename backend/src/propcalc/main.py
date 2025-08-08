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
from .api.comprehensive_dld_routes import router as comprehensive_dld_router
from .api.developer import router as developer_router

# Import DLD integration modules
from .api.dld_routes import router as dld_router
from .api.gdpr import router as gdpr_router
from .api.market_demo_routes import router as market_demo_router

# Import new API modules
from .api.market_routes import router as market_router
from .api.normalization_routes import router as normalization_router
from .api.pipeline_routes import router as pipeline_router
from .api.projects_routes import router as projects_router
from .api.real_dld_routes import router as real_dld_router
from .api.realtime_dld_routes import router as realtime_dld_router
from .api.system import router as system_router
from .api.vantage_score_demo import router as vantage_score_router

# Import AI and monitoring modules
from .core.exceptions import *
from .core.performance.connection_pool import init_connection_pools

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
    close_connection_pool,
    init_connection_pool,
)

# Import database modules
from .infrastructure.database.simple_db import init_db as init_simple_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration - Use PostgreSQL by default
USE_POSTGRES = os.getenv('USE_POSTGRES', 'true').lower() == 'true'

# Initialize database
if USE_POSTGRES:
    # Note: This needs to be awaited in the lifespan function
    logger.info("Using PostgreSQL database")
else:
    init_simple_db()
    logger.info("Using SQLite database")

# Initialize Redis cache
init_redis()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Vantage AI application...")

    # Initialize PostgreSQL if using it
    if USE_POSTGRES:
        try:
            await init_connection_pool()
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")

    # Initialize Redis cache
    init_redis()

    # Initialize OAuth manager with Redis client
    from .infrastructure.cache.redis_cache import redis_client
    # OAuth manager is already initialized in the module

    # Initialize GDPR manager with Redis client
    init_gdpr_manager(redis_client)

    # Initialize rate limiter with Redis client
    init_rate_limiter(redis_client)

    # Initialize performance modules
    init_connection_pools()

    logger.info("Vantage AI application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Vantage AI application...")

    # Close database connections
    if USE_POSTGRES:
        try:
            await close_connection_pool()
        except Exception as e:
            logger.warning(f"Error closing database connections: {e}")

    # Close Redis connections
    close_redis()

    logger.info("Vantage AI application shutdown complete")

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
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

    # Remove server information
    if "server" in response.headers:
        del response.headers["server"]

    return response

# Include DLD integration routes
app.include_router(dld_router)
app.include_router(real_dld_router)
app.include_router(realtime_dld_router)
app.include_router(pipeline_router)
app.include_router(comprehensive_dld_router)

# Include new API routes
app.include_router(market_router)
app.include_router(projects_router)
app.include_router(normalization_router)
app.include_router(vantage_score_router)
app.include_router(market_demo_router)
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(gdpr_router)
app.include_router(developer_router)
app.include_router(ai_router)
app.include_router(analytics_router)


# Configure Sentry
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
