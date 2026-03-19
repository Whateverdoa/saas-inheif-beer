"""User model for Clerk-authenticated users."""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User role enumeration."""
    B2B_ADMIN = "b2b_admin"
    B2C_CUSTOMER = "b2c_customer"


class User(BaseModel):
    """User model representing Clerk-authenticated users."""
    user_id: str = Field(..., description="Clerk user ID (primary key)")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(default=None, description="User full name")
    role: UserRole = Field(default=UserRole.B2C_CUSTOMER, description="User role")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_2abc123",
                "email": "user@example.com",
                "name": "John Doe",
                "role": "b2c_customer",
                "metadata": {},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }

