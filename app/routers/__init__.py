"""API routers — submodules load on demand (``from app.routers import beer`` only imports ``beer``)."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "admin",
    "auth",
    "beer",
    "compliance",
    "credits",
    "invoices",
    "legal",
    "ogos_config",
    "orders",
    "organizations",
    "webhooks",
    "kvk",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        return importlib.import_module(f"app.routers.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
