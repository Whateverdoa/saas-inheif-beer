"""Unit tests for pragmatic CMYK behavior in PDF validator."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import pdf_validator


class _Rect:
    def __init__(self, x0: float, y0: float, x1: float, y1: float) -> None:
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


class _FakePage:
    def __init__(self) -> None:
        self.mediabox = _Rect(0, 0, 100, 100)
        self.rect = _Rect(0, 0, 100, 100)
        self.trimbox = _Rect(0, 0, 100, 100)
        self.cropbox = _Rect(0, 0, 100, 100)
        self.bleedbox = None


class _FakeDoc:
    def __init__(self, metadata: dict[str, str]) -> None:
        self.metadata = metadata
        self._page = _FakePage()

    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int) -> _FakePage:
        return self._page

    def close(self) -> None:
        return None


def _install_fake_fitz(monkeypatch, metadata: dict[str, str]) -> None:
    class _FakeFitz:
        @staticmethod
        def open(stream: bytes, filetype: str) -> _FakeDoc:
            return _FakeDoc(metadata=metadata)

    monkeypatch.setattr(pdf_validator, "fitz", _FakeFitz)


def test_unknown_color_space_warns_but_does_not_fail(monkeypatch) -> None:
    _install_fake_fitz(monkeypatch, {"producer": "unknown producer"})
    validator = pdf_validator.PDFValidator(min_file_size=1, require_cmyk=True)

    result = validator.validate(b"x" * 2048)

    assert result.is_valid is True
    assert "PDF must use CMYK color space" not in result.errors
    assert any("Could not verify CMYK" in warning for warning in result.warnings)
    assert result.color_space == "Unknown"


def test_explicit_rgb_still_fails_when_cmyk_required(monkeypatch) -> None:
    _install_fake_fitz(monkeypatch, {"producer": "Adobe RGB workflow"})
    validator = pdf_validator.PDFValidator(min_file_size=1, require_cmyk=True)

    result = validator.validate(b"x" * 2048)

    assert result.is_valid is False
    assert "PDF must use CMYK color space" in result.errors
    assert result.color_space == "RGB"
