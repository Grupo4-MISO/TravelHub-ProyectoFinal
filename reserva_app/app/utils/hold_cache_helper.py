import json
import os
import time
from datetime import date, datetime

import redis
from app.domain.hold import Hold
from app.mappers.hold_mapper import HoldMapper


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
            # pass ssl only when explicitly requested
            cls._client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                ssl=True,
            )
        else:
            cls._client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
            )

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

        hold = HoldMapper.from_cache_json(raw)
        hold = hold.model_copy(update={'ttl_restante': max(cliente.ttl(key), 0)})
        return HoldMapper.to_public_dict(hold)

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

            hold = HoldMapper.from_cache_json(raw)
            hold_check_in = hold.check_in
            hold_check_out = hold.check_out

            if cls._hay_traslape(check_in_date, check_out_date, hold_check_in, hold_check_out):
                return False

        return True


    @classmethod
    def verificar_disponibilidad_cache_para_usuario(cls, habitacion_id, check_in, check_out, user_id):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)
        user_id_str = str(user_id)

        pattern = f"hold:{habitacion_id}:*"
        for key in cliente.scan_iter(match=pattern):
            raw = cliente.get(key)
            if not raw:
                continue

            hold = HoldMapper.from_cache_json(raw)
            if not cls._hay_traslape(check_in_date, check_out_date, hold.check_in, hold.check_out):
                continue

            es_hold_propio_exacto = (
                hold.user_id == user_id_str
                and hold.check_in == check_in_date
                and hold.check_out == check_out_date
            )

            if es_hold_propio_exacto:
                continue

            return False

        return True

    @classmethod
    def crear_hold_cache(cls, user_id, habitacion_id, check_in, check_out, ttl_segundos=900):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)

        hold = Hold.crear(
            user_id=user_id,
            habitacion_id=habitacion_id,
            check_in=check_in_date,
            check_out=check_out_date,
            ttl_segundos=ttl_segundos,
        )

        key = cls._construir_hold_key(habitacion_id, check_in_date, check_out_date)
        cliente.setex(key, ttl_segundos, json.dumps(HoldMapper.to_cache_dict(hold)))
        return HoldMapper.to_public_dict(hold)

    @classmethod
    def actualizar_hold_cache(cls, habitacion_id, check_in, check_out, user_id=None, ttl_segundos=900):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)
        key = cls._construir_hold_key(habitacion_id, check_in_date, check_out_date)

        raw = cliente.get(key)
        if not raw:
            return None

        hold = HoldMapper.from_cache_json(raw)
        if user_id and hold.user_id != str(user_id):
            return None

        hold = hold.model_copy(
            update={
                'expira_en': int(time.time()) + ttl_segundos,
                'ttl_segundos': ttl_segundos,
                'ttl_restante': ttl_segundos,
            }
        )
        cliente.setex(key, ttl_segundos, json.dumps(HoldMapper.to_cache_dict(hold)))
        return HoldMapper.to_public_dict(hold)

    @classmethod
    def eliminar_hold_cache(cls, habitacion_id, check_in, check_out, user_id=None):
        cliente = cls._get_client()
        check_in_date = cls._normalizar_fecha(check_in)
        check_out_date = cls._normalizar_fecha(check_out)
        key = cls._construir_hold_key(habitacion_id, check_in_date, check_out_date)

        raw = cliente.get(key)
        if not raw:
            return False

        hold = HoldMapper.from_cache_json(raw)
        if user_id and hold.user_id != str(user_id):
            return False

        return bool(cliente.delete(key))
