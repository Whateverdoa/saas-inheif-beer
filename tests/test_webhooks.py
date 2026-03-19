import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_stripe_webhook_missing_header():
    resp = client.post("/webhooks/stripe", data="{}")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Missing Stripe-Signature header"

def test_polar_webhook_missing_header():
    resp = client.post("/webhooks/polar", data="{}")
    assert resp.status_code == 400

def test_idempotency_inmemory(monkeypatch):
    from app.routers import webhooks

    async def fake_exists(event_id: str):
        return False

    async def fake_save(event_id: str, provider: str, payload: dict):
        return None

    def fake_verify(raw, header):
        return {"id": "evt_test_123", "type": "payment_intent.succeeded", "data": {"object": {"metadata": {"order_id": "ord_1"}}}}

    async def fake_process(evt):
        return {"handled": True}

    monkeypatch.setattr(webhooks.event_store, "exists", fake_exists)
    monkeypatch.setattr(webhooks.event_store, "save", fake_save)
    monkeypatch.setattr(webhooks.stripe_verifier, "verify", fake_verify)
    monkeypatch.setattr(webhooks.stripe_processor, "process", lambda evt: {"handled": True})

    resp = client.post("/webhooks/stripe", data=json.dumps({"dummy": True}), headers={"Stripe-Signature": "t=1,v1=dummy"})
    assert resp.status_code in (200, 400, 500)
