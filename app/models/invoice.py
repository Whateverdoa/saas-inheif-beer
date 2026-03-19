"""Invoice and transaction models."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceItem(BaseModel):
    """Single line item on an invoice."""
    description: str = Field(..., description="Item description")
    quantity: Decimal = Field(..., description="Quantity")
    unit_price: Decimal = Field(..., description="Unit price excluding VAT")
    vat_rate: Decimal = Field(default=Decimal("0.21"), description="VAT rate (default 21% for Netherlands)")
    total_excl_vat: Decimal = Field(..., description="Total excluding VAT")
    total_incl_vat: Decimal = Field(..., description="Total including VAT")


class Invoice(BaseModel):
    """Invoice model."""
    invoice_id: str = Field(..., description="Unique invoice identifier")
    invoice_number: str = Field(..., description="Human-readable invoice number")
    customer_name: str = Field(..., description="Customer name")
    customer_email: Optional[str] = Field(default=None, description="Customer email")
    customer_address: Optional[str] = Field(default=None, description="Customer address")
    
    # Company information
    company_name: str = Field(..., description="Company name")
    company_kvk: Optional[str] = Field(default=None, description="KvK number")
    company_btw: Optional[str] = Field(default=None, description="BTW/VAT number")
    company_address: Optional[str] = Field(default=None, description="Company address")
    company_bank_account: Optional[str] = Field(default=None, description="Bank account number")
    
    # Invoice details
    issue_date: datetime = Field(..., description="Invoice issue date")
    due_date: datetime = Field(..., description="Invoice due date")
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, description="Invoice status")
    
    # Financial details
    items: list[InvoiceItem] = Field(..., description="Invoice line items")
    subtotal_excl_vat: Decimal = Field(..., description="Subtotal excluding VAT")
    total_vat: Decimal = Field(..., description="Total VAT amount")
    total_incl_vat: Decimal = Field(..., description="Total including VAT")
    currency: str = Field(default="EUR", description="Currency code")
    
    # Payment information
    payment_provider: Optional[str] = Field(default=None, description="Payment provider (stripe, polar)")
    payment_id: Optional[str] = Field(default=None, description="Payment ID from provider")
    paid_at: Optional[datetime] = Field(default=None, description="Payment timestamp")
    
    # Integration
    eboekhouden_synced: bool = Field(default=False, description="Whether synced to e-boekhouden")
    eboekhouden_id: Optional[str] = Field(default=None, description="e-boekhouden transaction ID")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TransactionMapping(BaseModel):
    """Mapping from payment provider to e-boekhouden transaction format."""
    transaction_id: str = Field(..., description="Transaction ID from payment provider")
    provider: str = Field(..., description="Payment provider (stripe, polar)")
    amount: Decimal = Field(..., description="Transaction amount")
    currency: str = Field(default="EUR", description="Currency")
    description: str = Field(..., description="Transaction description")
    date: datetime = Field(..., description="Transaction date")
    customer_name: Optional[str] = Field(default=None, description="Customer name")
    customer_email: Optional[str] = Field(default=None, description="Customer email")
    invoice_id: Optional[str] = Field(default=None, description="Related invoice ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

