"""PDF validation models."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PDFBox(BaseModel):
    """PDF box coordinates (trimbox, bleedbox, mediabox)."""
    x0: float = Field(..., description="Left coordinate")
    y0: float = Field(..., description="Bottom coordinate")
    x1: float = Field(..., description="Right coordinate")
    y1: float = Field(..., description="Top coordinate")


class PDFValidationResult(BaseModel):
    """PDF validation result."""
    is_valid: bool = Field(..., description="Whether PDF passed validation")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
    # File metadata
    file_size: int = Field(..., description="File size in bytes")
    page_count: int = Field(..., description="Number of pages")
    
    # PDF boxes
    trimbox: Optional[PDFBox] = Field(default=None, description="Trim box coordinates")
    bleedbox: Optional[PDFBox] = Field(default=None, description="Bleed box coordinates")
    mediabox: Optional[PDFBox] = Field(default=None, description="Media box coordinates")
    
    # Color space
    color_space: Optional[str] = Field(default=None, description="Color space (e.g., 'CMYK', 'RGB')")
    is_cmyk: bool = Field(default=False, description="Whether PDF uses CMYK color space")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional PDF metadata")

    # Physical size & form hints (first page trim / media; mm)
    trim_width_mm: Optional[float] = Field(
        default=None, description="Trim width in millimetres (from PDF boxes)"
    )
    trim_height_mm: Optional[float] = Field(
        default=None, description="Trim height in millimetres (from PDF boxes)"
    )
    media_width_mm: Optional[float] = Field(default=None, description="Media box width in mm")
    media_height_mm: Optional[float] = Field(default=None, description="Media box height in mm")
    bleed_insets_mm: Optional[Dict[str, float]] = Field(
        default=None,
        description="Bleed extension beyond trim: left, right, bottom, top (mm)",
    )
    dimensions_display: Optional[str] = Field(
        default=None, description="Human-readable trim size, e.g. '80 × 100'"
    )
    suggested_shape: Optional[str] = Field(
        default=None,
        description="Order form shape id: rond, ovaal, rechthoek, custom",
    )
    matched_standard_label_type_id: Optional[str] = Field(
        default=None, description="Closest catalog preset id within tolerance"
    )
    matched_standard_label_name: Optional[str] = Field(
        default=None, description="Closest catalog preset display name"
    )
    match_distance_mm: Optional[float] = Field(
        default=None, description="L1 distance to closest preset (mm), swap allowed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "file_size": 1234567,
                "page_count": 1,
                "trimbox": {"x0": 0.0, "y0": 0.0, "x1": 210.0, "y1": 297.0},
                "bleedbox": {"x0": -3.0, "y0": -3.0, "x1": 213.0, "y1": 300.0},
                "mediabox": {"x0": 0.0, "y0": 0.0, "x1": 210.0, "y1": 297.0},
                "color_space": "CMYK",
                "is_cmyk": True,
                "metadata": {},
            }
        }

