"""Subscription model for Polar B2B subscriptions."""
from datetime import datetime
from typing import Optional, Union
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field
import uuid


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Subscription(BaseModel):
    """Subscription model for Polar B2B subscriptions."""
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Subscription UUID (primary key)")
    org_id: str = Field(..., description="Organization ID (FK to organizations)")
    polar_subscription_id: str = Field(..., description="Polar subscription ID")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.EXPIRED, description="Subscription status")
    plan_name: str = Field(..., description="Plan name")
    plan_price: Union[Decimal, float] = Field(..., description="Plan price")
    current_period_start: datetime = Field(..., description="Current period start")
    current_period_end: datetime = Field(..., description="Current period end")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "subscription_id": "550e8400-e29b-41d4-a716-446655440000",
                "org_id": "org_123",
                "polar_subscription_id": "sub_polar_123",
                "status": "active",
                "plan_name": "Professional Plan",
                "plan_price": "99.00",
                "current_period_start": "2024-01-01T00:00:00Z",
                "current_period_end": "2024-02-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }

