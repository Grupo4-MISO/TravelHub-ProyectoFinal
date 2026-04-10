from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
import sys
from pathlib import Path

import jwt

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.api import api as api_module
from main import app


def build_token(role="User", user_id=None, username="tester"):
    payload = {
        "sub": str(user_id or uuid4()),
        "username": username,
        "role": role,
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def auth_headers(role="User", user_id=None, username="tester"):
    return {
        "Authorization": f"Bearer {build_token(role=role, user_id=user_id, username=username)}"
    }


def make_manager(manager_id=None, hospedaje_id=None, user_id=None, username="tester", email="tester@example.com"):
    return SimpleNamespace(
        id=manager_id or uuid4(),
        hospedajeId=hospedaje_id or uuid4(),
        userId=user_id or uuid4(),
        userName=username,
        email=email,
        first_name="Test",
        last_name="User",
        created_at=datetime(2026, 4, 6, 12, 0, 0),
        updated_at=datetime(2026, 4, 6, 12, 30, 0),
    )


def test_health_ok(client):
    resp = client.get("/api/v1/Managers/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "healthy"}


def test_get_manager_by_id_ok(client, monkeypatch):
    manager_id = uuid4()
    manager = make_manager(manager_id=manager_id)
    monkeypatch.setattr(api_module.manager_crud, "get_manager_by_id", lambda manager_uuid: manager if manager_uuid == manager_id else None)

    resp = client.get(f"/api/v1/Managers/{manager_id}", headers=auth_headers())

    assert resp.status_code == 200
    assert resp.get_json() == {
        "id": str(manager.id),
        "hospedajeId": str(manager.hospedajeId),
        "userName": manager.userName,
        "userId": str(manager.userId),
        "email": manager.email,
        "first_name": manager.first_name,
        "last_name": manager.last_name,
        "created_at": manager.created_at.isoformat(),
        "updated_at": manager.updated_at.isoformat(),
    }


def test_get_manager_by_id_requires_token(client):
    manager_id = uuid4()

    resp = client.get(f"/api/v1/Managers/{manager_id}")

    assert resp.status_code == 401
    assert resp.get_json() == {"message": "Token missing"}


def test_get_managers_by_hospedaje_ok(client, monkeypatch):
    hospedaje_id = uuid4()
    managers = [
        make_manager(hospedaje_id=hospedaje_id, username="ana"),
        make_manager(hospedaje_id=hospedaje_id, username="luis"),
    ]
    monkeypatch.setattr(api_module.manager_crud, "get_all_managers_by_hospedaje_id", lambda value: managers if value == hospedaje_id else [])

    resp = client.get(
        f"/api/v1/Managers/hospedajes/{hospedaje_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["managers"]) == 2
    assert body["managers"][0]["userName"] == "ana"
    assert body["managers"][1]["userName"] == "luis"


def test_get_managers_by_hospedaje_not_found(client, monkeypatch):
    hospedaje_id = uuid4()
    monkeypatch.setattr(api_module.manager_crud, "get_all_managers_by_hospedaje_id", lambda value: [])

    resp = client.get(
        f"/api/v1/Managers/hospedajes/{hospedaje_id}",
        headers=auth_headers(),
    )

    assert resp.status_code == 404
    assert resp.get_json() == {"message": "Managers no encontrados"}


def test_create_manager_ok(client, monkeypatch):
    hospedaje_id = uuid4()
    user_id = uuid4()
    manager = make_manager(hospedaje_id=hospedaje_id, user_id=user_id, username="marco")

    monkeypatch.setattr(api_module.manager_crud, "create_manager", lambda data: manager)

    resp = client.post(
        "/api/v1/Managers",
        json={
            "hospedajeId": str(hospedaje_id),
            "userName": "marco",
            "userId": str(user_id),
            "email": "marco@example.com",
            "first_name": "Marco",
            "last_name": "User",
        },
        headers=auth_headers(user_id=user_id, username="marco"),
    )

    assert resp.status_code == 201
    assert resp.get_json() == {
        "id": str(manager.id),
        "hospedajeId": str(manager.hospedajeId),
        "userName": manager.userName,
        "userId": str(manager.userId),
        "email": manager.email,
        "first_name": manager.first_name,
        "last_name": manager.last_name,
        "created_at": manager.created_at.isoformat(),
        "updated_at": manager.updated_at.isoformat(),
    }


def test_update_manager_ok(client, monkeypatch):
    manager_id = uuid4()
    monkeypatch.setattr(api_module.manager_crud, "update_manager", lambda manager_uuid, data: True if manager_uuid == manager_id else None)

    resp = client.put(
        f"/api/v1/Managers/{manager_id}",
        json={"comment": "Comentario actualizado", "rating": 4},
        headers=auth_headers(role="Administrator"),
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Manager updated"}


def test_update_manager_forbidden_for_non_admin(client):
    manager_id = uuid4()

    resp = client.put(
        f"/api/v1/Managers/{manager_id}",
        json={"comment": "Manager actualizado", "rating": 4},
        headers=auth_headers(role="User"),
    )

    assert resp.status_code == 403
    assert resp.get_json() == {"message": "Unauthorized"}


def test_delete_manager_ok(client, monkeypatch):
    manager_id = uuid4()
    monkeypatch.setattr(api_module.manager_crud, "delete_manager", lambda manager_uuid: manager_uuid == manager_id)

    resp = client.delete(
        f"/api/v1/Managers/{manager_id}",
        headers=auth_headers(role="Administrator"),
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Manager deleted"}

