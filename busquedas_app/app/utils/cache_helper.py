import json

class CacheHelper:
    @staticmethod
    def construirCacheKey(ciudad, capacidad, check_in, check_out, country_code=None, currency_code=None):
        key = f"search:{ciudad}:{capacidad}:{check_in}:{check_out}"
        if country_code and currency_code:
            key = f"{key}:{country_code}:{currency_code}"
        return key

    @staticmethod
    def obtenerCache(redis_client, key):
        try:
            #Data cacheada en Redis
            data_cacheada = redis_client.get(key)

            return json.loads(data_cacheada) if data_cacheada else None
        
        except Exception:
            return None
        
    @staticmethod
    def guardarCache(redis_client, key, value, ttl):
        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        
        except Exception:
            return None