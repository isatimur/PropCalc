"""
Pytest configuration and fixtures for PropCalc backend tests
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.propcalc.main import app
from src.propcalc.core.performance.connection_pool import init_connection_pools, close_connection_pools
from src.propcalc.infrastructure.cache.redis_cache import init_redis, close_redis

# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Global test client
test_client = TestClient(app)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="session")
def sync_client() -> TestClient:
    """Create a sync HTTP client for testing."""
    return test_client

@pytest.fixture(scope="session")
async def setup_test_environment():
    """Setup test environment with connection pools and cache."""
    try:
        # Initialize connection pools for testing
        init_connection_pools()
        yield
    finally:
        # Cleanup
        await close_connection_pools()

@pytest.fixture(scope="function")
async def db_connection():
    """Get a database connection for testing."""
    from src.propcalc.infrastructure.database.postgres_db import get_db_instance
    db = await get_db_instance()
    yield db

@pytest.fixture(scope="function")
async def redis_client():
    """Get a Redis client for testing."""
    try:
        init_redis()
        from src.propcalc.infrastructure.cache.redis_cache import redis_client
        yield redis_client
    finally:
        close_redis()

# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )

# Test data fixtures
@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "price": 1500000,
        "area": 1200,
        "location_score": 85,
        "developer_score": 90,
        "market_trend": 2,
        "completion_date_score": 80,
        "property_type_score": 85,
        "amenities_score": 88,
        "transport_score": 82,
        "school_score": 87,
        "project_name": "Test Project",
        "developer_name": "Test Developer",
        "location": "Test Location"
    }

@pytest.fixture
def sample_dld_transaction():
    """Sample DLD transaction data for testing."""
    return {
        "transaction_id": "TEST-001",
        "property_id": "PROP-001",
        "transaction_date": "2024-01-15",
        "transaction_type": "Sale",
        "property_type": "Apartment",
        "area_sqft": 1200.0,
        "price_aed": 1500000,
        "price_per_sqft": 1250.0,
        "location": "Dubai Marina",
        "developer": "Test Developer",
        "project_name": "Test Project"
    }

# Mock fixtures for external services
@pytest.fixture
def mock_external_api(monkeypatch):
    """Mock external API calls for testing."""
    class MockExternalAPI:
        async def get_data(self):
            return {"mock": "data"}
    
    monkeypatch.setattr("src.propcalc.core.external_api.ExternalAPIClient", MockExternalAPI)
    return MockExternalAPI()

# Performance testing fixtures
@pytest.fixture
def performance_test_config():
    """Configuration for performance tests."""
    return {
        "max_response_time_ms": 200,
        "max_database_query_time_ms": 100,
        "concurrent_users": 10,
        "test_duration_seconds": 30
    }
