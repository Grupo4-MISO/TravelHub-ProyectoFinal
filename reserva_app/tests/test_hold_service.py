from datetime import date, timedelta

import pytest
from flask import Flask

import app.services.hold_service as hold_service_module
from app.services.hold_service import HoldService


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    app.config["TESTING"] = True
    with app.app_context():
        yield app


@pytest.fixture
def hold_service(app_ctx):
    return HoldService()


def _date_range():
    today = date.today()
    return today + timedelta(days=1), today + timedelta(days=3)


def test_get_hold_ttl_seconds_default(hold_service):
    assert hold_service._get_hold_ttl_seconds() == 900


def test_get_hold_ttl_seconds_from_config(app_ctx, hold_service):
    app_ctx.config["HOLD_TTL_SECONDS"] = 1200

    assert hold_service._get_hold_ttl_seconds() == 1200


def test_get_hold_ttl_seconds_invalid_config_fallback(app_ctx, hold_service):
    app_ctx.config["HOLD_TTL_SECONDS"] = "abc"

    assert hold_service._get_hold_ttl_seconds() == 900


def test_get_hold_ttl_seconds_lower_bound_one(app_ctx, hold_service):
    app_ctx.config["HOLD_TTL_SECONDS"] = 0

    assert hold_service._get_hold_ttl_seconds() == 1


def test_crear_hold_retorna_error_si_bd_falla(hold_service, monkeypatch):
    check_in, check_out = _date_range()
    monkeypatch.setattr(hold_service, "_verificar_disponibilidad_bd", lambda *_args, **_kwargs: "db error")

    result = hold_service.crear_hold("u1", "h1", check_in, check_out)

    assert result == "db error"


def test_crear_hold_retorna_no_disponible_si_bd_ocupada(hold_service, monkeypatch):
    check_in, check_out = _date_range()
    monkeypatch.setattr(hold_service, "_verificar_disponibilidad_bd", lambda *_args, **_kwargs: False)

    result = hold_service.crear_hold("u1", "h1", check_in, check_out)

    assert result == {
        "disponible": False,
        "motivo": "La habitación ya tiene una reserva confirmada en esas fechas",
    }


def test_crear_hold_retorna_no_disponible_si_hold_de_otro_usuario(hold_service, monkeypatch):
    check_in, check_out = _date_range()
    monkeypatch.setattr(hold_service, "_verificar_disponibilidad_bd", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        hold_service_module.HoldCacheHelper,
        "buscar_hold_cache",
        lambda *_args, **_kwargs: {"user_id": "otro"},
    )

    result = hold_service.crear_hold("u1", "h1", check_in, check_out)

    assert result == {
        "disponible": False,
        "motivo": "La habitación ya tiene una reserva temporal activa en esas fechas",
    }


def test_crear_hold_renueva_hold_existente_mismo_usuario(app_ctx, hold_service, monkeypatch):
    check_in, check_out = _date_range()
    app_ctx.config["HOLD_TTL_SECONDS"] = 777

    monkeypatch.setattr(hold_service, "_verificar_disponibilidad_bd", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        hold_service_module.HoldCacheHelper,
        "buscar_hold_cache",
        lambda *_args, **_kwargs: {"user_id": "u1"},
    )

    called = {}

    def _actualizar_hold_cache(**kwargs):
        called.update(kwargs)
        return {"hold_id": "h-1", "ttl_segundos": kwargs["ttl_segundos"]}

    monkeypatch.setattr(hold_service_module.HoldCacheHelper, "actualizar_hold_cache", _actualizar_hold_cache)

    result = hold_service.crear_hold("u1", "h1", check_in, check_out)

    assert result["disponible"] is True
    assert result["hold"]["hold_id"] == "h-1"
    assert called["ttl_segundos"] == 777


def test_crear_hold_retorna_no_disponible_si_cache_ocupada(hold_service, monkeypatch):
    check_in, check_out = _date_range()
    monkeypatch.setattr(hold_service, "_verificar_disponibilidad_bd", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(hold_service_module.HoldCacheHelper, "buscar_hold_cache", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        hold_service_module.HoldCacheHelper,
        "verificar_disponibilidad_cache",
        lambda *_args, **_kwargs: False,
    )

    result = hold_service.crear_hold("u1", "h1", check_in, check_out)

    assert result == {
        "disponible": False,
        "motivo": "La habitación ya tiene una reserva temporal activa en esas fechas",
    }


def test_crear_hold_crea_hold_con_ttl_configurado(app_ctx, hold_service, monkeypatch):
    check_in, check_out = _date_range()
    app_ctx.config["HOLD_TTL_SECONDS"] = "1200"

    monkeypatch.setattr(hold_service, "_verificar_disponibilidad_bd", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(hold_service_module.HoldCacheHelper, "buscar_hold_cache", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        hold_service_module.HoldCacheHelper,
        "verificar_disponibilidad_cache",
        lambda *_args, **_kwargs: True,
    )

    called = {}

    def _crear_hold_cache(**kwargs):
        called.update(kwargs)
        return {"hold_id": "h-2", "ttl_segundos": kwargs["ttl_segundos"]}

    monkeypatch.setattr(hold_service_module.HoldCacheHelper, "crear_hold_cache", _crear_hold_cache)

    result = hold_service.crear_hold("u1", "h1", check_in, check_out)

    assert result["disponible"] is True
    assert result["hold"]["hold_id"] == "h-2"
    assert called["ttl_segundos"] == 1200


def test_crear_hold_retorna_string_si_ocurre_excepcion(hold_service, monkeypatch):
    check_in, check_out = _date_range()

    def _raise(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(hold_service, "_verificar_disponibilidad_bd", _raise)

    result = hold_service.crear_hold("u1", "h1", check_in, check_out)

    assert result == "boom"


def test_verificar_disponibilidad_bd_delega_en_reserva_crud(hold_service, monkeypatch):
    check_in, check_out = _date_range()
    called = {}

    def _verificar(habitacion_id, ci, co):
        called["habitacion_id"] = habitacion_id
        called["check_in"] = ci
        called["check_out"] = co
        return True

    monkeypatch.setattr(hold_service.reserva_crud, "verificarDisponibilidadHabitacion", _verificar)

    result = hold_service._verificar_disponibilidad_bd("h1", check_in, check_out)

    assert result is True
    assert called == {
        "habitacion_id": "h1",
        "check_in": check_in,
        "check_out": check_out,
    }
