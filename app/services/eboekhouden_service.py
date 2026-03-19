"""e-boekhouden API integration service."""
import os
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import httpx

from app.models.invoice import TransactionMapping

logger = logging.getLogger("uvicorn.error")

# e-boekhouden API configuration
EBOEKHOUDEN_API_BASE_URL = "https://api.e-boekhouden.nl/v1"
EBOEKHOUDEN_API_KEY = os.getenv("EBOEKHOUDEN_API_KEY", "")
EBOEKHOUDEN_COMPANY_ID = os.getenv("EBOEKHOUDEN_COMPANY_ID", "")
EBOEKHOUDEN_SYNC_ENABLED = os.getenv("EBOEKHOUDEN_SYNC_ENABLED", "false").lower() == "true"


class EBoekhoudenClient:
    """Client for e-boekhouden API integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        company_id: Optional[str] = None,
        enabled: bool = False,
    ):
        self.api_key = api_key or EBOEKHOUDEN_API_KEY
        self.company_id = company_id or EBOEKHOUDEN_COMPANY_ID
        self.enabled = enabled or EBOEKHOUDEN_SYNC_ENABLED
        self.base_url = EBOEKHOUDEN_API_BASE_URL

        if not self.enabled:
            logger.info("eboekhouden.disabled", extra={"msg": "e-boekhouden sync is disabled"})
        elif not self.api_key or not self.company_id:
            logger.warning(
                "eboekhouden.missing_config",
                extra={"msg": "e-boekhouden API key or company ID not configured"},
            )

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Company-ID": self.company_id,
        }

    async def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to e-boekhouden API."""
        if not self.enabled:
            raise ValueError("e-boekhouden sync is disabled")

        if not self.api_key or not self.company_id:
            raise ValueError("e-boekhouden API key or company ID not configured")

        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(method, url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "eboekhouden.api_error",
                    extra={
                        "status_code": e.response.status_code,
                        "response": e.response.text,
                    },
                )
                raise
            except Exception as e:
                logger.exception("eboekhouden.request_error", extra={"error": str(e)})
                raise

    async def create_transaction(self, transaction: TransactionMapping) -> Dict[str, Any]:
        """
        Create a transaction in e-boekhouden.

        Args:
            transaction: Transaction mapping object

        Returns:
            Dictionary with e-boekhouden transaction ID and status
        """
        try:
            # Map transaction to e-boekhouden format
            eboekhouden_data = self._map_to_eboekhouden_format(transaction)

            # Make API request
            result = await self._make_request("POST", "transactions", eboekhouden_data)

            logger.info(
                "eboekhouden.transaction_created",
                extra={
                    "transaction_id": transaction.transaction_id,
                    "eboekhouden_id": result.get("id"),
                },
            )

            return {
                "success": True,
                "eboekhouden_id": result.get("id"),
                "transaction_id": transaction.transaction_id,
            }
        except Exception as e:
            logger.exception(
                "eboekhouden.create_transaction_error",
                extra={"transaction_id": transaction.transaction_id, "error": str(e)},
            )
            return {
                "success": False,
                "error": str(e),
                "transaction_id": transaction.transaction_id,
            }

    def _map_to_eboekhouden_format(self, transaction: TransactionMapping) -> Dict[str, Any]:
        """
        Map transaction to e-boekhouden API format.

        Note: This is a placeholder implementation. Adjust based on actual
        e-boekhouden API documentation.
        """
        return {
            "date": transaction.date.strftime("%Y-%m-%d"),
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "description": transaction.description,
            "customer_name": transaction.customer_name or "",
            "customer_email": transaction.customer_email or "",
            "payment_provider": transaction.provider,
            "payment_id": transaction.transaction_id,
            "invoice_id": transaction.invoice_id,
            "metadata": transaction.metadata,
        }

    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an invoice in e-boekhouden.

        Args:
            invoice_data: Invoice data dictionary

        Returns:
            Dictionary with e-boekhouden invoice ID and status
        """
        try:
            # Map invoice to e-boekhouden format
            eboekhouden_invoice = self._map_invoice_to_eboekhouden_format(invoice_data)

            # Make API request
            result = await self._make_request("POST", "invoices", eboekhouden_invoice)

            logger.info(
                "eboekhouden.invoice_created",
                extra={
                    "invoice_id": invoice_data.get("invoice_id"),
                    "eboekhouden_id": result.get("id"),
                },
            )

            return {
                "success": True,
                "eboekhouden_id": result.get("id"),
                "invoice_id": invoice_data.get("invoice_id"),
            }
        except Exception as e:
            logger.exception(
                "eboekhouden.create_invoice_error",
                extra={"invoice_id": invoice_data.get("invoice_id"), "error": str(e)},
            )
            return {
                "success": False,
                "error": str(e),
                "invoice_id": invoice_data.get("invoice_id"),
            }

    def _map_invoice_to_eboekhouden_format(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map invoice to e-boekhouden API format.

        Note: This is a placeholder implementation. Adjust based on actual
        e-boekhouden API documentation.
        """
        return {
            "invoice_number": invoice_data.get("invoice_number"),
            "date": invoice_data.get("issue_date"),
            "due_date": invoice_data.get("due_date"),
            "customer_name": invoice_data.get("customer_name"),
            "customer_email": invoice_data.get("customer_email"),
            "customer_address": invoice_data.get("customer_address"),
            "items": [
                {
                    "description": item.get("description"),
                    "quantity": float(item.get("quantity", 1)),
                    "unit_price": float(item.get("unit_price", 0)),
                    "vat_rate": float(item.get("vat_rate", 0.21)),
                }
                for item in invoice_data.get("items", [])
            ],
            "subtotal": float(invoice_data.get("subtotal_excl_vat", 0)),
            "vat_total": float(invoice_data.get("total_vat", 0)),
            "total": float(invoice_data.get("total_incl_vat", 0)),
            "currency": invoice_data.get("currency", "EUR"),
            "payment_provider": invoice_data.get("payment_provider"),
            "payment_id": invoice_data.get("payment_id"),
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to e-boekhouden API."""
        try:
            result = await self._make_request("GET", "test")
            return {"success": True, "message": "Connection successful", "data": result}
        except Exception as e:
            logger.exception("eboekhouden.test_connection_error", extra={"error": str(e)})
            return {"success": False, "error": str(e)}


# Singleton instance
_eboekhouden_client: Optional[EBoekhoudenClient] = None


def get_eboekhouden_client() -> EBoekhoudenClient:
    """Get the e-boekhouden client singleton."""
    global _eboekhouden_client
    if _eboekhouden_client is None:
        _eboekhouden_client = EBoekhoudenClient()
    return _eboekhouden_client

