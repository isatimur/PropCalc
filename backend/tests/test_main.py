# backend/tests/test_main.py
from decimal import Decimal

import pytest
from ai_workers.scoring_logic import VantageScoringEngine
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models import Developer, Project
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestVantageAI:
    """Comprehensive test suite for Vantage AI Trust Protocol"""

    def setup_method(self):
        """Setup test data before each test"""
        db = TestingSessionLocal()

        # Clear existing data
        db.query(Project).delete()
        db.query(Developer).delete()
        db.commit()

        # Create test developer
        developer = Developer(
            name="Test Developer",
            established_year=2010,
            track_record_score=85.0,
            financial_stability_score=80.0,
            customer_satisfaction_score=82.0,
            completed_projects_count=15,
            average_delay_days=25,
            total_project_value=Decimal("5000000000")
        )
        db.add(developer)
        db.commit()

        # Create test project
        project = Project(
            name="Test Project",
            developer_id=1,
            latitude=Decimal("25.1972"),
            longitude=Decimal("55.2744"),
            total_units=500,
            units_sold=350,
            starting_price=Decimal("1000000"),
            current_price=Decimal("1100000"),
            completion_date="2025-06-15",
            project_type="Residential",
            area_sqm=50000,
            amenities=["Pool", "Gym", "Parking"],
            vantage_score=82.5,
            score_breakdown={
                "developer_track_record": 85.0,
                "sales_velocity": 80.0,
                "location_potential": 85.0,
                "project_quality_proxy": 80.0,
                "social_sentiment": 82.0
            }
        )
        db.add(project)
        db.commit()
        db.close()

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "Vantage AI Trust Protocol"}

    def test_get_projects(self):
        """Test getting all projects"""
        response = client.get("/projects/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Project"
        assert data[0]["vantage_score"] == 82.5

    def test_get_project_by_id(self):
        """Test getting a specific project"""
        response = client.get("/projects/1")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["vantage_score"] == 82.5
        assert "score_breakdown" in data

    def test_get_project_not_found(self):
        """Test getting non-existent project"""
        response = client.get("/projects/999")
        assert response.status_code == 404

    def test_get_developers(self):
        """Test getting all developers"""
        response = client.get("/developers/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Developer"
        assert data[0]["track_record_score"] == 85.0

    def test_get_developer_by_id(self):
        """Test getting a specific developer"""
        response = client.get("/developers/1")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Developer"
        assert data["track_record_score"] == 85.0

    def test_get_developer_not_found(self):
        """Test getting non-existent developer"""
        response = client.get("/developers/999")
        assert response.status_code == 404

    def test_create_project(self):
        """Test creating a new project"""
        project_data = {
            "name": "New Test Project",
            "developer_id": 1,
            "latitude": 25.2048,
            "longitude": 55.2708,
            "total_units": 300,
            "units_sold": 150,
            "starting_price": 800000,
            "current_price": 850000,
            "completion_date": "2025-12-31",
            "project_type": "Luxury",
            "area_sqm": 30000,
            "amenities": ["Pool", "Gym"]
        }

        response = client.post("/projects/", json=project_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Project"
        assert "vantage_score" in data

    def test_create_project_invalid_data(self):
        """Test creating project with invalid data"""
        project_data = {
            "name": "",  # Invalid empty name
            "developer_id": 999  # Non-existent developer
        }

        response = client.post("/projects/", json=project_data)
        assert response.status_code == 422

    def test_get_market_analysis(self):
        """Test market analysis endpoint"""
        response = client.get("/market/analysis")
        assert response.status_code == 200
        data = response.json()
        assert "market_overview" in data
        assert "top_performers" in data
        assert "risk_zones" in data
        assert "developer_rankings" in data

    def test_get_project_transparency(self):
        """Test project transparency endpoint"""
        response = client.get("/projects/1/transparency")
        assert response.status_code == 200
        data = response.json()
        assert "sales_progress" in data
        assert "construction_updates" in data
        assert "developer_history" in data

    def test_get_project_recommendations(self):
        """Test project recommendations endpoint"""
        response = client.get("/projects/1/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert "risk_factors" in data
        assert "recommendations" in data
        assert "comparison_data" in data

    def test_search_projects(self):
        """Test project search endpoint"""
        response = client.get("/projects/search?query=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_developer_projects(self):
        """Test getting projects by developer"""
        response = client.get("/developers/1/projects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(project["developer_id"] == 1 for project in data)

    def test_get_project_score_history(self):
        """Test getting project score history"""
        response = client.get("/projects/1/scores")
        assert response.status_code == 200
        data = response.json()
        assert "score_history" in data
        assert "trend_analysis" in data

    def test_vantage_scoring_engine(self):
        """Test the Vantage scoring engine"""
        scoring_engine = VantageScoringEngine()

        # Test score calculation
        project_data = {
            "developer_track_record": 85.0,
            "sales_velocity": 80.0,
            "location_potential": 85.0,
            "project_quality_proxy": 80.0,
            "social_sentiment": 82.0
        }

        score = scoring_engine.calculate_vantage_score(project_data)
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_api_documentation(self):
        """Test API documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

class TestVantageScoringEngine:
    """Test the Vantage scoring engine specifically"""

    def test_score_calculation(self):
        """Test basic score calculation"""
        engine = VantageScoringEngine()

        # Test with perfect scores
        perfect_data = {
            "developer_track_record": 100.0,
            "sales_velocity": 100.0,
            "location_potential": 100.0,
            "project_quality_proxy": 100.0,
            "social_sentiment": 100.0
        }

        score = engine.calculate_vantage_score(perfect_data)
        assert score == 100.0

        # Test with poor scores
        poor_data = {
            "developer_track_record": 0.0,
            "sales_velocity": 0.0,
            "location_potential": 0.0,
            "project_quality_proxy": 0.0,
            "social_sentiment": 0.0
        }

        score = engine.calculate_vantage_score(poor_data)
        assert score == 0.0

    def test_risk_assessment(self):
        """Test risk assessment functionality"""
        engine = VantageScoringEngine()

        # Test high-risk project
        high_risk_data = {
            "developer_track_record": 30.0,
            "sales_velocity": 20.0,
            "location_potential": 40.0,
            "project_quality_proxy": 25.0,
            "social_sentiment": 15.0
        }

        risk_factors = engine.assess_risk_factors(high_risk_data)
        assert len(risk_factors) > 0
        assert any("high" in factor.lower() for factor in risk_factors)

    def test_recommendations_generation(self):
        """Test recommendations generation"""
        engine = VantageScoringEngine()

        project_data = {
            "developer_track_record": 70.0,
            "sales_velocity": 60.0,
            "location_potential": 80.0,
            "project_quality_proxy": 65.0,
            "social_sentiment": 75.0
        }

        recommendations = engine.generate_recommendations(project_data)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)

if __name__ == "__main__":
    pytest.main([__file__])
