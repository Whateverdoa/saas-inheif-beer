"""Credit model for B2C prepaid credit system."""
from datetime import datetime
from typing import Optional, Union
from decimal import Decimal
from pydantic import BaseModel, Field
import uuid


class Credit(BaseModel):
    """Credit model for B2C prepaid credits."""
    credit_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Credit UUID (primary key)")
    user_id: str = Field(..., description="User ID (FK to users)")
    amount: Union[Decimal, float] = Field(..., description="Credit balance")
    transaction_id: Optional[str] = Field(default=None, description="Transaction ID (FK to transactions - purchase)")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp (nullable)")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "credit_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_2abc123",
                "amount": "10.00",
                "transaction_id": "txn_123",
                "expires_at": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }

