"""
Pydantic schemas for API models
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """User creation schema"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")

class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")

class PasswordReset(BaseModel):
    """Password reset schema"""
    email: str = Field(..., description="User email")

class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., description="Project name")
    developer: str | None = Field(None, description="Developer name")
    location: str | None = Field(None, description="Project location")
    price: float | None = Field(None, description="Project price")
    vantage_score: float | None = Field(None, description="Vantage Score")

class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DeveloperBase(BaseModel):
    """Base developer schema"""
    name: str = Field(..., description="Developer name")
    performance_score: float | None = Field(None, description="Performance score")

class DeveloperResponse(DeveloperBase):
    """Developer response schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MarketOverview(BaseModel):
    """Market overview schema"""
    total_projects: int = Field(..., description="Total number of projects")
    average_price: float = Field(..., description="Average project price")
    average_vantage_score: float = Field(..., description="Average Vantage Score")
    last_updated: str = Field(..., description="Last update timestamp")

class VantageScoreRequest(BaseModel):
    """Vantage Score calculation request"""
    project_data: dict[str, Any] = Field(..., description="Project data for scoring")

class VantageScoreResponse(BaseModel):
    """Vantage Score calculation response"""
    score: float = Field(..., description="Calculated Vantage Score")
    confidence: float = Field(..., description="Prediction confidence")
    features: dict[str, float] = Field(..., description="Feature importance")

class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")

class CacheStats(BaseModel):
    """Cache statistics response"""
    connected_clients: int = Field(..., description="Connected Redis clients")
    used_memory_human: str = Field(..., description="Memory usage")
    hit_rate: float = Field(..., description="Cache hit rate")
    keyspace_hits: int = Field(..., description="Cache hits")
    keyspace_misses: int = Field(..., description="Cache misses")
