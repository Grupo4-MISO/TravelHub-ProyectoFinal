from app.utils.inventario_helper import InventarioHelper
from app.utils.busquedas_helper import BusquedasHelper
from app.utils.reserva_helper import ReservaHelper
from app.errors.exceptions import APIError, NotFoundError
from app.utils.cache_helper import CacheHelper
from flask_restful import Resource
from flask import request
import redis
import os
import logging
import requests

#Traemos las variables de entorno para las URLs de los microservicios
INVENTARIOS_URL = os.getenv('INVENTARIOS_URL', 'http://127.0.0.1:3000')
RESERVAS_URL = os.getenv('RESERVAS_URL', 'https://dpyrs6tuvj15e.cloudfront.net')
REDIS_HOST = os.getenv('REDIS_HOST')
TARIFAS_URL = os.getenv('TARIFAS_URL', 'http://tarifas_app:3008')

# Logger
logger = logging.getLogger(__name__)
if not logger.handlers:
  logging.basicConfig(level=logging.INFO)

#Conectamos a Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
    ssl=True
)

class SearchHealth(Resource):
    def get(self):
        """---
        tags:
          - Salud
        summary: Verifica el estado del servicio de búsquedas
        description: Retorna un estado simple para confirmar que el microservicio está activo.
        responses:
          200:
            description: Servicio disponible
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
        """
        return {'status': 'healthy'}, 200


class SeedDB(Resource):
    def post(self):
        """---
        tags:
          - Mantenimiento
        summary: Inicializa datos de prueba para búsquedas
        description: Crea habitaciones asociadas a reservas de prueba usando los microservicios de inventario y reservas.
        responses:
          200:
            description: Datos sembrados correctamente
          500:
            description: Error interno al ejecutar el seed
        """
        try:
            habitaciones = InventarioHelper.seed_reservas_ids(INVENTARIOS_URL)
            result = ReservaHelper.seedReservas(RESERVAS_URL, 5, habitaciones)
            return result, 200
        except Exception as e:
            return {"ok": False, "error": str(e)}, 500


class Search(Resource):
    def get(self):
        """---
        tags:
          - Búsquedas
        summary: Busca hospedajes disponibles
        description: Consulta inventario, valida disponibilidad por fechas y retorna los hospedajes filtrados.
        parameters:
          - in: query
            name: ciudad
            type: string
            required: true
            description: Ciudad de búsqueda.
            example: Bogota
          - in: query
            name: capacidad
            type: integer
            required: true
            description: Cantidad mínima de huéspedes.
            example: 2
          - in: query
            name: check_in
            type: string
            required: true
            description: Fecha de ingreso en formato YYYY-MM-DD.
            example: 2026-05-10
          - in: query
            name: check_out
            type: string
            required: true
            description: Fecha de salida en formato YYYY-MM-DD.
            example: 2026-05-15
          - in: query
            name: country_code
            type: string
            required: false
            description: Código de país para el contexto de búsqueda.
            example: CO
          - in: query
            name: currency_code
            type: string
            required: false
            description: Código de moneda para obtener tarifas.
            example: COP
        responses:
          200:
            description: Hospedajes disponibles encontrados
            schema:
              type: array
              items:
                type: object
          400:
            description: Parámetros inválidos o incompletos
          404:
            description: No se encontraron hospedajes o habitaciones disponibles
          500:
            description: Error interno al procesar la búsqueda
        """
        try:
          #Extraemos parametros de busqueda
          ciudad = request.args.get('ciudad')
          capacidad = request.args.get('capacidad')
          check_in = request.args.get('check_in')
          check_out = request.args.get('check_out')
          country_code = request.args.get('country_code')
          currency_code = request.args.get('currency_code')

          #Validamos parametros de busqueda
          BusquedasHelper.validacionCampoCiudad(ciudad)
          BusquedasHelper.validacionCampoCapacidad(capacidad)
          BusquedasHelper.validacionCampoFechas(check_in, check_out)

          #Construimos la clave de cache
          cache_key = CacheHelper.construirCacheKey(
            ciudad,
            capacidad,
            check_in,
            check_out,
            country_code,
            currency_code
          )

          #Intentamos obtener resultados de cache
          disponibles = CacheHelper.obtenerCache(redis_client, cache_key)

          if not disponibles:
            #Consulta al microservicio de inventario
            hospedajes_habitaciones = InventarioHelper.getInventario(
              INVENTARIOS_URL,
              ciudad,
              capacidad,
              currency_code
            )

            #Validamos que existan hospedajes para la ciudad y capacidad especificada
            if not hospedajes_habitaciones:
              raise NotFoundError('No se encontraron hospedajes disponibles para la ciudad o capacidad especificada')

            #Construimos los ids de habitaciones
            habitaciones_ids = [
              habitacion.get('habitacion_id')
              for habitacion in hospedajes_habitaciones
            ]

            #Consulta al microservicio de reservas
            disponibles = ReservaHelper.disponibilidadReserva(
              RESERVAS_URL,
              habitaciones_ids,
              check_in,
              check_out
            )

            #Validamos que existan habitaciones disponibles para las fechas especificadas
            if not disponibles:
              raise NotFoundError('No se encontraron habitaciones disponibles para las fechas especificadas')

            #Filtramos habitaciones disponibles
            hospedajes_habitaciones_disponibles = BusquedasHelper.filtrarHabitacionesDisponibles(
              hospedajes_habitaciones,
              disponibles
            )

            # Intentamos obtener tarifas vigentes una sola vez y armar un mapa (hotel_id, categoria) -> tarifa
            try:
              tarifas_endpoint = f"{TARIFAS_URL}/tarifas/publicas"
              hotel_ids = sorted({str(hab.get('hospedaje_id') or hab.get('hospedajeId') or '').strip() for hab in hospedajes_habitaciones_disponibles if (hab.get('hospedaje_id') or hab.get('hospedajeId'))})
              logger.info("Consultando tarifas vigentes en %s para hotel_ids=%s", tarifas_endpoint, hotel_ids)
              resp = requests.get(tarifas_endpoint, params={"vigentes": "true", "hotel_ids": ",".join(hotel_ids)}, timeout=5)
              resp.raise_for_status()
              tarifas_list = resp.json() or []
              logger.info("Se obtuvieron %d tarifas desde %s", len(tarifas_list), tarifas_endpoint)
              tarifa_map = {}
              for t in tarifas_list:
                key = (t.get('hotel_id'), (t.get('categoria_habitacion') or '').upper())
                tarifa_map[key] = t
            except Exception as e:
              logger.exception("No se pudieron obtener tarifas: %s", str(e))
              tarifa_map = {}

            # Aplicamos tarifas a las habitaciones disponibles cuando exista una tarifa válida
            applied_count = 0
            for hab in hospedajes_habitaciones_disponibles:
              hotel_id = hab.get('hospedaje_id') or hab.get('hospedajeId') or hab.get('hospedaje_id')
              categoria = (hab.get('categoria') or '').upper().strip()
              if not categoria:
                logger.debug("Habitacion %s sin categoria, se mantiene precio original", hab.get('habitacion_id'))
                continue
              tarifa = tarifa_map.get((hotel_id, categoria))
              if tarifa:
                # Validar moneda: sólo aplicar tarifa si la moneda de búsqueda coincide
                tarifa_moneda = (tarifa.get('moneda') or '').upper().strip()
                if currency_code and tarifa_moneda and currency_code.upper().strip() != tarifa_moneda:
                  logger.debug(
                    "No se aplica tarifa para hotel_id=%s categoria=%s porque la moneda de búsqueda '%s' no coincide con la tarifa '%s'",
                    hotel_id,
                    categoria,
                    currency_code,
                    tarifa_moneda,
                  )
                  continue
                # Reemplazamos precio por la tarifa final si existe
                valor_final = tarifa.get('valor_final') or tarifa.get('valor_noche') or tarifa.get('valor_base')
                if valor_final is not None:
                  hab['precio'] = valor_final
                hab['tarifa_aplicada'] = tarifa.get('id')
                hab['descuentos_activos'] = tarifa.get('descuentos_activos', [])
                applied_count += 1
              else:
                logger.debug("No se encontró tarifa para hotel_id=%s categoria=%s", hotel_id, categoria)
            logger.info("Se aplicaron %d tarifas a las habitaciones disponibles", applied_count)

            #Guardamos en cache
            CacheHelper.guardarCache(
              redis_client,
              cache_key,
              hospedajes_habitaciones_disponibles,
              ttl=120
            )

            return hospedajes_habitaciones_disponibles, 200

          return disponibles, 200
        except APIError as e:
          return {'msg': e.message}, e.status_code
        except Exception as e:
          return {'msg': 'Error al procesar la búsqueda', 'error': str(e)}, 500