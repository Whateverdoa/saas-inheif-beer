"""Infer print color space from PDF page content (streams + images), not only metadata."""

from __future__ import annotations

import logging
from typing import Any, Optional, Tuple

logger = logging.getLogger("uvicorn.error")

# PyMuPDF Page.get_images(full=True): index 5 = colorspace (1 Gray, 3 RGB, 4 CMYK)
_CS_GRAY = 1
_CS_RGB = 3
_CS_CMYK = 4


def _concat_page_streams(doc: Any, page: Any) -> bytes:
    chunks: list[bytes] = []
    try:
        xrefs = page.get_contents()
    except Exception as e:
        logger.debug("get_contents failed: %s", e)
        return b""
    for xref in xrefs:
        if not xref:
            continue
        try:
            chunks.append(doc.xref_stream(xref))
        except Exception as e:
            logger.debug("xref_stream %s failed: %s", xref, e)
    return b"".join(chunks)


def _stream_suggests_cmyk(raw: bytes) -> bool:
    if not raw:
        return False
    # Literal PDF operators / color space names (common in print PDFs)
    if b"DeviceCMYK" in raw:
        return True
    if b"/DefaultCMYK" in raw:
        return True
    return False


def _stream_suggests_rgb(raw: bytes) -> bool:
    if not raw:
        return False
    return b"DeviceRGB" in raw or b"/DefaultRGB" in raw


def _images_color_flags(page: Any) -> Tuple[bool, bool]:
    """Return (has_cmyk_image, has_rgb_image) from embedded images."""
    cmyk = rgb = False
    try:
        items = page.get_images(full=True)
    except Exception as e:
        logger.debug("get_images failed: %s", e)
        return False, False
    for item in items:
        if not item or len(item) < 6:
            continue
        cs = item[5]
        if cs == _CS_CMYK:
            cmyk = True
        elif cs == _CS_RGB:
            rgb = True
        elif cs == _CS_GRAY:
            pass
        elif isinstance(cs, str) and "CMYK" in cs.upper():
            cmyk = True
        elif isinstance(cs, str) and "RGB" in cs.upper():
            rgb = True
    return cmyk, rgb


def augment_color_space_from_content(
    doc: Any,
    page: Any,
    prior_color_space: Optional[str],
    prior_is_cmyk: bool,
) -> Tuple[Optional[str], bool]:
    """
    Refine color_space / is_cmyk using page streams and image dicts.

    Trusts explicit metadata first: CMYK or RGB from producer/creator is kept.
    """
    if prior_is_cmyk or prior_color_space == "CMYK":
        return "CMYK", True
    if prior_color_space == "RGB":
        return "RGB", False

    raw = _concat_page_streams(doc, page)
    stream_cmyk = _stream_suggests_cmyk(raw)
    stream_rgb = _stream_suggests_rgb(raw)
    img_cmyk, img_rgb = _images_color_flags(page)

    if stream_cmyk or img_cmyk:
        return "CMYK", True
    if stream_rgb or img_rgb:
        return "RGB", False
    return "Unknown", False
