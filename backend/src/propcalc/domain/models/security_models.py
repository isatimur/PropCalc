"""
Domain models for PropCalc with input validation and sanitization
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class ProjectData(BaseModel):
    """Validated project data for Vantage Score calculation"""
    
    # Core property data
    price: float = Field(..., gt=0, le=1000000000, description="Property price in AED")
    area: float = Field(..., gt=0, le=100000, description="Property area in sq ft")
    
    # Scoring components (0-100 scale)
    location_score: float = Field(default=80, ge=0, le=100, description="Location quality score")
    developer_score: float = Field(default=80, ge=0, le=100, description="Developer reputation score")
    market_trend: float = Field(default=0, ge=-10, le=10, description="Market trend indicator")
    completion_date_score: float = Field(default=80, ge=0, le=100, description="Completion date score")
    property_type_score: float = Field(default=80, ge=0, le=100, description="Property type score")
    amenities_score: float = Field(default=80, ge=0, le=100, description="Amenities quality score")
    transport_score: float = Field(default=80, ge=0, le=100, description="Transport accessibility score")
    school_score: float = Field(default=80, ge=0, le=100, description="School quality score")
    
    # Additional data
    project_name: Optional[str] = Field(None, max_length=200, description="Project name")
    developer_name: Optional[str] = Field(None, max_length=200, description="Developer name")
    location: Optional[str] = Field(None, max_length=200, description="Property location")
    
    @field_validator('project_name', 'developer_name', 'location')
    @classmethod
    def sanitize_string_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize string fields to prevent injection attacks"""
        if v is None:
            return v
        
        # Remove potentially dangerous characters
        v = re.sub(r'[<>"\']', '', v)
        # Remove multiple spaces
        v = re.sub(r'\s+', ' ', v)
        # Strip whitespace
        return v.strip()
    
    @field_validator('price', 'area')
    @classmethod
    def validate_positive_numbers(cls, v: float) -> float:
        """Ensure numbers are positive and reasonable"""
        if v <= 0:
            raise ValueError("Value must be positive")
        if v > 1000000000:  # 1 billion AED limit
            raise ValueError("Value exceeds maximum allowed")
        return v
    
    @model_validator(mode='after')
    def validate_score_consistency(self) -> 'ProjectData':
        """Validate that scores are consistent"""
        scores = [
            self.location_score, self.developer_score, self.completion_date_score,
            self.property_type_score, self.amenities_score, self.transport_score, self.school_score
        ]
        
        if any(score < 0 or score > 100 for score in scores):
            raise ValueError("All scores must be between 0 and 100")
        
        return self


class AIRequest(BaseModel):
    """Base model for AI API requests with rate limiting info"""
    
    client_id: Optional[str] = Field(None, max_length=100, description="Client identifier")
    request_id: Optional[str] = Field(None, max_length=100, description="Request identifier")
    
    @field_validator('client_id', 'request_id')
    @classmethod
    def sanitize_identifiers(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize identifier fields"""
        if v is None:
            return v
        
        # Only allow alphanumeric, hyphens, and underscores
        v = re.sub(r'[^a-zA-Z0-9\-_]', '', v)
        return v


class EnhancedScoreRequest(AIRequest):
    """Request model for enhanced score calculation"""
    
    project_data: ProjectData = Field(..., description="Project data for scoring")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_data": {
                    "price": 1500000,
                    "area": 1200,
                    "location_score": 85,
                    "developer_score": 90,
                    "market_trend": 2.5,
                    "completion_date_score": 88,
                    "property_type_score": 85,
                    "amenities_score": 82,
                    "transport_score": 87,
                    "school_score": 80,
                    "project_name": "Marina Heights",
                    "developer_name": "Emaar Properties",
                    "location": "Dubai Marina"
                }
            }
        }


class CompareScoresRequest(AIRequest):
    """Request model for score comparison"""
    
    project_data: ProjectData = Field(..., description="Project data for comparison")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_data": {
                    "price": 2000000,
                    "area": 1500,
                    "location_score": 90,
                    "developer_score": 95,
                    "market_trend": 3.0,
                    "completion_date_score": 92,
                    "property_type_score": 88,
                    "amenities_score": 85,
                    "transport_score": 90,
                    "school_score": 85,
                    "project_name": "Palm Jumeirah Villa",
                    "developer_name": "Nakheel Properties",
                    "location": "Palm Jumeirah"
                }
            }
        }


class TrainModelRequest(AIRequest):
    """Request model for model training"""
    
    num_samples: int = Field(default=2000, ge=100, le=10000, description="Number of training samples")
    algorithm: str = Field(default="random_forest", description="ML algorithm to use")
    
    @field_validator('algorithm')
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate ML algorithm selection"""
        allowed_algorithms = ["random_forest", "gradient_boosting", "linear_regression"]
        if v not in allowed_algorithms:
            raise ValueError(f"Algorithm must be one of {allowed_algorithms}")
        return v


class APIResponse(BaseModel):
    """Standard API response model"""
    
    status: str = Field(..., description="Response status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: float = Field(..., description="Response timestamp")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field"""
        allowed_statuses = ["success", "error", "warning"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: float = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
