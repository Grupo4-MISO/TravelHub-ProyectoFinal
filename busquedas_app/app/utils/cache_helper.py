import json

class CacheHelper:
    @staticmethod
    def construirCacheKey(ciudad, capacidad, check_in, check_out):
        return f"search:{ciudad}:{capacidad}:{check_in}:{check_out}"

    @staticmethod
    def obtenerCache(redis_client, key):
        return redis_client.get(key)

    @staticmethod
    def guardarCache(redis_client, key, value, ttl):
        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )