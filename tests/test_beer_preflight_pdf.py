"""POST /beer/preflight-pdf smoke tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.beer import router as beer_router

_app = FastAPI()
_app.include_router(beer_router)
client = TestClient(_app)


def _minimal_pdf_bytes() -> bytes:
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    n = 0
    while True:
        page = doc.new_page(width=200, height=200)
        page.insert_text((10, 12), f"Preflight line {n}\n" * 30)
        out = doc.tobytes()
        if len(out) >= 1024:
            doc.close()
            return out
        n += 1
        if n > 20:
            doc.close()
            raise RuntimeError("failed to build >=1024 byte PDF for test")


def test_preflight_rejects_non_pdf_extension() -> None:
    r = client.post(
        "/beer/preflight-pdf",
        files={"file": ("label.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 400


def test_preflight_too_small_returns_invalid() -> None:
    r = client.post(
        "/beer/preflight-pdf",
        files={"file": ("small.pdf", b"x" * 100, "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["is_valid"] is False
    assert any("too small" in e.lower() for e in data["errors"])


def test_preflight_minimal_pdf_parses() -> None:
    raw = _minimal_pdf_bytes()
    r = client.post(
        "/beer/preflight-pdf",
        files={"file": ("page.pdf", raw, "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["page_count"] >= 1
    assert data["file_size"] == len(raw)
