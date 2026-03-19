import os
import json
import logging
from typing import Any, Dict
from decimal import Decimal
from datetime import datetime

import stripe

from app.services.eboekhouden_service import get_eboekhouden_client
from app.services.invoice_service import get_invoice_service
from app.services.credit_service import get_credit_service
from app.services.database import get_database
from app.models.invoice import TransactionMapping
from app.models import Transaction, TransactionStatus, TransactionProvider

logger = logging.getLogger("uvicorn.error")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")

if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY


class StripeWebhookVerifier:
    def __init__(self, webhook_secret: str | None = None):
        self.webhook_secret = webhook_secret or STRIPE_WEBHOOK_SECRET
        if not self.webhook_secret:
            logger.warning("stripe.no_webhook_secret", extra={"msg": "STRIPE_WEBHOOK_SECRET not set"})

    def verify(self, raw_body: bytes, signature_header: str) -> Dict[str, Any]:
        # stripe library handles timestamp/signature, default tolerance ~300s
        evt = stripe.Webhook.construct_event(
            payload=raw_body.decode("utf-8"),
            sig_header=signature_header,
            secret=self.webhook_secret,
        )
        try:
            return json.loads(str(evt))
        except Exception:
            return evt.to_dict()


class StripeEventProcessor:
    """
    Business rules:
    - payment_intent.succeeded => submit order to OGOS (if metadata.order_id present)
    - payment_intent.payment_failed => mark order failed
    - payment_intent.succeeded => generate invoice and sync to e-boekhouden
    Extend as needed.
    """
    def __init__(self, event_store, ogos_client):
        self.event_store = event_store
        self.ogos_client = ogos_client
        self.eboekhouden_client = get_eboekhouden_client()
        self.invoice_service = get_invoice_service()
        self.credit_service = get_credit_service()
        self.db = get_database()

    async def process(self, event: Dict[str, Any]) -> Dict[str, Any]:
        evt_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        result: Dict[str, Any] = {"handled": False, "type": evt_type}

        if evt_type == "payment_intent.succeeded":
            metadata = data.get("metadata") or {}
            order_id = metadata.get("order_id")
            payment_type = metadata.get("type", "order")  # "order" or "credit"
            user_id = metadata.get("user_id")
            
            payment_id = data.get("id", "")
            amount = Decimal(str(data.get("amount", 0))) / 100  # Convert from cents
            currency = data.get("currency", "eur").upper()
            
            # Handle credit purchase
            if payment_type == "credit" and user_id:
                try:
                    # Create transaction record
                    transaction = Transaction(
                        user_id=user_id,
                        provider=TransactionProvider.STRIPE,
                        provider_transaction_id=payment_id,
                        amount=amount,
                        currency=currency,
                        status=TransactionStatus.COMPLETED,
                        metadata=metadata,
                    )
                    await self.db.create_transaction(transaction)
                    
                    # Add credits to user account (1 credit per EUR, or as specified)
                    credits_amount = metadata.get("credits_amount", amount)  # Default: 1 credit per EUR
                    credit = await self.credit_service.purchase_credits(
                        user_id=user_id,
                        amount=Decimal(str(credits_amount)),
                        transaction_id=transaction.transaction_id,
                    )
                    
                    result.update({
                        "handled": True,
                        "type": "credit_purchase",
                        "user_id": user_id,
                        "credits_added": float(credits_amount),
                        "credit_id": credit.credit_id,
                    })
                    logger.info(
                        "stripe.credit_purchased",
                        extra={"user_id": user_id, "amount": float(amount), "credits": float(credits_amount)},
                    )
                    
                    # Still generate invoice for credit purchase
                    customer_name = metadata.get("customer_name", "Customer")
                    customer_email = metadata.get("customer_email")
                    customer_address = metadata.get("customer_address")
                    
                    invoice = self.invoice_service.create_invoice_from_payment(
                        payment_id=payment_id,
                        provider="stripe",
                        amount=amount,
                        currency=currency,
                        customer_name=customer_name,
                        customer_email=customer_email,
                        customer_address=customer_address,
                        description=f"Credit purchase - {credits_amount} credits",
                        metadata={**metadata, "credit_purchase": True},
                    )
                    
                    result.update({
                        "invoice_id": invoice.invoice_id,
                        "invoice_number": invoice.invoice_number,
                    })
                    
                    return result
                
                except Exception as e:
                    logger.exception(
                        "stripe.credit_purchase_error",
                        extra={"payment_id": payment_id, "user_id": user_id, "error": str(e)},
                    )
                    # Don't fail the webhook, but log the error
            
            # Submit to OGOS if order_id present (for order payments)
            if order_id:
                ogos_resp = await self.ogos_client.submit_paid_order(order_id)
                result.update({"handled": True, "order_id": order_id, "ogos": ogos_resp})
            else:
                logger.info("stripe.no_order_id_in_metadata")
            
            # Generate invoice and sync to e-boekhouden (for order payments)
            try:
                # Extract customer information
                customer_id = data.get("customer")
                customer_name = metadata.get("customer_name", "Customer")
                customer_email = metadata.get("customer_email")
                customer_address = metadata.get("customer_address")
                
                # Generate invoice
                invoice = self.invoice_service.create_invoice_from_payment(
                    payment_id=payment_id,
                    provider="stripe",
                    amount=amount,
                    currency=currency,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    description=metadata.get("description", "Stripe payment"),
                    metadata=metadata,
                )
                
                result.update({
                    "invoice_id": invoice.invoice_id,
                    "invoice_number": invoice.invoice_number,
                })
                
                # Sync transaction to e-boekhouden
                if self.eboekhouden_client.enabled:
                    transaction = TransactionMapping(
                        transaction_id=payment_id,
                        provider="stripe",
                        amount=amount,
                        currency=currency,
                        description=metadata.get("description", "Stripe payment"),
                        date=datetime.fromtimestamp(data.get("created", 0)),
                        customer_name=customer_name,
                        customer_email=customer_email,
                        invoice_id=invoice.invoice_id,
                        metadata=metadata,
                    )
                    
                    eboekhouden_result = await self.eboekhouden_client.create_transaction(transaction)
                    if eboekhouden_result.get("success"):
                        result.update({"eboekhouden_synced": True})
                        
                        # Also sync invoice to e-boekhouden
                        await self.invoice_service.sync_to_eboekhouden(invoice)
                    
                    result.update({"eboekhouden": eboekhouden_result})
                    
            except Exception as e:
                logger.exception(
                    "stripe.invoice_generation_error",
                    extra={"payment_id": payment_id, "error": str(e)},
                )
                # Don't fail the webhook if invoice generation fails

        elif evt_type == "payment_intent.payment_failed":
            metadata = data.get("metadata") or {}
            order_id = metadata.get("order_id")
            if order_id:
                await self.event_store.mark_note(f"order:{order_id}", note="payment_failed")
                result.update({"handled": True, "order_id": order_id, "status": "payment_failed"})

        return result
