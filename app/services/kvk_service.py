"""KVK (Dutch Chamber of Commerce) company lookup via Basisprofiel API."""
from __future__ import annotations

import logging
import os
import re
from typing import Any, Optional

import httpx

logger = logging.getLogger("uvicorn.error")

KVK_MOCK: dict[str, dict[str, Any]] = {
    "12345678": {
        "kvk_number": "12345678",
        "name": "Bakkerij De Gouden Korst B.V.",
        "statutaire_naam": None,
        "rechtsvorm": None,
        "street": "Ginnekenweg",
        "house_number": "142",
        "house_number_addition": "A",
        "postal_code": "4835 NH",
        "city": "Breda",
        "full_address": "Ginnekenweg 142A, 4835 NH Breda",
        "source": "mock",
    },
    "69599084": {
        "kvk_number": "69599084",
        "name": "Bol.com B.V.",
        "statutaire_naam": None,
        "rechtsvorm": None,
        "street": "Papendorpseweg",
        "house_number": "100",
        "house_number_addition": None,
        "postal_code": "3528 BJ",
        "city": "Utrecht",
        "full_address": "Papendorpseweg 100, 3528 BJ Utrecht",
        "source": "mock",
    },
}


def normalize_kvk_input(raw: str) -> tuple[Optional[str], Optional[str]]:
    """Return (8-digit KVK number, error message)."""
    n = re.sub(r"\s+", "", raw or "")
    if not n:
        return None, "KVK nummer ontbreekt."
    if not re.fullmatch(r"\d{8}", n):
        return None, "KVK nummer moet exact 8 cijfers zijn."
    return n, None


def _compose_address(
    straatnaam: Optional[str],
    huisnummer: Optional[str],
    toevoeging: Optional[str],
    postcode: Optional[str],
    plaats: Optional[str],
    volledig: Optional[str],
) -> dict[str, Any]:
    if volledig and volledig.strip():
        full = volledig.strip()
    else:
        parts: list[str] = []
        line1 = " ".join(
            p
            for p in [
                (straatnaam or "").strip(),
                (huisnummer or "").strip(),
                (toevoeging or "").strip(),
            ]
            if p
        )
        if line1:
            parts.append(line1)
        line2 = " ".join(p for p in [(postcode or "").strip(), (plaats or "").strip()] if p)
        if line2:
            parts.append(line2)
        full = ", ".join(parts) if parts else ""
    return {
        "street": straatnaam,
        "house_number": huisnummer,
        "house_number_addition": toevoeging,
        "postal_code": postcode,
        "city": plaats,
        "full_address": full,
    }


def _pick_address(addresses: list[dict[str, Any]]) -> dict[str, Any]:
    for addr in addresses:
        t = (addr.get("type") or "").lower()
        if "bezoek" in t:
            return addr
    return addresses[0] if addresses else {}


def normalize_basisprofiel_response(data: dict[str, Any]) -> dict[str, Any]:
    """Map Basisprofiel JSON to a flat DTO for the frontend."""
    kvk_num = data.get("kvkNummer") or ""
    naam = (
        data.get("naam")
        or data.get("statutaireNaam")
        or ""
    )
    statutaire = data.get("statutaireNaam")
    rechtsvorm = None
    hv = data.get("hoofdvestiging") or {}
    if isinstance(hv, dict):
        eerste = hv.get("eersteHandelsnaam")
        if eerste and not naam:
            naam = eerste
        adressen = hv.get("adressen") or []
        if adressen:
            a = _pick_address(adressen)
            addr = _compose_address(
                a.get("straatnaam"),
                a.get("huisnummer"),
                a.get("huisnummerToevoeging") or a.get("huisletter"),
                a.get("postcode"),
                a.get("plaats"),
                a.get("volledigAdres"),
            )
        else:
            addr = _compose_address(None, None, None, None, None, None)
        owner = data.get("eigenaar") or {}
        if isinstance(owner, dict) and not hv.get("adressen"):
            rechtsvorm = owner.get("rechtsvorm") or owner.get("uitgebreideRechtsvorm")
            oa = owner.get("adressen") or []
            if oa:
                a = _pick_address(oa)
                addr = _compose_address(
                    a.get("straatnaam"),
                    a.get("huisnummer"),
                    a.get("huisnummerToevoeging") or a.get("huisletter"),
                    a.get("postcode"),
                    a.get("plaats"),
                    a.get("volledigAdres"),
                )
    else:
        addr = _compose_address(None, None, None, None, None, None)
        rechtsvorm = None

    if rechtsvorm is None and isinstance(data.get("eigenaar"), dict):
        rechtsvorm = (data["eigenaar"] or {}).get("rechtsvorm")

    return {
        "kvk_number": kvk_num,
        "name": naam,
        "statutaire_naam": statutaire,
        "rechtsvorm": rechtsvorm,
        **addr,
        "source": "kvk_api",
    }


async def lookup_kvk(kvk_nummer: str) -> dict[str, Any]:
    """
    Look up company by 8-digit KVK number.
    Uses official Basisprofiel API when ``KVK_API_KEY`` is set.
    Without a key, only built-in test numbers (12345678, 69599084) work.
    Set ``KVK_USE_MOCK=true`` to force mock-only (useful in tests).
    """
    normalized, err = normalize_kvk_input(kvk_nummer)
    if err or not normalized:
        raise ValueError(err or "Invalid KVK number")

    use_mock = os.getenv("KVK_USE_MOCK", "").lower() in ("1", "true", "yes")
    api_key = (os.getenv("KVK_API_KEY") or "").strip()

    if use_mock:
        if normalized in KVK_MOCK:
            return dict(KVK_MOCK[normalized])
        raise LookupError(
            f"Mock-modus: alleen test-KVK {', '.join(sorted(KVK_MOCK.keys()))}."
        )

    if not api_key:
        if normalized in KVK_MOCK:
            return dict(KVK_MOCK[normalized])
        raise LookupError(
            "Geen KVK API key. Zet KVK_API_KEY (zie developers.kvk.nl) "
            "of gebruik testnummer 12345678 of 69599084."
        )

    base = (os.getenv("KVK_API_BASE") or "https://api.kvk.nl").rstrip("/")
    url = f"{base}/api/v1/basisprofielen"
    headers = {"apikey": api_key}

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            url,
            params={"kvkNummer": normalized, "geoData": "False"},
            headers=headers,
        )

    if r.status_code == 404:
        raise LookupError(f"Geen bedrijf gevonden voor KVK {normalized}.")
    if r.status_code == 401 or r.status_code == 403:
        logger.warning("KVK API auth failed (status %s)", r.status_code)
        raise PermissionError("KVK API authenticatie mislukt. Controleer KVK_API_KEY.")
    if not r.is_success:
        logger.error("KVK API error %s: %s", r.status_code, r.text[:500])
        raise RuntimeError(f"KVK API fout ({r.status_code}). Probeer later opnieuw.")

    body = r.json()
    if not isinstance(body, dict):
        raise RuntimeError("Onverwacht antwoord van KVK API.")

    return normalize_basisprofiel_response(body)
