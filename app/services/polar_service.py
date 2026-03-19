import os
import hmac
import hashlib
import json
import logging
from typing import Any, Dict
from decimal import Decimal
from datetime import datetime

from app.services.eboekhouden_service import get_eboekhouden_client
from app.services.invoice_service import get_invoice_service
from app.services.subscription_service import get_subscription_service
from app.services.database import get_database
from app.models.invoice import TransactionMapping
from app.models import Subscription, SubscriptionStatus

logger = logging.getLogger("uvicorn.error")

POLAR_WEBHOOK_SECRET = os.getenv("POLAR_WEBHOOK_SECRET", "")

def _parse_signature_header(sig_header: str) -> dict:
    parts = [p.strip() for p in (sig_header or "").split(",")]
    out = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


class PolarWebhookVerifier:
    def __init__(self, webhook_secret: str | None = None):
        self.webhook_secret = webhook_secret or POLAR_WEBHOOK_SECRET
        if not self.webhook_secret:
            logger.warning("POLAR_WEBHOOK_SECRET not set - webhook verification will fail")

    def verify(self, raw_body: bytes, signature_header: str | None, timestamp: str | None):
        if not self.webhook_secret:
            raise ValueError("No POLAR_WEBHOOK_SECRET configured")
        if not signature_header:
            raise ValueError("Missing Polar-Signature header")

        sig = _parse_signature_header(signature_header)
        t = sig.get("t") or (timestamp or "")
        v1 = sig.get("v1")
        if not (t and v1):
            raise ValueError("Invalid Polar signature header")

        payload_to_sign = f"{t}.{raw_body.decode('utf-8')}".encode("utf-8")
        expected = hmac.new(
            key=self.webhook_secret.encode("utf-8"),
            msg=payload_to_sign,
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected, v1):
            raise ValueError("Signature mismatch")

        return json.loads(raw_body.decode("utf-8"))


class PolarEventProcessor:
    """
    Example mapping:
    - subscription.active / updated => enable org/tier
    - subscription.canceled => disable / downgrade
    - payment.* => generate invoice and sync to e-boekhouden
    """
    def __init__(self, event_store):
        self.event_store = event_store
        self.eboekhouden_client = get_eboekhouden_client()
        self.invoice_service = get_invoice_service()
        self.subscription_service = get_subscription_service()
        self.db = get_database()

    async def process(self, event: Dict[str, Any]) -> Dict[str, Any]:
        evt_type = event.get("type")
        obj = event.get("data", {})
        result = {"handled": False, "type": evt_type}

        if evt_type in {"subscription.active", "subscription.updated"}:
            # Extract subscription and organization info
            subscription_id = obj.get("id") or obj.get("subscription_id")
            polar_subscription_id = subscription_id
            org_id = obj.get("organization_id") or obj.get("customer", {}).get("id")
            plan = obj.get("plan", {})
            plan_name = plan.get("name") or obj.get("price_id", "Unknown Plan")
            plan_price = obj.get("amount") or plan.get("amount", 0)
            if isinstance(plan_price, int):
                plan_price = Decimal(plan_price) / 100  # Convert from cents
            
            current_period_start = obj.get("current_period_start")
            current_period_end = obj.get("current_period_end")
            
            if org_id and polar_subscription_id:
                # Parse dates if they're timestamps
                from datetime import datetime
                if isinstance(current_period_start, (int, float)):
                    current_period_start = datetime.fromtimestamp(current_period_start)
                elif isinstance(current_period_start, str):
                    # Try to parse ISO format
                    try:
                        current_period_start = datetime.fromisoformat(current_period_start.replace("Z", "+00:00"))
                    except:
                        current_period_start = datetime.now()
                
                if isinstance(current_period_end, (int, float)):
                    current_period_end = datetime.fromtimestamp(current_period_end)
                elif isinstance(current_period_end, str):
                    try:
                        current_period_end = datetime.fromisoformat(current_period_end.replace("Z", "+00:00"))
                    except:
                        current_period_end = datetime.now()
                
                # Check if subscription exists
                existing_sub = await self.db.get_subscription_by_org(org_id)
                
                if existing_sub:
                    # Update existing subscription
                    await self.db.update_subscription(
                        existing_sub.subscription_id,
                        status=SubscriptionStatus.ACTIVE,
                        plan_name=plan_name,
                        plan_price=plan_price,
                        current_period_start=current_period_start,
                        current_period_end=current_period_end,
                    )
                else:
                    # Create new subscription
                    subscription = Subscription(
                        org_id=org_id,
                        polar_subscription_id=polar_subscription_id,
                        status=SubscriptionStatus.ACTIVE,
                        plan_name=plan_name,
                        plan_price=plan_price,
                        current_period_start=current_period_start or datetime.now(),
                        current_period_end=current_period_end or datetime.now(),
                    )
                    await self.db.create_subscription(subscription)
                
                # Update organization subscription status
                await self.db.update_organization(org_id, subscription_status=SubscriptionStatus.ACTIVE)
                
                await self.event_store.mark_note(f"org:{org_id}", note=f"tier:{plan_name}")
                result.update({"handled": True, "org_id": org_id, "tier": plan_name, "subscription_id": polar_subscription_id})

        elif evt_type in {"subscription.canceled", "subscription.expired"}:
            org_id = obj.get("organization_id") or obj.get("customer", {}).get("id")
            subscription_id = obj.get("id") or obj.get("subscription_id")
            
            if org_id:
                # Update subscription status
                existing_sub = await self.db.get_subscription_by_org(org_id)
                if existing_sub:
                    await self.db.update_subscription(
                        existing_sub.subscription_id,
                        status=SubscriptionStatus.EXPIRED if evt_type == "subscription.expired" else SubscriptionStatus.CANCELLED,
                    )
                
                # Update organization subscription status
                await self.db.update_organization(
                    org_id,
                    subscription_status=SubscriptionStatus.EXPIRED if evt_type == "subscription.expired" else SubscriptionStatus.CANCELLED,
                )
                
                await self.event_store.mark_note(f"org:{org_id}", note="tier:inactive")
                result.update({"handled": True, "org_id": org_id, "tier": "inactive"})

        # Handle payment events for invoice generation and e-boekhouden sync
        if evt_type.startswith("payment.") or evt_type.startswith("transaction."):
            try:
                payment_id = obj.get("id") or event.get("id", "")
                amount = Decimal(str(obj.get("amount", 0))) / 100  # Convert from cents if needed
                currency = obj.get("currency", "eur").upper()
                
                # Extract customer information
                customer = obj.get("customer", {})
                customer_name = customer.get("name") or obj.get("organization_id", "Customer")
                customer_email = customer.get("email")
                
                # Generate invoice
                invoice = self.invoice_service.create_invoice_from_payment(
                    payment_id=payment_id,
                    provider="polar",
                    amount=amount,
                    currency=currency,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    description=f"Polar {evt_type}",
                    metadata=obj,
                )
                
                result.update({
                    "handled": True,
                    "invoice_id": invoice.invoice_id,
                    "invoice_number": invoice.invoice_number,
                })
                
                # Sync transaction to e-boekhouden
                if self.eboekhouden_client.enabled:
                    transaction = TransactionMapping(
                        transaction_id=payment_id,
                        provider="polar",
                        amount=amount,
                        currency=currency,
                        description=f"Polar {evt_type}",
                        date=datetime.now(),
                        customer_name=customer_name,
                        customer_email=customer_email,
                        invoice_id=invoice.invoice_id,
                        metadata=obj,
                    )
                    
                    eboekhouden_result = await self.eboekhouden_client.create_transaction(transaction)
                    if eboekhouden_result.get("success"):
                        result.update({"eboekhouden_synced": True})
                        
                        # Also sync invoice to e-boekhouden
                        await self.invoice_service.sync_to_eboekhouden(invoice)
                    
                    result.update({"eboekhouden": eboekhouden_result})
                    
            except Exception as e:
                logger.exception(
                    "polar.invoice_generation_error",
                    extra={"event_type": evt_type, "error": str(e)},
                )
                # Don't fail the webhook if invoice generation fails

        return result
