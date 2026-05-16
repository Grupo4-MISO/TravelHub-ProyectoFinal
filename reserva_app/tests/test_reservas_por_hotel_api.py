from datetime import datetime, timedelta

import jwt
import pytest
from flask import Flask
from flask_restful import Api

import app.api.api as api_module
from app.api.api import Reservas_por_hotel


@pytest.fixture

def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "supersecretkey"

    api = Api(app)
    api.add_resource(Reservas_por_hotel, "/api/v1/reservas/hotel")

    return app.test_client()


@pytest.fixture

def auth_headers(client):
    payload = {
        "sub": "HTL-99281",
        "username": "Hotel Las Colinas Manizales",
        "role": "Accomodation",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
    }
    token = jwt.encode(payload, "supersecretkey", algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return {"Authorization": f"Bearer {token}"}


class _FakeReserva:
    def __init__(self, habitacion_id, estado="pendiente"):
        self.id = f"{habitacion_id}-id"
        self.public_id = f"RSV-{habitacion_id}"
        self.habitacion_id = habitacion_id
        self.user_id = "u-1"
        self.check_in = datetime(2026, 5, 11).date()
        self.check_out = datetime(2026, 5, 15).date()
        self.estado = estado
        self.created_at = datetime(2026, 5, 1, 10, 0, 0)
        self.updated_at = datetime(2026, 5, 1, 11, 0, 0)


class _FakeQuery:
    def __init__(self, reservas):
        self._reservas = reservas

    def all(self):
        return self._reservas


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_reservas_por_hotel_retorna_solo_las_del_sub(client, auth_headers, monkeypatch):
    reservas = [
        _FakeReserva("11111111-1111-1111-1111-111111111111", estado="pendiente"),
        _FakeReserva("22222222-2222-2222-2222-222222222222", estado="confirmada"),
    ]

    def _fake_query(_model):
        return _FakeQuery(reservas)

    def _fake_get(url, timeout=5):
        habitacion_id = url.rsplit("/", 1)[-1]
        if habitacion_id == "11111111-1111-1111-1111-111111111111":
            return _FakeResponse({"hospedaje_id": "HTL-99281"})
        return _FakeResponse({"hospedaje_id": "HTL-99999"})

    monkeypatch.setattr(api_module.reservas_crud.db, "query", _fake_query)
    monkeypatch.setattr(api_module.requests, "get", _fake_get)

    response = client.get("/api/v1/reservas/hotel", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["habitacion_id"] == "11111111-1111-1111-1111-111111111111"
    assert body[0]["public_id"] == "RSV-11111111-1111-1111-1111-111111111111"


def test_reservas_por_hotel_retorna_401_sin_token(client):
    response = client.get("/api/v1/reservas/hotel")

    assert response.status_code == 401
    assert response.get_json()["msg"] == "Se requiere token de autorizacion"
