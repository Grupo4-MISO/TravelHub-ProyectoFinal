from datetime import datetime, timedelta

import pytest
from flask import Flask
from flask_restful import Api

import app.api.api as api_module
from app.api.api import HoldReserva


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True

    api = Api(app)
    api.add_resource(HoldReserva, "/api/v1/reservas/hold")

    return app.test_client()


def _future_dates(days_start=1, days_end=3):
    today = datetime.now().date()
    check_in = (today + timedelta(days=days_start)).strftime("%Y-%m-%d")
    check_out = (today + timedelta(days=days_end)).strftime("%Y-%m-%d")
    return check_in, check_out


def _base_payload():
    check_in, check_out = _future_dates()
    return {
        "user_id": "u-1",
        "habitacion_id": 101,
        "check_in": check_in,
        "check_out": check_out,
    }


def test_hold_reserva_retorna_400_si_falta_campo_requerido(client):
    payload = _base_payload()
    payload.pop("user_id")

    response = client.post("/api/v1/reservas/hold", json=payload)

    assert response.status_code == 400
    assert response.get_json()["msg"] == "El campo user_id es requerido"


def test_hold_reserva_retorna_400_si_formato_fecha_invalido(client):
    payload = _base_payload()
    payload["check_in"] = "10/04/2026"

    response = client.post("/api/v1/reservas/hold", json=payload)

    assert response.status_code == 400
    assert response.get_json()["msg"] == "Formato de fecha inválido, use YYYY-MM-DD"


def test_hold_reserva_retorna_400_si_checkin_no_es_anterior_checkout(client):
    check_in, _ = _future_dates()
    payload = _base_payload()
    payload["check_in"] = check_in
    payload["check_out"] = check_in

    response = client.post("/api/v1/reservas/hold", json=payload)

    assert response.status_code == 400
    assert response.get_json()["msg"] == "La fecha de check-out debe ser posterior a la fecha de check-in"


def test_hold_reserva_retorna_400_si_checkout_no_es_futuro(client):
    today = datetime.now().date()
    payload = _base_payload()
    payload["check_in"] = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    payload["check_out"] = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.post("/api/v1/reservas/hold", json=payload)

    assert response.status_code == 400
    assert response.get_json()["msg"] == "La fecha de check-out debe ser una fecha futura"


def test_hold_reserva_retorna_501_si_servicio_no_implementado(client, monkeypatch):
    def _raise_not_implemented(*_args, **_kwargs):
        raise NotImplementedError("pendiente")

    monkeypatch.setattr(api_module.hold_service, "crear_hold", _raise_not_implemented)

    response = client.post("/api/v1/reservas/hold", json=_base_payload())

    assert response.status_code == 501
    body = response.get_json()
    assert body["msg"] == "Funcionalidad pendiente de implementación"
    assert "pendiente" in body["detalle"]


def test_hold_reserva_retorna_500_si_servicio_devuelve_error_string(client, monkeypatch):
    monkeypatch.setattr(api_module.hold_service, "crear_hold", lambda *_args, **_kwargs: "db error")

    response = client.post("/api/v1/reservas/hold", json=_base_payload())

    assert response.status_code == 500
    body = response.get_json()
    assert body["msg"] == "Error al crear la reserva temporal"
    assert body["error"] == "db error"


def test_hold_reserva_retorna_409_si_no_hay_disponibilidad(client, monkeypatch):
    monkeypatch.setattr(
        api_module.hold_service,
        "crear_hold",
        lambda *_args, **_kwargs: {"disponible": False, "motivo": "ocupada"},
    )

    response = client.post("/api/v1/reservas/hold", json=_base_payload())

    assert response.status_code == 409
    assert response.get_json()["msg"] == "ocupada"


def test_hold_reserva_retorna_201_si_hold_creado(client, monkeypatch):
    resultado = {
        "disponible": True,
        "hold": {
            "hold_id": "h-123",
            "habitacion_id": 101,
            "ttl": 900,
        },
    }
    monkeypatch.setattr(api_module.hold_service, "crear_hold", lambda *_args, **_kwargs: resultado)

    response = client.post("/api/v1/reservas/hold", json=_base_payload())

    assert response.status_code == 201
    assert response.get_json() == resultado
