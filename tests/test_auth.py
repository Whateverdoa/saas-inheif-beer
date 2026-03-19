import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_auth_me_missing_header():
    """Test /auth/me endpoint without Authorization header."""
    resp = client.get("/auth/me")
    assert resp.status_code == 401
    assert "Missing Authorization header" in resp.json()["detail"]


def test_auth_me_invalid_header_format():
    """Test /auth/me endpoint with invalid Authorization header format."""
    resp = client.get("/auth/me", headers={"Authorization": "InvalidFormat token"})
    assert resp.status_code == 401
    assert "Invalid Authorization header format" in resp.json()["detail"]


def test_auth_me_invalid_token(monkeypatch):
    """Test /auth/me endpoint with invalid token."""
    def fake_verify_token(token: str):
        raise ValueError("Token verification failed: invalid token")
    
    with patch("app.dependencies.auth._auth_service.verify_token", side_effect=fake_verify_token):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert resp.status_code == 401
        assert "Token verification failed" in resp.json()["detail"]


def test_auth_me_valid_token(monkeypatch):
    """Test /auth/me endpoint with valid token."""
    mock_user = {
        "user_id": "user_123",
        "session_id": "sess_123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
    }
    
    def fake_verify_token(token: str):
        return mock_user
    
    with patch("app.dependencies.auth._auth_service.verify_token", side_effect=fake_verify_token):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer valid_token"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["user"]["user_id"] == "user_123"
        assert data["user"]["email"] == "test@example.com"


def test_auth_login_missing_token():
    """Test /auth/login endpoint without token."""
    resp = client.post("/auth/login", json={})
    assert resp.status_code == 422  # Validation error


def test_auth_login_invalid_token(monkeypatch):
    """Test /auth/login endpoint with invalid token."""
    def fake_verify_token(token: str):
        raise ValueError("Token verification failed: invalid token")
    
    with patch("app.routers.auth.auth_service.verify_token", side_effect=fake_verify_token):
        resp = client.post("/auth/login", json={"token": "invalid_token"})
        assert resp.status_code == 401
        assert "Authentication failed" in resp.json()["detail"]


def test_auth_login_valid_token(monkeypatch):
    """Test /auth/login endpoint with valid token."""
    mock_user = {
        "user_id": "user_123",
        "session_id": "sess_123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
    }
    
    def fake_verify_token(token: str):
        return mock_user
    
    with patch("app.routers.auth.auth_service.verify_token", side_effect=fake_verify_token):
        resp = client.post("/auth/login", json={"token": "valid_token"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["authenticated"] is True
        assert data["user"]["user_id"] == "user_123"


def test_auth_logout():
    """Test /auth/logout endpoint."""
    resp = client.post("/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_admin_events_unauthorized():
    """Test /admin/events endpoint without authentication."""
    resp = client.get("/admin/events")
    assert resp.status_code == 401


def test_admin_events_authorized(monkeypatch):
    """Test /admin/events endpoint with authentication."""
    mock_user = {
        "user_id": "user_123",
        "email": "test@example.com",
    }
    
    def fake_verify_token(token: str):
        return mock_user
    
    async def fake_list_events(provider=None, limit=100, offset=0):
        return {
            "events": [
                {"event_id": "evt_1", "provider": "stripe", "status": "saved"},
                {"event_id": "evt_2", "provider": "polar", "status": "saved"},
            ],
            "total": 2,
            "limit": limit,
            "offset": offset,
        }
    
    with patch("app.dependencies.auth._auth_service.verify_token", side_effect=fake_verify_token):
        with patch("app.routers.admin.event_store.list_events", side_effect=fake_list_events):
            resp = client.get("/admin/events", headers={"Authorization": "Bearer valid_token"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["ok"] is True
            assert len(data["events"]) == 2


def test_admin_events_with_provider_filter(monkeypatch):
    """Test /admin/events endpoint with provider filter."""
    mock_user = {
        "user_id": "user_123",
        "email": "test@example.com",
    }
    
    def fake_verify_token(token: str):
        return mock_user
    
    async def fake_list_events(provider=None, limit=100, offset=0):
        return {
            "events": [{"event_id": "evt_1", "provider": provider, "status": "saved"}] if provider else [],
            "total": 1 if provider else 0,
            "limit": limit,
            "offset": offset,
        }
    
    with patch("app.dependencies.auth._auth_service.verify_token", side_effect=fake_verify_token):
        with patch("app.routers.admin.event_store.list_events", side_effect=fake_list_events):
            resp = client.get(
                "/admin/events?provider=stripe",
                headers={"Authorization": "Bearer valid_token"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["ok"] is True


def test_admin_event_by_id_unauthorized():
    """Test /admin/events/{event_id} endpoint without authentication."""
    resp = client.get("/admin/events/evt_123")
    assert resp.status_code == 401


def test_admin_event_by_id_not_found(monkeypatch):
    """Test /admin/events/{event_id} endpoint with non-existent event."""
    mock_user = {
        "user_id": "user_123",
        "email": "test@example.com",
    }
    
    def fake_verify_token(token: str):
        return mock_user
    
    async def fake_get_event(event_id: str):
        return None
    
    with patch("app.dependencies.auth._auth_service.verify_token", side_effect=fake_verify_token):
        with patch("app.routers.admin.event_store.get_event", side_effect=fake_get_event):
            resp = client.get(
                "/admin/events/evt_nonexistent",
                headers={"Authorization": "Bearer valid_token"}
            )
            assert resp.status_code == 404
            assert "not found" in resp.json()["detail"].lower()


def test_admin_event_by_id_found(monkeypatch):
    """Test /admin/events/{event_id} endpoint with existing event."""
    mock_user = {
        "user_id": "user_123",
        "email": "test@example.com",
    }
    
    def fake_verify_token(token: str):
        return mock_user
    
    async def fake_get_event(event_id: str):
        return {
            "event_id": event_id,
            "provider": "stripe",
            "status": "saved",
            "payload": {"type": "payment_intent.succeeded"},
        }
    
    with patch("app.dependencies.auth._auth_service.verify_token", side_effect=fake_verify_token):
        with patch("app.routers.admin.event_store.get_event", side_effect=fake_get_event):
            resp = client.get(
                "/admin/events/evt_123",
                headers={"Authorization": "Bearer valid_token"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["ok"] is True
            assert data["event"]["event_id"] == "evt_123"


def test_admin_stats_unauthorized():
    """Test /admin/stats endpoint without authentication."""
    resp = client.get("/admin/stats")
    assert resp.status_code == 401


def test_admin_stats_authorized(monkeypatch):
    """Test /admin/stats endpoint with authentication."""
    mock_user = {
        "user_id": "user_123",
        "email": "test@example.com",
    }
    
    def fake_verify_token(token: str):
        return mock_user
    
    async def fake_get_stats():
        return {
            "total_events": 10,
            "by_provider": {"stripe": 6, "polar": 4},
            "by_status": {"saved": 8, "failed": 2},
        }
    
    with patch("app.dependencies.auth._auth_service.verify_token", side_effect=fake_verify_token):
        with patch("app.routers.admin.event_store.get_stats", side_effect=fake_get_stats):
            resp = client.get("/admin/stats", headers={"Authorization": "Bearer valid_token"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["ok"] is True
            assert data["total_events"] == 10
            assert "by_provider" in data
            assert "by_status" in data

