import json
import os
import time
import uuid
from datetime import date, datetime

import redis


class HoldCacheHelper:
    """Helper de operaciones sobre Redis para reservas temporales (holds)."""

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client:
            return cls._client

        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            cls._client = redis.Redis.from_url(redis_url, decode_responses=True)
            return cls._client

        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        redis_ssl = os.getenv('REDIS_SSL', 'false').lower() in ('1', 'true', 'yes', 'on')

        redis_kwargs = {
            'host': redis_host,
            'port': redis_port,
            'db': redis_db,
            'decode_responses': True,
        }
        if redis_ssl:
            redis_kwargs['ssl'] = True

        cls._client = redis.Redis(**redis_kwargs)
        return cls._client

    @staticmethod
    def _normalizar_fecha(fecha):
        if isinstance(fecha, datetime):
            return fecha.date()
        if isinstance(fecha, date):
            return fecha
        return datetime.strptime(str(fecha), '%Y-%m-%d').date()

    @staticmethod
    def _hay_traslape(inicio_a, fin_a, inicio_b, fin_b):
        return not (fin_a <= inicio_b or inicio_a >= fin_b)

    @staticmethod
    def _construir_hold_key(habitacion_id, check_in, check_out):
        return f"hold:{habitacion_id}:{check_in}:{check_out}"

    @classmethod
    def buscar_hold_cache(cls, habitacion_id, check_in, check_out):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)
        key = cls._construir_hold_key(habitacion_id, check_in_date, check_out_date)

        raw = cliente.get(key)
        if not raw:
            return None

        hold = json.loads(raw)
        hold['ttl_restante'] = max(cliente.ttl(key), 0)
        return hold

    @classmethod
    def verificar_disponibilidad_cache(cls, habitacion_id, check_in, check_out):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)

        pattern = f"hold:{habitacion_id}:*"
        for key in cliente.scan_iter(match=pattern):
            raw = cliente.get(key)
            if not raw:
                continue

            hold = json.loads(raw)
            hold_check_in = cls._normalizar_fecha(hold.get('check_in'))
            hold_check_out = cls._normalizar_fecha(hold.get('check_out'))

            if cls._hay_traslape(check_in_date, check_out_date, hold_check_in, hold_check_out):
                return False

        return True

    @classmethod
    def crear_hold_cache(cls, user_id, habitacion_id, check_in, check_out, ttl_segundos=900):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)

        hold = {
            'hold_id': str(uuid.uuid4()),
            'user_id': str(user_id),
            'habitacion_id': str(habitacion_id),
            'check_in': check_in_date.isoformat(),
            'check_out': check_out_date.isoformat(),
            'expira_en': int(time.time()) + ttl_segundos,
            'ttl_segundos': ttl_segundos,
        }

        key = cls._construir_hold_key(habitacion_id, check_in_date, check_out_date)
        cliente.setex(key, ttl_segundos, json.dumps(hold))
        return hold

    @classmethod
    def actualizar_hold_cache(cls, habitacion_id, check_in, check_out, user_id=None, ttl_segundos=900):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)
        key = cls._construir_hold_key(habitacion_id, check_in_date, check_out_date)

        raw = cliente.get(key)
        if not raw:
            return None

        hold = json.loads(raw)
        if user_id and str(hold.get('user_id')) != str(user_id):
            return None

        hold['expira_en'] = int(time.time()) + ttl_segundos
        hold['ttl_segundos'] = ttl_segundos
        cliente.setex(key, ttl_segundos, json.dumps(hold))
        hold['ttl_restante'] = ttl_segundos
        return hold
