"""Invoice endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any
import logging

from app.dependencies.auth import get_current_user
from app.services.invoice_service import get_invoice_service
from app.models.invoice import Invoice

router = APIRouter(prefix="/invoices", tags=["invoices"])
logger = logging.getLogger("uvicorn.error")

invoice_service = get_invoice_service()


@router.post("/generate")
async def generate_invoice(
    payment_id: str,
    provider: str,
    amount: float,
    currency: str = "EUR",
    customer_name: str = "",
    customer_email: Optional[str] = None,
    customer_address: Optional[str] = None,
    description: str = "Service payment",
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Generate an invoice from payment data.
    
    Protected endpoint requiring Clerk authentication.
    """
    from decimal import Decimal

    try:
        invoice = invoice_service.create_invoice_from_payment(
            payment_id=payment_id,
            provider=provider,
            amount=Decimal(str(amount)),
            currency=currency,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_address=customer_address,
            description=description,
        )

        logger.info(
            "invoice.generated",
            extra={"user_id": user.get("user_id"), "invoice_id": invoice.invoice_id},
        )

        return {"ok": True, "invoice": invoice.dict()}
    except Exception as e:
        logger.exception("invoice.generate_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate invoice",
        )


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get invoice by ID.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        invoice = invoice_service.get_invoice(invoice_id)
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found",
            )
        return {"ok": True, "invoice": invoice.dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("invoice.get_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoice",
        )


@router.get("/{invoice_id}/html")
async def get_invoice_html(
    invoice_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> HTMLResponse:
    """
    Get invoice as HTML.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        invoice = invoice_service.get_invoice(invoice_id)
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found",
            )

        html_content = invoice_service.render_invoice_html(invoice)
        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("invoice.get_html_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to render invoice HTML",
        )


@router.get("")
async def list_invoices(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    List invoices with pagination.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        result = invoice_service.list_invoices(limit=limit, offset=offset)
        return {"ok": True, **result}
    except Exception as e:
        logger.exception("invoice.list_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list invoices",
        )


@router.post("/{invoice_id}/sync-eboekhouden")
async def sync_invoice_to_eboekhouden(
    invoice_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Sync invoice to e-boekhouden.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        invoice = invoice_service.get_invoice(invoice_id)
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found",
            )

        result = await invoice_service.sync_to_eboekhouden(invoice)
        return {"ok": result.get("success", False), **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("invoice.sync_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync invoice to e-boekhouden",
        )

