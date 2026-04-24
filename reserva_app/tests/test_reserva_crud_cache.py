from datetime import date

from app.services.reserva_crud import ReservaCRUD


def test_existe_reserva_en_cache_true(monkeypatch):
    crud = ReservaCRUD()

    monkeypatch.setattr(
        "app.services.reserva_crud.HoldCacheHelper.verificar_disponibilidad_cache",
        lambda *_args, **_kwargs: False,
    )

    result = crud.existeReservaEnCache("h1", date(2026, 4, 10), date(2026, 4, 12))

    assert result is True


def test_existe_reserva_en_cache_false(monkeypatch):
    crud = ReservaCRUD()

    monkeypatch.setattr(
        "app.services.reserva_crud.HoldCacheHelper.verificar_disponibilidad_cache",
        lambda *_args, **_kwargs: True,
    )

    result = crud.existeReservaEnCache("h1", date(2026, 4, 10), date(2026, 4, 12))

    assert result is False


def test_existe_reserva_en_cache_false_si_hold_es_del_mismo_usuario(monkeypatch):
    crud = ReservaCRUD()

    monkeypatch.setattr(
        "app.services.reserva_crud.HoldCacheHelper.verificar_disponibilidad_cache_para_usuario",
        lambda *_args, **_kwargs: True,
    )

    result = crud.existeReservaEnCache("h1", date(2026, 4, 10), date(2026, 4, 12), user_id="u1")

    assert result is False


def test_verificar_disponibilidad_usa_sql_y_cache(monkeypatch):
    crud = ReservaCRUD()

    monkeypatch.setattr(
        crud,
        "_obtener_habitaciones_ocupadas",
        lambda *_args, **_kwargs: {"h1"},
    )
    monkeypatch.setattr(
        crud,
        "_obtener_habitaciones_ocupadas_cache",
        lambda *_args, **_kwargs: {"h2"},
    )

    result = crud.verificarDisponibilidad(["h1", "h2", "h3"], date(2026, 4, 10), date(2026, 4, 12))

    assert result == ["h3"]


def test_verificar_disponibilidad_habitacion_false_si_esta_en_cache(monkeypatch):
    crud = ReservaCRUD()

    monkeypatch.setattr(
        crud,
        "_obtener_habitaciones_ocupadas",
        lambda *_args, **_kwargs: set(),
    )
    monkeypatch.setattr(
        crud,
        "existeReservaEnCache",
        lambda *_args, **_kwargs: True,
    )

    result = crud.verificarDisponibilidadHabitacion("h1", date(2026, 4, 10), date(2026, 4, 12))

    assert result is False


def test_crear_reserva_limpia_hold_si_user_id_presente(monkeypatch):
    crud = ReservaCRUD()

    class FakeReserva:
        id = "11111111-1111-1111-1111-111111111111"
        public_id = "RSV-ABC12345"
        habitacion_id = "1ecf9ccf-fc58-4a44-95c9-b4dd8c5bf5b8"
        check_in = date(2026, 4, 10)
        check_out = date(2026, 4, 12)
        estado = "confirmada"
        created_at = None
        updated_at = None

    deleted = {"called": False}

    monkeypatch.setattr(crud, "verificarDisponibilidadHabitacion", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("app.services.reserva_crud.ReservaORM", lambda **_kwargs: FakeReserva())
    monkeypatch.setattr(crud.db, "add", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(crud.db, "commit", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(crud.db, "refresh", lambda *_args, **_kwargs: None)

    def _eliminar_hold_cache(*_args, **_kwargs):
        deleted["called"] = True
        return True

    monkeypatch.setattr("app.services.reserva_crud.HoldCacheHelper.eliminar_hold_cache", _eliminar_hold_cache)

    result = crud.crearReserva(
        "1ecf9ccf-fc58-4a44-95c9-b4dd8c5bf5b8",
        date(2026, 4, 10),
        date(2026, 4, 12),
        user_id="u1",
    )

    assert isinstance(result, dict)
    assert deleted["called"] is True
