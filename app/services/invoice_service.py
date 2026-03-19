"""Invoice generation and management service."""
import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from jinja2 import Template
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.services.eboekhouden_service import get_eboekhouden_client

logger = logging.getLogger("uvicorn.error")

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


class InvoiceService:
    """Service for generating and managing invoices."""

    def __init__(self):
        self._invoice_storage: Dict[str, Invoice] = {}
        self._invoice_counter = 0

    def _get_next_invoice_number(self) -> str:
        """Generate next invoice number."""
        self._invoice_counter += 1
        year = datetime.now().year
        return f"INV-{year}-{self._invoice_counter:04d}"

    def _get_company_info(self) -> Dict[str, str]:
        """Get company information from environment variables."""
        return {
            "company_name": os.getenv("COMPANY_NAME", "Your Company Name"),
            "company_kvk": os.getenv("COMPANY_KVK_NUMBER", ""),
            "company_btw": os.getenv("COMPANY_BTW_NUMBER", ""),
            "company_address": os.getenv("COMPANY_ADDRESS", ""),
            "company_bank_account": os.getenv("COMPANY_BANK_ACCOUNT", ""),
            "company_email": os.getenv("COMPANY_EMAIL", "contact@example.com"),
        }

    def _get_branding_info(self) -> Dict[str, str]:
        """Get branding information from environment variables."""
        return {
            "logo_url": os.getenv("BRANDING_LOGO_URL", ""),
            "primary_color": os.getenv("BRANDING_PRIMARY_COLOR", "#2563eb"),
            "secondary_color": os.getenv("BRANDING_SECONDARY_COLOR", "#64748b"),
            "font_family": os.getenv("BRANDING_FONT_FAMILY", "Inter"),
        }

    def create_invoice_from_payment(
        self,
        payment_id: str,
        provider: str,
        amount: Decimal,
        currency: str,
        customer_name: str,
        customer_email: Optional[str] = None,
        customer_address: Optional[str] = None,
        description: str = "Service payment",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Invoice:
        """
        Create an invoice from payment information.

        Args:
            payment_id: Payment ID from provider
            provider: Payment provider (stripe, polar)
            amount: Payment amount (including VAT)
            currency: Currency code
            customer_name: Customer name
            customer_email: Customer email (optional)
            customer_address: Customer address (optional)
            description: Invoice description
            metadata: Additional metadata

        Returns:
            Created Invoice object
        """
        invoice_id = str(uuid.uuid4())
        invoice_number = self._get_next_invoice_number()
        company_info = self._get_company_info()

        # Calculate VAT (assuming 21% for Netherlands)
        vat_rate = Decimal("0.21")
        total_incl_vat = amount
        total_vat = total_incl_vat - (total_incl_vat / (Decimal("1") + vat_rate))
        subtotal_excl_vat = total_incl_vat - total_vat

        # Create invoice item
        item = InvoiceItem(
            description=description,
            quantity=Decimal("1"),
            unit_price=subtotal_excl_vat,
            vat_rate=vat_rate,
            total_excl_vat=subtotal_excl_vat,
            total_incl_vat=total_incl_vat,
        )

        # Create invoice
        invoice = Invoice(
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_address=customer_address,
            company_name=company_info["company_name"],
            company_kvk=company_info["company_kvk"] or None,
            company_btw=company_info["company_btw"] or None,
            company_address=company_info["company_address"] or None,
            company_bank_account=company_info["company_bank_account"] or None,
            issue_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            status=InvoiceStatus.PAID if provider else InvoiceStatus.PENDING,
            items=[item],
            subtotal_excl_vat=subtotal_excl_vat,
            total_vat=total_vat,
            total_incl_vat=total_incl_vat,
            currency=currency,
            payment_provider=provider,
            payment_id=payment_id,
            paid_at=datetime.now() if provider else None,
            metadata=metadata or {},
        )

        # Store invoice
        self._invoice_storage[invoice_id] = invoice

        logger.info(
            "invoice.created",
            extra={
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "amount": float(total_incl_vat),
                "provider": provider,
            },
        )

        return invoice

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID."""
        return self._invoice_storage.get(invoice_id)

    def list_invoices(
        self, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """List invoices with pagination."""
        invoices = list(self._invoice_storage.values())
        # Sort by issue_date descending
        invoices.sort(key=lambda x: x.issue_date, reverse=True)
        total = len(invoices)
        paginated = invoices[offset : offset + limit]
        return {
            "invoices": [invoice.dict() for invoice in paginated],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def render_invoice_html(self, invoice: Invoice) -> str:
        """Render invoice as HTML."""
        template_file = TEMPLATE_DIR / "invoice.html"
        if not template_file.exists():
            raise FileNotFoundError(f"Invoice template not found: {template_file}")

        with open(template_file, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        company_info = self._get_company_info()
        branding_info = self._get_branding_info()

        # Prepare template context
        context = {
            **company_info,
            **branding_info,
            "invoice_number": invoice.invoice_number,
            "customer_name": invoice.customer_name,
            "customer_email": invoice.customer_email or "",
            "customer_address": invoice.customer_address or "",
            "issue_date": invoice.issue_date.strftime("%d-%m-%Y"),
            "due_date": invoice.due_date.strftime("%d-%m-%Y"),
            "status": invoice.status.value,
            "items": [
                {
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "vat_rate": float(item.vat_rate),
                    "total_incl_vat": float(item.total_incl_vat),
                }
                for item in invoice.items
            ],
            "subtotal_excl_vat": float(invoice.subtotal_excl_vat),
            "total_vat": float(invoice.total_vat),
            "total_incl_vat": float(invoice.total_incl_vat),
            "payment_provider": invoice.payment_provider or "",
        }

        return template.render(**context)

    async def sync_to_eboekhouden(self, invoice: Invoice) -> Dict[str, Any]:
        """Sync invoice to e-boekhouden."""
        try:
            eboekhouden_client = get_eboekhouden_client()

            # Convert invoice to dictionary
            invoice_data = invoice.dict()

            # Create invoice in e-boekhouden
            result = await eboekhouden_client.create_invoice(invoice_data)

            if result.get("success"):
                # Update invoice
                invoice.eboekhouden_synced = True
                invoice.eboekhouden_id = result.get("eboekhouden_id")
                self._invoice_storage[invoice.invoice_id] = invoice

                logger.info(
                    "invoice.synced_to_eboekhouden",
                    extra={
                        "invoice_id": invoice.invoice_id,
                        "eboekhouden_id": result.get("eboekhouden_id"),
                    },
                )

            return result
        except Exception as e:
            logger.exception(
                "invoice.sync_error",
                extra={"invoice_id": invoice.invoice_id, "error": str(e)},
            )
            return {"success": False, "error": str(e)}


# Singleton instance
_invoice_service: Optional[InvoiceService] = None


def get_invoice_service() -> InvoiceService:
    """Get the invoice service singleton."""
    global _invoice_service
    if _invoice_service is None:
        _invoice_service = InvoiceService()
    return _invoice_service

