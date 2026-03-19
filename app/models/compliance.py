"""Compliance and legal document models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LegalDocumentVersion(BaseModel):
    """Version information for a legal document."""
    version: str = Field(..., description="Document version identifier")
    last_updated: datetime = Field(..., description="Last update timestamp")
    content: str = Field(..., description="Document content (markdown or HTML)")


class LegalDocumentInfo(BaseModel):
    """Information about a legal document."""
    document_type: str = Field(..., description="Type of document (terms, privacy, dpa, cookies)")
    current_version: str = Field(..., description="Current version identifier")
    last_updated: datetime = Field(..., description="Last update timestamp")
    available_formats: list[str] = Field(default=["markdown", "html"], description="Available output formats")


class ChecklistItem(BaseModel):
    """Single item in the launch checklist."""
    id: str = Field(..., description="Unique identifier for the checklist item")
    name: str = Field(..., description="Display name of the checklist item")
    status: str = Field(default="pending", description="Status: pending or completed")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    notes: Optional[str] = Field(default=None, description="Additional notes about this item")


class ComplianceStatus(BaseModel):
    """Overall compliance status."""
    total_items: int = Field(..., description="Total number of checklist items")
    completed_items: int = Field(..., description="Number of completed items")
    completion_percentage: float = Field(..., description="Completion percentage (0-100)")
    items: list[ChecklistItem] = Field(..., description="List of all checklist items")

