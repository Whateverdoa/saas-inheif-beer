"""Order model for B2B and B2C orders."""
from datetime import datetime
from typing import Optional, Dict, Any, Union
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field
import uuid

from app.models.pdf_validation import PDFValidationResult


class OrderType(str, Enum):
    """Order type enumeration."""
    B2B = "b2b"
    B2C = "b2c"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OrderSpecifications(BaseModel):
    """Order specifications for OGOS API."""
    location_code: str = Field(..., description="OGOS location code")
    material_code: Optional[str] = Field(default=None, description="Material code")
    quantity: int = Field(..., description="Quantity")
    shape: Optional[str] = Field(default=None, description="Shape")
    adhesive: Optional[str] = Field(default=None, description="Adhesive type")
    core_size: Optional[str] = Field(default=None, description="Core size")
    product_type: Optional[str] = Field(default=None, description="Product type")
    shipping_method: Optional[str] = Field(default=None, description="Shipping method")


class ShippingAddress(BaseModel):
    """Shipping address for order."""
    name: str = Field(..., description="Recipient name")
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    postal_code: str = Field(..., description="Postal code")
    country: str = Field(default="NL", description="Country code")
    phone: Optional[str] = Field(default=None, description="Phone number")


class Order(BaseModel):
    """Order model for both B2B and B2C orders."""
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Order UUID (primary key)")
    user_id: str = Field(..., description="User ID (FK to users)")
    org_id: Optional[str] = Field(default=None, description="Organization ID (FK to organizations, nullable for B2C)")
    order_type: OrderType = Field(..., description="Order type (b2b or b2c)")
    ogos_order_id: Optional[str] = Field(default=None, description="OGOS order ID from API response")
    reference: str = Field(..., description="Customer reference")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    
    # PDF storage
    pdf_url: Optional[str] = Field(default=None, description="PDF file storage URL/path")
    pdf_metadata: Optional[PDFValidationResult] = Field(default=None, description="PDF validation metadata")
    
    # Order specifications
    specifications: OrderSpecifications = Field(..., description="Order specifications")
    shipping_address: ShippingAddress = Field(..., description="Shipping address")
    
    # Pricing
    price_calculated: Optional[Union[Decimal, float]] = Field(default=None, description="Calculated price")
    shipping_cost: Optional[Union[Decimal, float]] = Field(default=None, description="Shipping cost")
    total: Optional[Union[Decimal, float]] = Field(default=None, description="Total amount")
    currency: str = Field(default="EUR", description="Currency code")
    
    # Payment (B2C)
    payment_id: Optional[str] = Field(default=None, description="Stripe payment intent ID (B2C)")
    
    # OGOS GUID used
    ogos_guid_used: str = Field(..., description="OGOS GUID used for this order")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    submitted_at: Optional[datetime] = Field(default=None, description="Submission timestamp")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_2abc123",
                "org_id": None,
                "order_type": "b2c",
                "ogos_order_id": "OGOS-12345",
                "reference": "ORDER-2024-001",
                "status": "pending",
                "pdf_url": "/uploads/order.pdf",
                "specifications": {
                    "location_code": "NL001",
                    "material_code": "MAT001",
                    "quantity": 100,
                },
                "price_calculated": "50.00",
                "shipping_cost": "5.00",
                "total": "55.00",
                "currency": "EUR",
                "ogos_guid_used": "master-guid-123",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }

