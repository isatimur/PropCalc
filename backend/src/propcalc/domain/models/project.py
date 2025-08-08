"""
Project domain model
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class ProjectType(str, Enum):
    """Project type enumeration"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    LAND = "land"

class Project(BaseModel):
    """Project domain model"""
    id: int | None = None
    name: str = Field(..., description="Project name")
    developer: str | None = Field(None, description="Developer name")
    location: str | None = Field(None, description="Project location")
    price: float | None = Field(None, description="Project price")
    vantage_score: float | None = Field(None, description="Vantage Score")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Project status")
    project_type: ProjectType = Field(ProjectType.RESIDENTIAL, description="Project type")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
