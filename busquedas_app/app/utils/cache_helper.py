import json

class CacheHelper:
    @staticmethod
    def construirCacheKey(ciudad, capacidad, check_in, check_out, country_code, currency_code):
        return f"search:{ciudad}:{capacidad}:{check_in}:{check_out}:{country_code}:{currency_code}"

    @staticmethod
    def obtenerCache(redis_client, key):
        #Data cacheada en Redis
        data_cacheada = redis_client.get(key)

        return json.loads(data_cacheada) if data_cacheada else None

    @staticmethod
    def guardarCache(redis_client, key, value, ttl):
        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )