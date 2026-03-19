from fastapi import APIRouter, Request, Header, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.services.stripe_service import StripeWebhookVerifier, StripeEventProcessor
from app.services.polar_service import PolarWebhookVerifier, PolarEventProcessor
from app.services.event_store import get_event_store
from app.services.ogos_client_async import OGOSClient

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

logger = logging.getLogger("uvicorn.error")

# Init shared services (DI-lite)
event_store = get_event_store()          # Convex or in-memory, depending on env
ogos_client = OGOSClient()               # Async httpx client with retry
stripe_verifier = StripeWebhookVerifier()
stripe_processor = StripeEventProcessor(event_store=event_store, ogos_client=ogos_client)
polar_verifier = PolarWebhookVerifier()
polar_processor = PolarEventProcessor(event_store=event_store)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(default=None, alias="Stripe-Signature"),
):
    if not stripe_signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe-Signature header")

    raw_body = await request.body()
    try:
        event = stripe_verifier.verify(raw_body, stripe_signature)  # raises on invalid
    except Exception as e:
        logger.warning("stripe.verify_failed", extra={"error": str(e)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # idempotency
    event_id = event.get("id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing event id")
    if await event_store.exists(event_id):
        logger.info("stripe.event_duplicate", extra={"event_id": event_id, "type": event.get("type")})
        return JSONResponse({"ok": True, "duplicate": True})

    # persist before processing (exactly-once)
    await event_store.save(event_id, provider="stripe", payload=event)

    try:
        result = await stripe_processor.process(event)  # may submit to OGOS on payment success
        logger.info("stripe.event_processed", extra={"event_id": event_id, "type": event.get("type")})
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        logger.exception("stripe.process_failed", extra={"event_id": event_id, "type": event.get("type")})
        await event_store.mark_failed(event_id, error=str(e))
        # 200 to avoid webhook storms; switch to 500 to force retries.
        return JSONResponse({"ok": False, "error": "processing_failed"}, status_code=200)


@router.post("/polar")
async def polar_webhook(
    request: Request,
    polar_sig: Optional[str] = Header(default=None, alias="Polar-Signature"),
    polar_ts: Optional[str] = Header(default=None, alias="Polar-Timestamp"),
):
    """
    Polar webhook verification:
    - Uses HMAC-SHA256 over: f"{timestamp}.{raw_body}" with secret POLAR_WEBHOOK_SECRET.
    - Signature header format: "t=..., v1=hexdigest"
    NOTE: If Polar changes formats, adjust in PolarWebhookVerifier.
    """
    raw_body = await request.body()

    try:
        event = polar_verifier.verify(raw_body, polar_sig, polar_ts)
    except Exception as e:
        logger.warning("polar.verify_failed", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail="Invalid Polar signature")

    event_id = event.get("id") or event.get("event_id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing event id")

    if await event_store.exists(event_id):
        logger.info("polar.event_duplicate", extra={"event_id": event_id, "type": event.get("type")})
        return JSONResponse({"ok": True, "duplicate": True})

    await event_store.save(event_id, provider="polar", payload=event)

    try:
        result = await polar_processor.process(event)
        logger.info("polar.event_processed", extra={"event_id": event_id, "type": event.get("type")})
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        logger.exception("polar.process_failed", extra={"event_id": event_id, "type": event.get("type")})
        await event_store.mark_failed(event_id, error=str(e))
        return JSONResponse({"ok": False, "error": "processing_failed"}, status_code=200)
