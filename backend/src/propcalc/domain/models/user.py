"""
User domain model
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(BaseModel):
    """User domain model"""
    id: int | None = None
    email: str = Field(..., description="User email")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    role: UserRole = Field(UserRole.USER, description="User role")
    is_active: bool = Field(True, description="User active status")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
