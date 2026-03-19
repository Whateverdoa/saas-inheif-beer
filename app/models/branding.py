"""Branding configuration models."""
from typing import Optional
from pydantic import BaseModel, Field


class BrandingConfig(BaseModel):
    """Branding configuration model."""
    logo_url: Optional[str] = Field(default=None, description="URL or path to logo image")
    primary_color: str = Field(default="#2563eb", description="Primary brand color (hex)")
    secondary_color: str = Field(default="#64748b", description="Secondary brand color (hex)")
    font_family: str = Field(default="Inter", description="Primary font family")
    company_name: str = Field(..., description="Company name")
    company_domain: Optional[str] = Field(default=None, description="Company domain")
    company_email: Optional[str] = Field(default=None, description="Company email address")


class CompanyInfo(BaseModel):
    """Company information model."""
    company_name: str = Field(..., description="Company name")
    kvk_number: Optional[str] = Field(default=None, description="KvK registration number")
    btw_number: Optional[str] = Field(default=None, description="BTW/VAT number")
    bank_account: Optional[str] = Field(default=None, description="Bank account number")
    address: Optional[str] = Field(default=None, description="Company address")
    domain: Optional[str] = Field(default=None, description="Company domain")
    email: Optional[str] = Field(default=None, description="Company email")

