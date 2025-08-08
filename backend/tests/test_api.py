import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from main import app
from simple_db import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Setup test database before each test"""
    init_db()
    yield
    # Cleanup after test

class TestHealthEndpoints:
    def test_root_health_check(self):
        """Test root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"

    def test_api_health_check(self):
        """Test API health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "vantage-ai-api"

class TestProjectsEndpoints:
    def test_get_projects_default(self):
        """Test getting projects with default parameters"""
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["items"]) > 0

    def test_get_projects_with_pagination(self):
        """Test getting projects with pagination"""
        response = client.get("/api/v1/projects?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5
        assert data["limit"] == 5
        assert data["offset"] == 0

    def test_get_projects_with_filters(self):
        """Test getting projects with filters"""
        response = client.get("/api/v1/projects?location=Dubai&price_range=Premium")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_project_by_id(self):
        """Test getting a specific project"""
        # First get all projects to get an ID
        projects_response = client.get("/api/v1/projects?limit=1")
        projects_data = projects_response.json()
        if projects_data["items"]:
            project_id = projects_data["items"][0]["id"]

            response = client.get(f"/api/v1/projects/{project_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == project_id

    def test_get_project_not_found(self):
        """Test getting a non-existent project"""
        response = client.get("/api/v1/projects/99999")
        assert response.status_code == 404

class TestDevelopersEndpoints:
    def test_get_developers(self):
        """Test getting all developers"""
        response = client.get("/api/v1/developers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_developer_by_id(self):
        """Test getting a specific developer"""
        # First get all developers to get an ID
        developers_response = client.get("/api/v1/developers")
        developers_data = developers_response.json()
        if developers_data:
            developer_id = developers_data[0]["id"]

            response = client.get(f"/api/v1/developers/{developer_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == developer_id

    def test_get_developer_not_found(self):
        """Test getting a non-existent developer"""
        response = client.get("/api/v1/developers/99999")
        assert response.status_code == 404

class TestMarketEndpoints:
    def test_get_market_overview(self):
        """Test getting market overview"""
        response = client.get("/api/v1/market/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "total_units" in data
        assert "active_developers" in data
        assert "avg_price_per_sqft" in data
        assert "sales_percentage" in data

    def test_get_top_performers(self):
        """Test getting top performers"""
        response = client.get("/api/v1/top-performers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5  # Default limit

    def test_get_top_performers_with_limit(self):
        """Test getting top performers with custom limit"""
        response = client.get("/api/v1/top-performers?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

class TestVantageScoreEndpoints:
    def test_get_vantage_score(self):
        """Test getting vantage score for a project"""
        # First get a project ID
        projects_response = client.get("/api/v1/projects?limit=1")
        projects_data = projects_response.json()
        if projects_data["items"]:
            project_id = projects_data["items"][0]["id"]

            response = client.get(f"/api/v1/projects/{project_id}/vantage-score")
            assert response.status_code == 200
            data = response.json()
            assert "project_id" in data
            assert "overall_score" in data
            assert "score_breakdown" in data
            assert "risk_level" in data

    def test_get_vantage_score_not_found(self):
        """Test getting vantage score for non-existent project"""
        response = client.get("/api/v1/projects/99999/vantage-score")
        assert response.status_code == 404

class TestFileUploadEndpoints:
    def test_upload_dld_transactions_csv(self):
        """Test uploading DLD transactions CSV file"""
        # Create sample CSV data
        csv_data = """Transaction ID,Property Type,Location,Transaction Date,Price (AED),Area (sq ft),Developer Name
TXN001,Apartment,Dubai Marina,2024-01-15,2500000,1200,Emaar Properties
TXN002,Villa,Palm Jumeirah,2024-01-20,5000000,2500,Damac Properties"""

        files = {"file": ("test_transactions.csv", io.StringIO(csv_data), "text/csv")}
        response = client.post("/api/v1/upload/dld-transactions", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["processed_rows"] == 2
        assert data["total_rows"] == 2

    def test_upload_dld_transactions_excel(self):
        """Test uploading DLD transactions Excel file"""
        # Create sample Excel data
        df = pd.DataFrame({
            'Transaction ID': ['TXN003', 'TXN004'],
            'Property Type': ['Apartment', 'Villa'],
            'Location': ['Downtown Dubai', 'Dubai Hills'],
            'Transaction Date': ['2024-01-25', '2024-01-30'],
            'Price (AED)': [3000000, 6000000],
            'Area (sq ft)': [1400, 2800],
            'Developer Name': ['Emaar Properties', 'Sobha Realty']
        })

        # Save to bytes buffer
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        files = {"file": ("test_transactions.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = client.post("/api/v1/upload/dld-transactions", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["processed_rows"] == 2

    def test_upload_invalid_file_type(self):
        """Test uploading invalid file type"""
        files = {"file": ("test.txt", io.StringIO("invalid data"), "text/plain")}
        response = client.post("/api/v1/upload/dld-transactions", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "Only CSV and Excel files are supported" in data["detail"]

    def test_upload_missing_columns(self):
        """Test uploading file with missing required columns"""
        csv_data = """Transaction ID,Property Type,Location
TXN001,Apartment,Dubai Marina"""

        files = {"file": ("test_transactions.csv", io.StringIO(csv_data), "text/csv")}
        response = client.post("/api/v1/upload/dld-transactions", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "Missing required columns" in data["detail"]

class TestErrorHandling:
    def test_invalid_pagination_parameters(self):
        """Test invalid pagination parameters"""
        response = client.get("/api/v1/projects?limit=-1")
        assert response.status_code == 422  # Validation error

        response = client.get("/api/v1/projects?offset=-1")
        assert response.status_code == 422

    def test_invalid_limit_parameter(self):
        """Test invalid limit parameter for top performers"""
        response = client.get("/api/v1/top-performers?limit=1000")
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])
