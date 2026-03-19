"""Transaction model for payments."""
from datetime import datetime
from typing import Optional, Dict, Any, Union
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field
import uuid


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TransactionProvider(str, Enum):
    """Transaction provider enumeration."""
    STRIPE = "stripe"
    POLAR = "polar"


class Transaction(BaseModel):
    """Transaction model for payments (B2C + subscription payments)."""
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Transaction UUID (primary key)")
    user_id: str = Field(..., description="User ID (FK to users)")
    org_id: Optional[str] = Field(default=None, description="Organization ID (FK to organizations, nullable)")
    order_id: Optional[str] = Field(default=None, description="Order ID (FK to orders, nullable)")
    provider: TransactionProvider = Field(..., description="Payment provider")
    provider_transaction_id: str = Field(..., description="Provider transaction ID")
    amount: Union[Decimal, float] = Field(..., description="Transaction amount")
    currency: str = Field(default="EUR", description="Currency code")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, description="Transaction status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_2abc123",
                "org_id": None,
                "order_id": None,
                "provider": "stripe",
                "provider_transaction_id": "pi_1234567890",
                "amount": "10.00",
                "currency": "EUR",
                "status": "completed",
                "metadata": {},
                "created_at": "2024-01-01T00:00:00Z",
            }
        }

