"""PDF validation service using PyMuPDF."""
import logging
from typing import BinaryIO, Optional
import fitz  # PyMuPDF

from app.models.pdf_validation import PDFBox, PDFValidationResult
from app.services.pdf_color_probe import augment_color_space_from_content
from app.services.pdf_label_geometry import enrich_pdf_validation_result

logger = logging.getLogger("uvicorn.error")

# Validation limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_PAGE_COUNT = 100
MIN_FILE_SIZE = 1024  # 1 KB


class PDFValidator:
    """PDF validation service."""
    
    def __init__(
        self,
        max_file_size: int = MAX_FILE_SIZE,
        max_page_count: int = MAX_PAGE_COUNT,
        min_file_size: int = MIN_FILE_SIZE,
        require_cmyk: bool = True,
    ):
        """
        Initialize PDF validator.
        
        Args:
            max_file_size: Maximum file size in bytes
            max_page_count: Maximum number of pages
            min_file_size: Minimum file size in bytes
            require_cmyk: Whether CMYK color space is required
        """
        self.max_file_size = max_file_size
        self.max_page_count = max_page_count
        self.min_file_size = min_file_size
        self.require_cmyk = require_cmyk
    
    def validate(self, pdf_data: bytes) -> PDFValidationResult:
        """
        Validate PDF file.
        
        Args:
            pdf_data: PDF file bytes
            
        Returns:
            PDFValidationResult with validation status and metadata
        """
        errors = []
        warnings = []
        
        # File size validation
        file_size = len(pdf_data)
        if file_size < self.min_file_size:
            errors.append(f"File too small: {file_size} bytes (minimum: {self.min_file_size} bytes)")
            return PDFValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                file_size=file_size,
                page_count=0,
            )
        
        if file_size > self.max_file_size:
            errors.append(f"File too large: {file_size} bytes (maximum: {self.max_file_size} bytes)")
            return PDFValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                file_size=file_size,
                page_count=0,
            )
        
        # Try to open PDF
        try:
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        except Exception as e:
            errors.append(f"Invalid PDF file: {str(e)}")
            return PDFValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                file_size=file_size,
                page_count=0,
            )
        
        try:
            page_count = len(pdf_document)
            
            # Page count validation
            if page_count == 0:
                errors.append("PDF has no pages")
            elif page_count > self.max_page_count:
                errors.append(f"Too many pages: {page_count} (maximum: {self.max_page_count})")
            
            # Get boxes from first page (assuming all pages should have same boxes)
            first_page = pdf_document[0] if page_count > 0 else None
            
            trimbox = None
            bleedbox = None
            mediabox = None
            color_space = None
            is_cmyk = False
            
            if first_page:
                # Get boxes
                mediabox_rect = first_page.mediabox
                mediabox = PDFBox(
                    x0=mediabox_rect.x0,
                    y0=mediabox_rect.y0,
                    x1=mediabox_rect.x1,
                    y1=mediabox_rect.y1,
                )
                
                # Try to get trimbox (may not exist)
                trimbox_rect = first_page.rect  # Default to page rect
                if hasattr(first_page, "trimbox") and first_page.trimbox:
                    trimbox_rect = first_page.trimbox
                else:
                    # Try to get from cropbox as fallback
                    if hasattr(first_page, "cropbox") and first_page.cropbox:
                        trimbox_rect = first_page.cropbox
                
                trimbox = PDFBox(
                    x0=trimbox_rect.x0,
                    y0=trimbox_rect.y0,
                    x1=trimbox_rect.x1,
                    y1=trimbox_rect.y1,
                )
                
                # Try to get bleedbox (may not exist)
                if hasattr(first_page, "bleedbox") and first_page.bleedbox:
                    bleedbox_rect = first_page.bleedbox
                    bleedbox = PDFBox(
                        x0=bleedbox_rect.x0,
                        y0=bleedbox_rect.y0,
                        x1=bleedbox_rect.x1,
                        y1=bleedbox_rect.y1,
                    )
                else:
                    warnings.append("Bleedbox not found in PDF")
                
                # Color space: metadata hints, then page streams + image dicts (PyMuPDF).
                try:
                    pdf_metadata = pdf_document.metadata
                    if pdf_metadata:
                        producer = str(pdf_metadata.get("producer", "")).lower()
                        creator = str(pdf_metadata.get("creator", "")).lower()
                        profile = f"{producer} {creator}"
                        if "cmyk" in profile:
                            is_cmyk = True
                            color_space = "CMYK"
                        elif "rgb" in profile or "srgb" in profile:
                            color_space = "RGB"

                    if not color_space:
                        color_space = "Unknown"

                    color_space, is_cmyk = augment_color_space_from_content(
                        pdf_document,
                        first_page,
                        color_space,
                        is_cmyk,
                    )

                except Exception as e:
                    logger.warning(f"Error checking color space: {e}")
                    if self.require_cmyk:
                        warnings.append(f"Could not verify color space: {str(e)}")
            
            # CMYK requirement check
            if self.require_cmyk and color_space == "RGB":
                errors.append("PDF must use CMYK color space")
            
            # Validate boxes
            if trimbox and mediabox:
                if trimbox.x1 > mediabox.x1 or trimbox.y1 > mediabox.y1:
                    errors.append("Trimbox extends beyond mediabox")
                if trimbox.x0 < mediabox.x0 or trimbox.y0 < mediabox.y0:
                    errors.append("Trimbox extends beyond mediabox")
            
            if bleedbox and trimbox:
                if bleedbox.x1 < trimbox.x1 or bleedbox.y1 < trimbox.y1:
                    warnings.append("Bleedbox may be smaller than trimbox")
                if bleedbox.x0 > trimbox.x0 or bleedbox.y0 > trimbox.y0:
                    warnings.append("Bleedbox may be smaller than trimbox")
            
            # Additional metadata
            pdf_metadata = pdf_document.metadata if pdf_document.metadata else {}
            metadata = {
                "title": pdf_metadata.get("title", ""),
                "author": pdf_metadata.get("author", ""),
                "subject": pdf_metadata.get("subject", ""),
                "creator": pdf_metadata.get("creator", ""),
                "producer": pdf_metadata.get("producer", ""),
                "creation_date": pdf_metadata.get("creationDate", ""),
                "modification_date": pdf_metadata.get("modDate", ""),
            }
            
            is_valid = len(errors) == 0

            base = PDFValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                file_size=file_size,
                page_count=page_count,
                trimbox=trimbox,
                bleedbox=bleedbox,
                mediabox=mediabox,
                color_space=color_space,
                is_cmyk=is_cmyk,
                metadata=metadata,
            )
            return enrich_pdf_validation_result(base, trimbox, mediabox, bleedbox)
        
        finally:
            pdf_document.close()
    
    def validate_file(self, file: BinaryIO) -> PDFValidationResult:
        """
        Validate PDF from file-like object.
        
        Args:
            file: File-like object containing PDF data
            
        Returns:
            PDFValidationResult with validation status and metadata
        """
        pdf_data = file.read()
        return self.validate(pdf_data)


# Singleton instance
_pdf_validator: Optional[PDFValidator] = None


def get_pdf_validator() -> PDFValidator:
    """Get PDF validator singleton instance."""
    global _pdf_validator
    if _pdf_validator is None:
        _pdf_validator = PDFValidator()
    return _pdf_validator

