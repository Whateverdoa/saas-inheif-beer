"""KVK lookup service tests (mock, no API key)."""
import pytest

from app.services.kvk_service import lookup_kvk, normalize_kvk_input


def test_normalize_kvk_input_valid() -> None:
    n, err = normalize_kvk_input(" 12345678 ")
    assert err is None
    assert n == "12345678"


def test_normalize_kvk_input_invalid() -> None:
    n, err = normalize_kvk_input("123")
    assert n is None
    assert err is not None


@pytest.mark.asyncio
async def test_lookup_mock_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KVK_API_KEY", raising=False)
    monkeypatch.delenv("KVK_USE_MOCK", raising=False)
    data = await lookup_kvk("12345678")
    assert data["kvk_number"] == "12345678"
    assert "Bakkerij" in data["name"]
    assert data["source"] == "mock"


@pytest.mark.asyncio
async def test_lookup_fails_unknown_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KVK_API_KEY", raising=False)
    monkeypatch.delenv("KVK_USE_MOCK", raising=False)
    with pytest.raises(LookupError):
        await lookup_kvk("99999999")
