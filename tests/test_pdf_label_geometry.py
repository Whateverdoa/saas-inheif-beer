"""Unit tests for PDF label geometry helpers (no PyMuPDF required)."""

from __future__ import annotations

from app.models.pdf_validation import PDFBox, PDFValidationResult
from app.services.pdf_label_geometry import (
    box_width_height_mm,
    enrich_pdf_validation_result,
    nearest_standard_label,
    suggest_shape_id,
)


def test_pt_mm_roundtrip_scale() -> None:
    box = PDFBox(x0=0, y0=0, x1=72, y1=72)
    w, h = box_width_height_mm(box)
    assert w == 25.4
    assert h == 25.4


def test_suggest_shape_rectangle() -> None:
    assert suggest_shape_id(100, 40) == "rechthoek"


def test_suggest_shape_roundish() -> None:
    assert suggest_shape_id(100, 95) == "rond"


def test_suggest_shape_oval() -> None:
    assert suggest_shape_id(100, 88) == "ovaal"


def test_nearest_match_front_body() -> None:
    mid, name, dist = nearest_standard_label(80, 100, max_total_delta_mm=20)
    assert mid == "front-body-standard"
    assert name is not None
    assert dist is not None
    assert dist <= 1


def test_enrich_adds_dimensions() -> None:
    trim = PDFBox(x0=0, y0=0, x1=72 * 80 / 25.4, y1=72 * 100 / 25.4)
    media = trim
    base = PDFValidationResult(
        is_valid=True,
        errors=[],
        warnings=[],
        file_size=5000,
        page_count=1,
        trimbox=trim,
        bleedbox=None,
        mediabox=media,
        color_space="CMYK",
        is_cmyk=True,
        metadata={},
    )
    out = enrich_pdf_validation_result(base, trim, media, None)
    assert out.trim_width_mm is not None
    assert out.trim_height_mm is not None
    assert out.dimensions_display == "80 × 100"
    assert out.suggested_shape == "rechthoek"
    assert out.matched_standard_label_type_id == "front-body-standard"
