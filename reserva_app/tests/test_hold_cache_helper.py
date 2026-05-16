import json
import time
from datetime import date, datetime, timedelta

import app.utils.hold_cache_helper as hold_cache_module
from app.utils.hold_cache_helper import HoldCacheHelper


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.ttls = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value
        self.ttls[key] = ttl

    def ttl(self, key):
        return self.ttls.get(key, -1)

    def scan_iter(self, match=None):
        keys = list(self.store.keys())
        if not match:
            for key in keys:
                yield key
            return

        prefix = match[:-1] if match.endswith("*") else match
        for key in keys:
            if key.startswith(prefix):
                yield key

    def delete(self, key):
        if key not in self.store:
            return 0

        del self.store[key]
        self.ttls.pop(key, None)
        return 1


class FakeRedisFactory:
    last_from_url = None
    last_init_kwargs = None

    def __init__(self, **kwargs):
        FakeRedisFactory.last_init_kwargs = kwargs

    @classmethod
    def from_url(cls, url, decode_responses=True):
        cls.last_from_url = (url, decode_responses)
        return FakeRedis()


def _future_dates(days_start=1, days_end=3):
    today = date.today()
    return today + timedelta(days=days_start), today + timedelta(days=days_end)


def _hold_json(user_id="u1", habitacion_id="h1", check_in=None, check_out=None):
    ci, co = _future_dates() if (check_in is None or check_out is None) else (check_in, check_out)
    return json.dumps(
        {
            "id": "h-1",
            "public_id": "RSV-HOLD0001",
            "user_id": user_id,
            "habitacion_id": habitacion_id,
            "check_in": ci.isoformat(),
            "check_out": co.isoformat(),
            "estado": "pendiente",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "expira_en": int(time.time()) + 900,
            "ttl_segundos": 900,
        }
    )


def setup_function():
    HoldCacheHelper._client = None


def test_normalizar_fecha_datetime():
    dt = datetime(2026, 4, 10, 12, 30, 0)

    result = HoldCacheHelper._normalizar_fecha(dt)

    assert result == date(2026, 4, 10)


def test_normalizar_fecha_date():
    d = date(2026, 4, 10)

    result = HoldCacheHelper._normalizar_fecha(d)

    assert result == d


def test_normalizar_fecha_string():
    result = HoldCacheHelper._normalizar_fecha("2026-04-10")

    assert result == date(2026, 4, 10)


def test_hay_traslape_true():
    a1 = date(2026, 4, 10)
    a2 = date(2026, 4, 14)
    b1 = date(2026, 4, 12)
    b2 = date(2026, 4, 16)

    assert HoldCacheHelper._hay_traslape(a1, a2, b1, b2) is True


def test_hay_traslape_false_limite_compartido():
    a1 = date(2026, 4, 10)
    a2 = date(2026, 4, 12)
    b1 = date(2026, 4, 12)
    b2 = date(2026, 4, 16)

    assert HoldCacheHelper._hay_traslape(a1, a2, b1, b2) is False


def test_construir_hold_key():
    result = HoldCacheHelper._construir_hold_key("101", "2026-04-10", "2026-04-12")

    assert result == "hold:101:2026-04-10:2026-04-12"


def test_buscar_hold_cache_retorna_none_si_no_existe():
    HoldCacheHelper._client = FakeRedis()

    result = HoldCacheHelper.buscar_hold_cache("h1", "2026-04-10", "2026-04-12")

    assert result is None


def test_buscar_hold_cache_retorna_hold_con_ttl():
    client = FakeRedis()
    key = HoldCacheHelper._construir_hold_key("h1", date(2026, 4, 10), date(2026, 4, 12))
    client.setex(key, 850, _hold_json(check_in=date(2026, 4, 10), check_out=date(2026, 4, 12)))
    HoldCacheHelper._client = client

    result = HoldCacheHelper.buscar_hold_cache("h1", "2026-04-10", "2026-04-12")

    assert result is not None
    assert result["id"] == "h-1"
    assert result["public_id"] == "RSV-HOLD0001"
    assert result["estado"] == "pendiente"
    assert result["ttl_restante"] == 850


def test_verificar_disponibilidad_cache_true_sin_traslape():
    client = FakeRedis()
    client.setex(
        "hold:h1:2026-04-10:2026-04-12",
        900,
        _hold_json(check_in=date(2026, 4, 10), check_out=date(2026, 4, 12)),
    )
    HoldCacheHelper._client = client

    # No traslapa con [2026-04-12, 2026-04-14)
    result = HoldCacheHelper.verificar_disponibilidad_cache("h1", "2026-04-12", "2026-04-14")

    assert result is True


def test_verificar_disponibilidad_cache_false_con_traslape():
    client = FakeRedis()
    client.setex(
        "hold:h1:2026-04-10:2026-04-14",
        900,
        _hold_json(check_in=date(2026, 4, 10), check_out=date(2026, 4, 14)),
    )
    HoldCacheHelper._client = client

    # Traslapa con [2026-04-12, 2026-04-16)
    result = HoldCacheHelper.verificar_disponibilidad_cache("h1", "2026-04-12", "2026-04-16")

    assert result is False


def test_verificar_disponibilidad_cache_para_usuario_true_si_hold_exacto_es_del_mismo_usuario():
    client = FakeRedis()
    client.setex(
        "hold:h1:2026-04-10:2026-04-14",
        900,
        _hold_json(user_id="u1", check_in=date(2026, 4, 10), check_out=date(2026, 4, 14)),
    )
    HoldCacheHelper._client = client

    result = HoldCacheHelper.verificar_disponibilidad_cache_para_usuario("h1", "2026-04-10", "2026-04-14", "u1")

    assert result is True


def test_verificar_disponibilidad_cache_para_usuario_false_si_hold_es_de_otro_usuario():
    client = FakeRedis()
    client.setex(
        "hold:h1:2026-04-10:2026-04-14",
        900,
        _hold_json(user_id="otro", check_in=date(2026, 4, 10), check_out=date(2026, 4, 14)),
    )
    HoldCacheHelper._client = client

    result = HoldCacheHelper.verificar_disponibilidad_cache_para_usuario("h1", "2026-04-10", "2026-04-14", "u1")

    assert result is False


def test_verificar_disponibilidad_cache_para_usuario_false_si_hay_otro_hold_traslapado():
    client = FakeRedis()
    client.setex(
        "hold:h1:2026-04-10:2026-04-14",
        900,
        _hold_json(user_id="u1", check_in=date(2026, 4, 10), check_out=date(2026, 4, 14)),
    )
    client.setex(
        "hold:h1:2026-04-12:2026-04-16",
        900,
        _hold_json(user_id="otro", check_in=date(2026, 4, 12), check_out=date(2026, 4, 16)),
    )
    HoldCacheHelper._client = client

    result = HoldCacheHelper.verificar_disponibilidad_cache_para_usuario("h1", "2026-04-10", "2026-04-14", "u1")

    assert result is False


def test_crear_hold_cache_persiste_hold_y_ttl():
    client = FakeRedis()
    HoldCacheHelper._client = client
    check_in, check_out = _future_dates()

    hold = HoldCacheHelper.crear_hold_cache(
        user_id="u1",
        habitacion_id="101",
        check_in=check_in,
        check_out=check_out,
        ttl_segundos=1200,
    )

    key = HoldCacheHelper._construir_hold_key("101", check_in, check_out)
    persisted = json.loads(client.get(key))

    assert hold["user_id"] == "u1"
    assert hold["habitacion_id"] == "101"
    assert hold["estado"] == "pendiente"
    assert hold["public_id"].startswith("RSV-")
    assert hold["ttl_segundos"] == 1200
    assert persisted["id"] == hold["id"]
    assert client.ttl(key) == 1200


def test_actualizar_hold_cache_none_si_no_existe():
    HoldCacheHelper._client = FakeRedis()

    result = HoldCacheHelper.actualizar_hold_cache(
        habitacion_id="h1",
        check_in="2026-04-10",
        check_out="2026-04-12",
        user_id="u1",
        ttl_segundos=300,
    )

    assert result is None


def test_actualizar_hold_cache_none_si_user_no_coincide():
    client = FakeRedis()
    key = HoldCacheHelper._construir_hold_key("h1", date(2026, 4, 10), date(2026, 4, 12))
    client.setex(key, 900, _hold_json(user_id="otro", check_in=date(2026, 4, 10), check_out=date(2026, 4, 12)))
    HoldCacheHelper._client = client

    result = HoldCacheHelper.actualizar_hold_cache(
        habitacion_id="h1",
        check_in="2026-04-10",
        check_out="2026-04-12",
        user_id="u1",
        ttl_segundos=300,
    )

    assert result is None


def test_actualizar_hold_cache_renueva_ttl_y_retorma_hold_actualizado():
    client = FakeRedis()
    key = HoldCacheHelper._construir_hold_key("h1", date(2026, 4, 10), date(2026, 4, 12))
    client.setex(key, 900, _hold_json(user_id="u1", check_in=date(2026, 4, 10), check_out=date(2026, 4, 12)))
    HoldCacheHelper._client = client

    result = HoldCacheHelper.actualizar_hold_cache(
        habitacion_id="h1",
        check_in="2026-04-10",
        check_out="2026-04-12",
        user_id="u1",
        ttl_segundos=450,
    )

    assert result is not None
    assert result["ttl_segundos"] == 450
    assert result["ttl_restante"] == 450
    assert client.ttl(key) == 450


def test_eliminar_hold_cache_false_si_no_existe():
    HoldCacheHelper._client = FakeRedis()

    result = HoldCacheHelper.eliminar_hold_cache("h1", "2026-04-10", "2026-04-12")

    assert result is False


def test_eliminar_hold_cache_false_si_user_no_coincide():
    client = FakeRedis()
    key = HoldCacheHelper._construir_hold_key("h1", date(2026, 4, 10), date(2026, 4, 12))
    client.setex(key, 900, _hold_json(user_id="otro", check_in=date(2026, 4, 10), check_out=date(2026, 4, 12)))
    HoldCacheHelper._client = client

    result = HoldCacheHelper.eliminar_hold_cache("h1", "2026-04-10", "2026-04-12", user_id="u1")

    assert result is False
    assert client.get(key) is not None


def test_eliminar_hold_cache_true_si_elimina_hold_del_mismo_usuario():
    client = FakeRedis()
    key = HoldCacheHelper._construir_hold_key("h1", date(2026, 4, 10), date(2026, 4, 12))
    client.setex(key, 900, _hold_json(user_id="u1", check_in=date(2026, 4, 10), check_out=date(2026, 4, 12)))
    HoldCacheHelper._client = client

    result = HoldCacheHelper.eliminar_hold_cache("h1", "2026-04-10", "2026-04-12", user_id="u1")

    assert result is True
    assert client.get(key) is None


def test_get_client_usa_redis_url(monkeypatch):
    HoldCacheHelper._client = None
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setattr(hold_cache_module.redis, "Redis", FakeRedisFactory)

    client = HoldCacheHelper._get_client()

    assert isinstance(client, FakeRedis)
    assert FakeRedisFactory.last_from_url == ("redis://localhost:6379/0", True)


def test_get_client_usa_host_port_db(monkeypatch):
    HoldCacheHelper._client = None
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("REDIS_HOST", "redis-host")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("REDIS_DB", "3")
    monkeypatch.setattr(hold_cache_module.redis, "Redis", FakeRedisFactory)

    client = HoldCacheHelper._get_client()
    print(FakeRedisFactory.last_init_kwargs)
    assert isinstance(client, FakeRedisFactory)
    assert FakeRedisFactory.last_init_kwargs == {
        'host': "redis-host",
        "decode_responses": True,
        'port': 6379,
        "ssl": True,
    }
