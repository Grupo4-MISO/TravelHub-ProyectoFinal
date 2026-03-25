from types import SimpleNamespace
from uuid import uuid4
from werkzeug.security import generate_password_hash

from app.api import api as api_module


def test_health_ok(client):
    resp = client.get("/api/v1/auth/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "healthy"}


def test_login_missing_credentials(client):
    resp = client.post("/api/v1/auth/login", json={})
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Missing credentials"


def test_login_invalid_credentials_user_not_found(client, monkeypatch):
    monkeypatch.setattr(api_module.user_crud, "get_user_by_email", lambda email: None)

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "noexiste@travelhub.com", "password": "secret123"},
    )
    assert resp.status_code == 401
    assert resp.get_json()["message"] == "Invalid credentials"


def test_login_success(client, monkeypatch):
    fake_user = SimpleNamespace(
        id=uuid4(),
        username="admin",
        password_hash=generate_password_hash("secret123"),
        role=SimpleNamespace(value="Administrator"),
    )
    monkeypatch.setattr(api_module.user_crud, "get_user_by_email", lambda email: fake_user)

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@travelhub.com", "password": "secret123"},
    )

    body = resp.get_json()
    assert resp.status_code == 200
    assert "token" in body
    assert body["user"]["username"] == "admin"
    assert body["user"]["role"] == "Administrator"


def test_create_user_missing_password(client):
    resp = client.post(
        "/api/v1/auth/users",
        json={"username": "u1", "email": "u1@x.com", "role": "Traveler"},
    )
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Missing password"


def test_create_user_invalid_role(client):
    resp = client.post(
        "/api/v1/auth/users",
        json={
            "username": "u1",
            "email": "u1@x.com",
            "password": "abc123",
            "role": "NoExiste",
        },
    )
    assert resp.status_code == 400
    assert "Invalid role" in resp.get_json()["message"]


def test_create_user_success_hashes_password(client, monkeypatch):
    captured = {}

    def fake_create_user(payload):
        captured["payload"] = payload
        return SimpleNamespace(
            id=uuid4(),
            username=payload["username"],
            email=payload["email"],
        )

    monkeypatch.setattr(api_module.user_crud, "create_user", fake_create_user)

    resp = client.post(
        "/api/v1/auth/users",
        json={
            "username": "nuevo",
            "email": "nuevo@travelhub.com",
            "password": "abc123",
            "role": "Traveler",
        },
    )

    body = resp.get_json()
    assert resp.status_code == 201
    assert body["username"] == "nuevo"
    assert "password" not in captured["payload"]
    assert "password_hash" in captured["payload"]
    assert captured["payload"]["role"].value == "Traveler"
