"""
API endpoint tests for PropCalc backend
Uses proper testing patterns and fixtures
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.propcalc.main import app

# Test client
test_client = TestClient(app)

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    @pytest.mark.api
    @pytest.mark.unit
    def test_root_health_check(self):
        """Test root health check endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"

    @pytest.mark.api
    @pytest.mark.unit
    def test_api_health_check(self):
        """Test API health check endpoint"""
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "vantage-ai-api"

class TestProjectsEndpoints:
    """Test projects API endpoints"""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_get_projects_default(self):
        """Test getting projects with default parameters"""
        response = test_client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        # Note: In test environment, items might be empty
        assert isinstance(data["items"], list)

    @pytest.mark.api
    @pytest.mark.integration
    def test_get_projects_with_pagination(self):
        """Test getting projects with pagination"""
        response = test_client.get("/api/v1/projects?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5
        assert data["limit"] == 5
        assert data["offset"] == 0

    @pytest.mark.api
    @pytest.mark.integration
    def test_get_projects_with_filters(self):
        """Test getting projects with filters"""
        response = test_client.get("/api/v1/projects?location=Dubai&price_range=Premium")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.api
    @pytest.mark.integration
    def test_get_project_by_id(self):
        """Test getting a specific project"""
        # First get all projects to get an ID
        projects_response = test_client.get("/api/v1/projects?limit=1")
        projects_data = projects_response.json()
        
        if projects_data["items"]:
            project_id = projects_data["items"][0]["id"]
            response = test_client.get(f"/api/v1/projects/{project_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == project_id
        else:
            # If no projects exist, test with a non-existent ID
            response = test_client.get("/api/v1/projects/99999")
            assert response.status_code == 404

    @pytest.mark.api
    @pytest.mark.unit
    def test_get_project_not_found(self):
        """Test getting a non-existent project"""
        response = test_client.get("/api/v1/projects/99999")
        assert response.status_code == 404

class TestDevelopersEndpoints:
    """Test developers API endpoints"""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_get_developers(self):
        """Test getting all developers"""
        response = test_client.get("/api/v1/developers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Note: In test environment, list might be empty
        assert isinstance(data, list)

    @pytest.mark.api
    @pytest.mark.integration
    def test_get_developer_by_id(self):
        """Test getting a specific developer"""
        # First get all developers to get an ID
        developers_response = test_client.get("/api/v1/developers")
        developers_data = developers_response.json()
        
        if developers_data:
            developer_id = developers_data[0]["id"]
            response = test_client.get(f"/api/v1/developers/{developer_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == developer_id
        else:
            # If no developers exist, test with a non-existent ID
            response = test_client.get("/api/v1/developers/99999")
            assert response.status_code == 404

    @pytest.mark.api
    @pytest.mark.unit
    def test_get_developer_not_found(self):
        """Test getting a non-existent developer"""
        response = test_client.get("/api/v1/developers/99999")
        assert response.status_code == 404

class TestAnalyticsEndpoints:
    """Test analytics API endpoints"""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_get_market_overview(self):
        """Test getting market overview"""
        response = test_client.get("/api/v1/analytics/market-overview")
        assert response.status_code == 200
        data = response.json()
        # Validate response structure
        assert isinstance(data, dict)

    @pytest.mark.api
    @pytest.mark.integration
    def test_get_dld_analytics(self):
        """Test getting DLD analytics"""
        response = test_client.get("/api/v1/analytics/dld")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.api
    @pytest.mark.unit
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = test_client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404

    @pytest.mark.api
    @pytest.mark.unit
    def test_invalid_project_id_format(self):
        """Test invalid project ID format"""
        response = test_client.get("/api/v1/projects/invalid-id")
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    @pytest.mark.unit
    def test_invalid_pagination_parameters(self):
        """Test invalid pagination parameters"""
        response = test_client.get("/api/v1/projects?limit=-1&offset=invalid")
        assert response.status_code == 422  # Validation error

# Performance tests
class TestPerformance:
    """Test API performance requirements"""
    
    @pytest.mark.slow
    @pytest.mark.api
    def test_health_check_response_time(self):
        """Test health check responds within 100ms"""
        import time
        start_time = time.time()
        response = test_client.get("/api/v1/health")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 100, f"Response time {response_time_ms}ms exceeds 100ms limit"
        assert response.status_code == 200

    @pytest.mark.slow
    @pytest.mark.api
    def test_projects_endpoint_response_time(self):
        """Test projects endpoint responds within 200ms"""
        import time
        start_time = time.time()
        response = test_client.get("/api/v1/projects?limit=10")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 200, f"Response time {response_time_ms}ms exceeds 200ms limit"
        assert response.status_code == 200

# Integration tests
class TestIntegration:
    """Test integration between different components"""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_database_connection(self, db_connection):
        """Test database connection works"""
        assert db_connection is not None
        # Test basic database operation
        result = db_connection.execute_query("SELECT 1 as test")
        assert len(result) > 0
        assert result[0]["test"] == 1

    @pytest.mark.integration
    @pytest.mark.redis
    def test_redis_connection(self, redis_client):
        """Test Redis connection works"""
        assert redis_client is not None
        # Test basic Redis operation
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        assert value == "test_value"
        redis_client.delete("test_key")
