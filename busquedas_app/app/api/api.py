from app.utils.inventario_helper import InventarioHelper
from app.utils.busquedas_helper import BusquedasHelper
from app.utils.reserva_helper import ReservaHelper
from app.utils.cache_helper import CacheHelper
from flask_restful import Resource
from flask import request
import redis
import os

#Traemos las variables de entorno para las URLs de los microservicios
INVENTARIOS_URL = os.getenv('INVENTARIOS_URL')
RESERVAS_URL = os.getenv('RESERVAS_URL')
REDIS_HOST = os.getenv('REDIS_HOST')

#Conectamos a Redis
redis_client = redis.Redis(
    host = REDIS_HOST,
    port = 6379,
    decode_responses = True,
    ssl = True
)

class SearchHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class Search(Resource):
    def get(self):
        #Extraemos parametros de busqueda
        ciudad = request.args.get('ciudad')
        capacidad = request.args.get('capacidad')
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')

        #Construimos la clave de cache
        cache_key = CacheHelper.construirCacheKey(ciudad, capacidad, check_in, check_out)

        #Intentamos obtener resultados de cache
        disponibles = CacheHelper.obtenerCache(redis_client, cache_key)

        if not disponibles:
            #Consulta al microservicio de inventario
            hospedajes_habitaciones = InventarioHelper.getInventario(INVENTARIOS_URL, ciudad, capacidad)

            #Validamos que la respuesta no sea error
            if isinstance(hospedajes_habitaciones, str):
                return {'msg': 'Error al buscar habitaciones', 'error': hospedajes_habitaciones}, 500
            
            #Construimos los ids de habitaciones
            habitaciones_ids = [habitacion.get('habitacion_id') for habitacion in hospedajes_habitaciones]

            #Consulta al microservicio de reservas
            disponibles = ReservaHelper.disponibilidadReserva(RESERVAS_URL, habitaciones_ids, check_in, check_out)

            #Validamos que la respuesta no sea error
            if isinstance(disponibles, str):
                return {'msg': 'Error al verificar disponibilidad', 'error': disponibles}, 500

            #Filtramos habitaciones disponibles
            hospedajes_habitaciones_disponibles = BusquedasHelper.filtrarHabitacionesDisponibles(hospedajes_habitaciones, disponibles)
            
            #Guardamos en cache
            CacheHelper.guardarCache(redis_client, cache_key, hospedajes_habitaciones_disponibles, ttl = 120)

            return hospedajes_habitaciones_disponibles, 200

        print(disponibles)
        return disponibles, 200