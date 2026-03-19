"""Organization model for B2B drukkerijen."""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Organization(BaseModel):
    """Organization model for B2B printing companies."""
    org_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Organization UUID (primary key)")
    user_id: str = Field(..., description="Owner user ID (FK to users)")
    name: str = Field(..., description="Organization name")
    kvk_number: Optional[str] = Field(default=None, description="KvK registration number")
    address: Optional[str] = Field(default=None, description="Organization address")
    contact_email: Optional[str] = Field(default=None, description="Contact email")
    ogos_guid: str = Field(..., description="Organization's OGOS GUID")
    subscription_id: Optional[str] = Field(default=None, description="Polar subscription ID")
    subscription_status: SubscriptionStatus = Field(default=SubscriptionStatus.EXPIRED, description="Subscription status")
    rate_limit_per_day: int = Field(default=100, description="Rate limit per day for orders")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "org_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_2abc123",
                "name": "Print Shop BV",
                "kvk_number": "12345678",
                "address": "123 Main St, Amsterdam",
                "contact_email": "contact@printshop.nl",
                "ogos_guid": "org-guid-12345",
                "subscription_id": "sub_polar_123",
                "subscription_status": "active",
                "rate_limit_per_day": 100,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }

