from datetime import datetime
from pathlib import Path
import sys
from types import SimpleNamespace
from uuid import uuid4

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


def make_traveler(traveler_id=None, user_id=None):
    traveler_id = traveler_id or uuid4()
    return SimpleNamespace(
        id=traveler_id,
        documentNumber="900123456",
        userId=user_id or uuid4(),
        first_name="Ana",
        last_name="Lopez",
        phone="3001234567",
        email="ana@example.com",
        travelerStatus=SimpleNamespace(name="Pending"),
        created_at=datetime(2026, 4, 23, 12, 0, 0),
        updated_at=datetime(2026, 4, 23, 12, 30, 0),
    )


def make_traveler_address(traveler_id):
    return SimpleNamespace(
        id=uuid4(),
        traveler_id=traveler_id,
        line1="Calle 123",
        line2="Apto 456",
        city="Bogota",
        state="Cundinamarca",
        country="Colombia",
        countryCode="CO",
        postal_code="110111",
        created_at=datetime(2026, 4, 23, 12, 0, 0),
        updated_at=datetime(2026, 4, 23, 12, 30, 0),
    )


def traveler_payload():
    return {
        "traveler": {
            "documentNumber": "900123456",
            "first_name": "Ana",
            "last_name": "Lopez",
            "email": "ana@example.com",
            "phone": "3001234567",
            "password": "Pass12345",
            "travelerStatus": "Pending",
        },
        "address": {
            "line1": "Calle 123",
            "line2": "Apto 456",
            "city": "Bogota",
            "state": "Cundinamarca",
            "country": "Colombia",
            "countryCode": "CO",
            "postal_code": "110111",
        },
    }


def test_health_ok(client):
    resp = client.get("/api/v1/Travelers/health")

    assert resp.status_code == 200
    assert resp.get_json() == {"status": "healthy"}


def test_get_traveler_by_userid_ok(client, monkeypatch):
    user_id = uuid4()
    traveler = make_traveler(user_id=user_id)
    address = make_traveler_address(traveler.id)

    monkeypatch.setattr(
        api_module.traveler_crud,
        "get_traveler_by_userid",
        lambda value: (traveler, [address]) if value == user_id else None,
    )

    resp = client.get(f"/api/v1/Travelers/users/{user_id}", headers=auth_headers())

    assert resp.status_code == 200
    assert resp.get_json() == {
        "id": str(traveler.id),
        "documentNumber": traveler.documentNumber,
        "userId": str(traveler.userId),
        "first_name": traveler.first_name,
        "last_name": traveler.last_name,
        "phone": traveler.phone,
        "email": traveler.email,
        "travelerStatus": traveler.travelerStatus.name,
        "created_at": traveler.created_at.isoformat(),
        "updated_at": traveler.updated_at.isoformat(),
        "addresses": [
            {
                "id": str(address.id),
                "traveler_id": str(address.traveler_id),
                "line1": address.line1,
                "line2": address.line2,
                "city": address.city,
                "state": address.state,
                "country": address.country,
                "countryCode": address.countryCode,
                "postal_code": address.postal_code,
                "created_at": address.created_at.isoformat(),
                "updated_at": address.updated_at.isoformat(),
            }
        ],
    }


def test_get_traveler_by_userid_not_found(client, monkeypatch):
    monkeypatch.setattr(api_module.traveler_crud, "get_traveler_by_userid", lambda value: None)

    resp = client.get(f"/api/v1/Travelers/users/{uuid4()}", headers=auth_headers())

    assert resp.status_code == 404
    assert resp.get_json() == {"message": "Traveler not found"}


def test_create_traveler_missing_fields(client):
    resp = client.post("/api/v1/Travelers", json={})

    assert resp.status_code == 400
    assert resp.get_json() == {
        "message": "Faltan campos requeridos en Traveler: documentNumber, first_name, last_name, email, password"
    }


def test_create_traveler_invalid_user_data(client, monkeypatch):
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "validate_user_creation_data",
        lambda email, password, first_name, last_name: (False, "Email inválido"),
    )

    resp = client.post("/api/v1/Travelers", json=traveler_payload())

    assert resp.status_code == 400
    assert resp.get_json() == {"message": "Email inválido"}


def test_create_traveler_duplicate_email(client, monkeypatch):
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "validate_user_creation_data",
        lambda email, password, first_name, last_name: (True, None),
    )
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "create_user_in_auth_service",
        lambda email, password, first_name, last_name, role="Traveler": (None, "email ya registrado"),
    )

    resp = client.post("/api/v1/Travelers", json=traveler_payload())

    assert resp.status_code == 409
    assert resp.get_json() == {"message": "email ya registrado"}


def test_create_traveler_ok(client, monkeypatch):
    user_id = uuid4()
    traveler = make_traveler(user_id=user_id)

    monkeypatch.setattr(
        api_module.AsyncUserService,
        "validate_user_creation_data",
        lambda email, password, first_name, last_name: (True, None),
    )
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "create_user_in_auth_service",
        lambda email, password, first_name, last_name, role="Traveler": (
            {
                "id": str(user_id),
                "username": "ana.lopez",
                "email": "ana@example.com",
            },
            None,
        ),
    )

    captured = {}

    def fake_create_traveler(data):
        captured["data"] = data
        return traveler

    monkeypatch.setattr(api_module.traveler_crud, "create_traveler", fake_create_traveler)

    resp = client.post("/api/v1/Travelers", json=traveler_payload())
    body = resp.get_json()

    assert resp.status_code == 201
    assert body["message"] == "Traveler y dirección creados exitosamente"
    assert body["Traveler"]["id"] == str(traveler.id)
    assert body["user"]["id"] == str(user_id)
    assert body["address"]["city"] == "Bogota"
    assert captured["data"]["userId"] == str(user_id)
    assert captured["data"]["documentNumber"] == "900123456"


def test_create_traveler_when_crud_returns_none(client, monkeypatch):
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "validate_user_creation_data",
        lambda email, password, first_name, last_name: (True, None),
    )
    monkeypatch.setattr(
        api_module.AsyncUserService,
        "create_user_in_auth_service",
        lambda email, password, first_name, last_name, role="Traveler": (
            {"id": str(uuid4()), "email": "ana@example.com"},
            None,
        ),
    )
    monkeypatch.setattr(api_module.traveler_crud, "create_traveler", lambda data: None)

    resp = client.post("/api/v1/Travelers", json=traveler_payload())

    assert resp.status_code == 409
    assert resp.get_json() == {"message": "Error creating Traveler"}


def test_get_traveler_by_id_requires_token(client):
    resp = client.get(f"/api/v1/Travelers/{uuid4()}")

    assert resp.status_code == 401
    assert resp.get_json() == {"message": "Token missing"}


def test_get_traveler_by_id_ok(client, monkeypatch):
    traveler_id = uuid4()
    traveler = make_traveler(traveler_id=traveler_id)

    monkeypatch.setattr(
        api_module.traveler_crud,
        "get_traveler_by_id",
        lambda value: traveler if value == traveler_id else None,
    )

    resp = client.get(f"/api/v1/Travelers/{traveler_id}", headers=auth_headers())

    assert resp.status_code == 200
    assert resp.get_json()["id"] == str(traveler_id)


def test_get_traveler_by_id_not_found(client, monkeypatch):
    monkeypatch.setattr(api_module.traveler_crud, "get_traveler_by_id", lambda value: None)

    resp = client.get(f"/api/v1/Travelers/{uuid4()}", headers=auth_headers())

    assert resp.status_code == 404
    assert resp.get_json() == {"message": "Traveler not found"}


def test_update_traveler_requires_admin(client):
    resp = client.put(
        f"/api/v1/Travelers/{uuid4()}",
        headers=auth_headers(role="Traveler"),
        json={"first_name": "Nuevo"},
    )

    assert resp.status_code == 403
    assert resp.get_json() == {"message": "Unauthorized"}


def test_update_traveler_ok(client, monkeypatch):
    traveler_id = uuid4()
    monkeypatch.setattr(
        api_module.traveler_crud,
        "update_traveler",
        lambda value, data: SimpleNamespace(id=value) if value == traveler_id else None,
    )

    resp = client.put(
        f"/api/v1/Travelers/{traveler_id}",
        headers=auth_headers(role="Admin"),
        json={"first_name": "Nuevo"},
    )

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Traveler updated"}


def test_update_traveler_returns_400_when_missing(client, monkeypatch):
    monkeypatch.setattr(api_module.traveler_crud, "update_traveler", lambda value, data: None)

    resp = client.put(
        f"/api/v1/Travelers/{uuid4()}",
        headers=auth_headers(role="Admin"),
        json={"first_name": "Nuevo"},
    )

    assert resp.status_code == 400
    assert resp.get_json() == {"message": "Error updating Traveler"}


def test_delete_traveler_requires_admin(client):
    resp = client.delete(f"/api/v1/Travelers/{uuid4()}", headers=auth_headers(role="Traveler"))

    assert resp.status_code == 403
    assert resp.get_json() == {"message": "Unauthorized"}


def test_delete_traveler_ok(client, monkeypatch):
    traveler_id = uuid4()
    monkeypatch.setattr(api_module.traveler_crud, "delete_traveler", lambda value: value == traveler_id)

    resp = client.delete(f"/api/v1/Travelers/{traveler_id}", headers=auth_headers(role="Admin"))

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Traveler deleted"}


def test_delete_traveler_not_found(client, monkeypatch):
    monkeypatch.setattr(api_module.traveler_crud, "delete_traveler", lambda value: False)

    resp = client.delete(f"/api/v1/Travelers/{uuid4()}", headers=auth_headers(role="Admin"))

    assert resp.status_code == 404
    assert resp.get_json() == {"message": "Traveler not found"}


def test_get_traveler_by_userid_requires_token(client):
    resp = client.get(f"/api/v1/Travelers/users/{uuid4()}")

    assert resp.status_code == 401
    assert resp.get_json() == {"message": "Token missing"}


def test_get_traveler_by_userid_ok_with_token(client, monkeypatch):
    user_id = uuid4()
    traveler = make_traveler(user_id=user_id)
    address = make_traveler_address(traveler.id)

    monkeypatch.setattr(
        api_module.traveler_crud,
        "get_traveler_by_userid",
        lambda value: (traveler, [address]) if value == user_id else None,
    )

    resp = client.get(f"/api/v1/Travelers/users/{user_id}", headers=auth_headers())

    assert resp.status_code == 200
    assert resp.get_json()["userId"] == str(user_id)
    assert len(resp.get_json()["addresses"]) == 1


def test_seed_db_ok(client, monkeypatch):
    monkeypatch.setattr(
        api_module.SeedHelper,
        "reset_and_seed",
        lambda: {"ok": True, "travelers_procesados": 3},
    )

    resp = client.post("/api/v1/Travelers/seed")

    assert resp.status_code == 200
    assert resp.get_json() == {"msg": "Seed ejecutado correctamente", "Travelers procesados": 3}


def test_seed_db_error(client, monkeypatch):
    monkeypatch.setattr(
        api_module.SeedHelper,
        "reset_and_seed",
        lambda: {"ok": False, "error": "fallo seed"},
    )

    resp = client.post("/api/v1/Travelers/seed")

    assert resp.status_code == 500
    assert resp.get_json() == {"msg": "Error al ejecutar el seed", "error": "fallo seed"}