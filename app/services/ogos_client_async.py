import os
import logging
from typing import Any, Dict
import httpx
import asyncio
import math

logger = logging.getLogger("uvicorn.error")

OGOS_BASE_URL = os.getenv("OGOS_BASE_URL", "https://api.ogos.example.com")
OGOS_API_KEY = os.getenv("OGOS_API_KEY", "")

DEFAULT_TIMEOUT = 20.0
MAX_ATTEMPTS = 4
INITIAL_BACKOFF = 0.8  # seconds


class OGOSClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or OGOS_BASE_URL).rstrip("/")
        self.api_key = api_key or OGOS_API_KEY

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request_with_retry(self, method: str, url: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        attempt = 0
        exc: Exception | None = None
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            while attempt < MAX_ATTEMPTS:
                try:
                    resp = await client.request(method, url, headers=self._headers(), json=json_data)
                    if 200 <= resp.status_code < 300:
                        return resp.json()
                    if resp.status_code in (429, 500, 502, 503, 504):
                        raise httpx.HTTPStatusError("server_or_rate_error", request=resp.request, response=resp)
                    return {"ok": False, "status": resp.status_code, "error": resp.text}
                except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.HTTPStatusError) as e:
                    exc = e
                    backoff = INITIAL_BACKOFF * math.pow(2, attempt)
                    jitter = 0.2 * backoff
                    sleep_for = backoff + jitter
                    logger.warning("ogos.retrying", extra={"attempt": attempt + 1, "sleep": sleep_for, "error": str(e)})
                    await asyncio.sleep(sleep_for)
                    attempt += 1
                except Exception as e:
                    logger.exception("ogos.unexpected_error")
                    return {"ok": False, "error": str(e)}

        return {"ok": False, "error": str(exc) if exc else "unknown_error"}

    async def submit_paid_order(self, order_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/order"
        payload = {"orderId": order_id, "source": "stripe", "status": "paid"}
        return await self._request_with_retry("POST", url, payload)
