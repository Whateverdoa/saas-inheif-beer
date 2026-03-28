"""Derive physical mm dimensions and form hints from PDF boxes (PyMuPDF points)."""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

from app.models.beer_label import STANDARD_BEER_LABEL_TYPES, BeerLabelType
from app.models.pdf_validation import PDFBox, PDFValidationResult


def pt_to_mm(pt: float) -> float:
    """Convert PDF points (1/72 inch) to millimetres."""
    return round(pt * (25.4 / 72.0), 2)


def box_width_height_mm(box: PDFBox) -> Tuple[float, float]:
    """Width and height in mm from axis-aligned box (PDF user space)."""
    w_pt = abs(box.x1 - box.x0)
    h_pt = abs(box.y1 - box.y0)
    return pt_to_mm(w_pt), pt_to_mm(h_pt)


def suggest_shape_id(width_mm: float, height_mm: float) -> str:
    """
    Map trim aspect ratio to order-form shape ids: rond, ovaal, rechthoek, custom.

    Typical rectangular beer labels (e.g. 80×100 mm) stay rechthoek; near-square
    trims map to rond; moderate aspect between those bands maps to ovaal.
    """
    if width_mm <= 0 or height_mm <= 0:
        return "custom"
    lo, hi = min(width_mm, height_mm), max(width_mm, height_mm)
    ratio = lo / hi if hi else 0
    elong = hi / lo if lo else 0
    if ratio >= 0.93:
        return "rond"
    if ratio < 0.82 or elong > 1.5:
        return "rechthoek"
    return "ovaal"


def nearest_standard_label(
    width_mm: float,
    height_mm: float,
    max_total_delta_mm: float = 18.0,
) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Find closest catalog preset by L1 distance, allowing 90° swap.

    Returns
    -------
    id, name, distance_mm — id/name None if no preset within max_total_delta_mm.
    """
    best_id: Optional[str] = None
    best_name: Optional[str] = None
    best_d = math.inf

    for lt in STANDARD_BEER_LABEL_TYPES:
        d = _preset_distance(width_mm, height_mm, lt)
        if d < best_d:
            best_d = d
            best_id = lt.id
            best_name = lt.name

    if best_id is not None and best_d <= max_total_delta_mm:
        return best_id, best_name, round(best_d, 2)
    return None, None, round(best_d, 2) if best_d != math.inf else None


def _preset_distance(w_mm: float, h_mm: float, lt: BeerLabelType) -> float:
    a = abs(w_mm - lt.width_mm) + abs(h_mm - lt.height_mm)
    b = abs(w_mm - lt.height_mm) + abs(h_mm - lt.width_mm)
    return min(a, b)


def bleed_insets_mm(trim: PDFBox, bleed: PDFBox) -> Optional[Dict[str, float]]:
    """Approximate bleed extension beyond trim in mm (left, right, bottom, top)."""
    keys = ("left", "right", "bottom", "top")
    left = pt_to_mm(trim.x0 - bleed.x0)
    right = pt_to_mm(bleed.x1 - trim.x1)
    bottom = pt_to_mm(trim.y0 - bleed.y0)
    top = pt_to_mm(bleed.y1 - trim.y1)
    return dict(zip(keys, (round(v, 2) for v in (left, right, bottom, top))))


def enrich_pdf_validation_result(
    base: PDFValidationResult,
    trimbox: Optional[PDFBox],
    mediabox: Optional[PDFBox],
    bleedbox: Optional[PDFBox],
) -> PDFValidationResult:
    """Return a copy of base with physical dimensions and catalog match filled in."""
    data = base.model_dump()

    tw = th = mw = mh = None
    dim_display: Optional[str] = None
    shape = "custom"
    bleed_mm: Optional[Dict[str, float]] = None

    if trimbox:
        tw, th = box_width_height_mm(trimbox)
        dim_display = f"{int(round(tw))} × {int(round(th))}"
        shape = suggest_shape_id(tw, th)

    if mediabox:
        mw, mh = box_width_height_mm(mediabox)

    if trimbox and bleedbox:
        bleed_mm = bleed_insets_mm(trimbox, bleedbox)

    mid: Optional[str] = None
    mname: Optional[str] = None
    mdist: Optional[float] = None
    if tw is not None and th is not None:
        mid, mname, mdist = nearest_standard_label(tw, th)

    data.update(
        {
            "trim_width_mm": tw,
            "trim_height_mm": th,
            "media_width_mm": mw,
            "media_height_mm": mh,
            "bleed_insets_mm": bleed_mm,
            "dimensions_display": dim_display,
            "suggested_shape": shape,
            "matched_standard_label_type_id": mid,
            "matched_standard_label_name": mname,
            "match_distance_mm": mdist,
        }
    )
    return PDFValidationResult(**data)
