from datetime import datetime, timedelta

import pytest
from flask import Flask
from flask_restful import Api

import app.api.api as api_module
from app.api.api import CrearReserva


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True

    api = Api(app)
    api.add_resource(CrearReserva, "/api/v1/reservas/crear")

    return app.test_client()


def _future_dates(days_start=1, days_end=3):
    today = datetime.now().date()
    check_in = (today + timedelta(days=days_start)).strftime("%Y-%m-%d")
    check_out = (today + timedelta(days=days_end)).strftime("%Y-%m-%d")
    return check_in, check_out


def _base_payload():
    check_in, check_out = _future_dates()
    return {
        "habitacion_id": "1ecf9ccf-fc58-4a44-95c9-b4dd8c5bf5b8",
        "check_in": check_in,
        "check_out": check_out,
    }


def test_crear_reserva_retorna_400_si_falta_habitacion_id(client):
    payload = _base_payload()
    payload.pop("habitacion_id")

    response = client.post("/api/v1/reservas/crear", json=payload)

    assert response.status_code == 400
    assert response.get_json()["msg"] == "El campo habitacion_id es requerido"


def test_crear_reserva_retorna_400_si_fecha_invalida(client):
    payload = _base_payload()
    payload["check_in"] = "10/04/2026"

    response = client.post("/api/v1/reservas/crear", json=payload)

    assert response.status_code == 400
    assert response.get_json()["msg"] == "La fecha de check-in debe estar en formato YYYY-MM-DD"


def test_crear_reserva_retorna_409_si_no_hay_disponibilidad(client, monkeypatch):
    monkeypatch.setattr(
        api_module.reservas_crud,
        "crearReserva",
        lambda *_args, **_kwargs: "La habitación no está disponible para las fechas seleccionadas",
    )

    response = client.post("/api/v1/reservas/crear", json=_base_payload())

    assert response.status_code == 409
    assert response.get_json()["msg"] == "La habitación no está disponible para las fechas seleccionadas"


def test_crear_reserva_retorna_201_si_se_crea_en_sql(client, monkeypatch):
    reserva = {
        "id": "bd9f0966-e7c9-4cb6-9ab6-8cd444da0000",
        "public_id": "RSV-ABC12345",
        "habitacion_id": "1ecf9ccf-fc58-4a44-95c9-b4dd8c5bf5b8",
        "check_in": _base_payload()["check_in"],
        "check_out": _base_payload()["check_out"],
        "estado": "pendiente",
        "created_at": None,
        "updated_at": None,
    }
    monkeypatch.setattr(api_module.reservas_crud, "crearReserva", lambda *_args, **_kwargs: reserva)

    response = client.post("/api/v1/reservas/crear", json=_base_payload())

    assert response.status_code == 201
    body = response.get_json()
    assert body["msg"] == "Reserva creada correctamente"
    assert body["reserva"] == reserva


def test_crear_reserva_envia_user_id_a_servicio(client, monkeypatch):
    captured = {}

    def _crear_reserva(habitacion_id, check_in, check_out, user_id=None):
        captured["habitacion_id"] = habitacion_id
        captured["user_id"] = user_id
        return {
            "id": "bd9f0966-e7c9-4cb6-9ab6-8cd444da0000",
            "public_id": "RSV-ABC12345",
            "habitacion_id": habitacion_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "estado": "pendiente",
            "created_at": None,
            "updated_at": None,
        }

    monkeypatch.setattr(api_module.reservas_crud, "crearReserva", _crear_reserva)

    payload = _base_payload()
    payload["user_id"] = "u1"

    response = client.post("/api/v1/reservas/crear", json=payload)

    assert response.status_code == 201
    assert captured["user_id"] == "u1"
