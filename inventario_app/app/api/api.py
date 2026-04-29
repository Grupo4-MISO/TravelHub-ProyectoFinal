from app.services.inventario_crud import InventarioCRUD, CountriesCRUD
from app.utils.helper import InventarioHelper
from app.utils.seedHelper import SeedHelper
from app.errors.exceptions import BadRequestError, DatababaseError
from flask_restful import Resource
from flask import request
from flasgger import swag_from
import uuid

# Inicializamos el CRUD
inventario_CRUD = InventarioCRUD()
countries_CRUD = CountriesCRUD()

class CountryList(Resource):
        @swag_from({
                'tags': ['Countries'],
                'responses': {
                        200: {
                                'description': 'Lista de países',
                                'schema': {
                                        'type': 'array',
                                        'items': {
                                                'type': 'object',
                                                'properties': {
                                                        'id': {'type': 'string', 'example': '123e4567-e89b-12d3-a456-426614174000'},
                                                        'name': {'type': 'string', 'example': 'Argentina'},
                                                        'code': {'type': 'string', 'example': 'AR'},
                                                        'CurrencyCode': {'type': 'string', 'example': 'ARS'},
                                                        'CurrencySymbol': {'type': 'string', 'example': '$'},
                                                        'FlagEmoji': {'type': 'string', 'example': '🇦🇷'},
                                                        'PhoneCode': {'type': 'string', 'example': '+54'},
                                                }
                                        }
                                }
                        }
                }
        })
        def get(self):
                """Obtener lista de países."""
                countries = countries_CRUD.obtener_paises()
                return countries, 200

class PopularCitiesByCountry(Resource):
        @swag_from({
                'tags': ['Countries'],
                'parameters': [
                        {
                                'name': 'code',
                                'in': 'path',
                                'type': 'string',
                                'required': True,
                                'description': 'Código del país (ejemplo: CO, PE, EC, MX, CL, AR)',
                        },
                ],
                'responses': {
                        200: {
                                'description': 'Ciudades populares del país consultado',
                                'schema': {
                                        'type': 'array',
                                        'items': {'type': 'string'},
                                        'example': ['Cartagena', 'Bogotá', 'Medellín', 'Cali', 'Santa Marta', 'San Andrés', 'Eje Cafetero', 'Villa de Leyva']
                                }
                        },
                        400: {
                                'description': 'Código inválido o no configurado',
                        }
                }
        })
        def get(self, code):
                """Obtener ciudades populares de un país por su código."""
                country_code = (code or '').upper().strip()

                if not country_code:
                        return {'msg': 'El parámetro code es requerido en la URL'}, 400

                cities = countries_CRUD.obtener_ciudades_por_codigo(country_code)

                if isinstance(cities, DatababaseError):
                        return {'msg': cities.message}, 500

                if not cities:
                        return {
                                'msg': f'No hay ciudades registradas para el código de país {country_code}'
                        }, 400

                return cities, 200
        
class InventarioHealth(Resource):
        @swag_from({
                'tags': ['Health'],
                'responses': {
                        200: {
                                'description': 'Servicio operativo',
                                'schema': {
                                        'type': 'object',
                                        'properties': {
                                                'status': {'type': 'string', 'example': 'healthy'}
                                        }
                                }
                        }
                }
        })
        def get(self):
                """Health check del servicio de inventario."""
                return {'status': 'healthy'}, 200

class FiltroHabitaciones(Resource):
        @swag_from({
                'tags': ['Inventario'],
                'parameters': [
                        {
                                'name': 'ciudad',
                                'in': 'query',
                                'type': 'string',
                                'required': False,
                                'description': 'Ciudad a consultar',
                        },
                        {
                                'name': 'capacidad',
                                'in': 'query',
                                'type': 'integer',
                                'required': False,
                                'description': 'Capacidad mínima requerida',
                        },
                        {
                                'name': 'currency_code',
                                'in': 'query',
                                'type': 'string',
                                'required': False,
                                'description': 'Código de moneda para obtener tarifas (ejemplo: USD, COP, EUR)',
                        }
                ],
                'responses': {
                        200: {'description': 'Resultado de la búsqueda'},
                        400: {'description': 'Parámetros inválidos'}
                }
        })
        def get(self):
                """Obtener habitaciones disponibles por ciudad y capacidad."""
                ciudad = request.args.get('ciudad')
                capacidad = request.args.get('capacidad')
                currency_code = request.args.get('currency_code')

                ciudad = InventarioHelper.validacionCampoCiudad(ciudad)
                capacidad = InventarioHelper.validacionCampoCapacidad(capacidad)

                response = inventario_CRUD.habitacionesDisponibles(ciudad, capacidad, currency_code)

                return response, 200
    
class ListadoCiudades(Resource):
    def get(self):
        #Traemos el listado de ciudades disponibles en el inventario
        ciudades = inventario_CRUD.listadoCiudades()

        return ciudades, 200

class ListadoPaises(Resource):
    def get(self):
        #Traemos el listado de paises disponibles en el inventario
        paises = inventario_CRUD.listadoPaises()

        return paises, 200

class CleanDB(Resource):
       def post(self):
              inventario_CRUD.resetDb()
              return {'msg': 'Base de datos limpiada exitosamente'}, 200


class HabitacionesporId(Resource):
    #Retorna los datos de una habitación a partir del id del hotel, para el dashboard del hotel
    def get(self):
        id_hotel = request.args.get('id')

        habitaciones = inventario_CRUD.habitacionesporIdHotel(id_hotel)
        if habitaciones is None:
            response = []
        else:
            response = [
                {
                    'habitacion_id': str(habitacion.id),
                    'precio': habitacion.precio,
                    'capacidad': habitacion.capacidad,
                    'descripcion': habitacion.descripcion
                }
                for habitacion in habitaciones
            ]
        return response, 200
    
class ListadoHoteles(Resource):
        #Recibe un listado de habitaciones y retorna un listado de hoteles (a los cuales
        #pertencen dichas habitaciones), para el dashboard del viajero.
        def post(self):
                data = request.get_json()
                habitaciones_ids = data.get('habitaciones_ids', [])
                hoteles = inventario_CRUD.hotelesPorHabitaciones(habitaciones_ids)
                return hoteles, 200
        
class SeedDB(Resource):
        @swag_from({
                'tags': ['Seed'],
                'responses': {
                        200: {
                                'description': 'Seed ejecutado correctamente',
                                'schema': {
                                        'type': 'object',
                                        'properties': {
                                                'msg': {'type': 'string', 'example': 'Seed ejecutado correctamente'},
                                                'countries_insertados': {'type': 'integer', 'example': 6},
                                                'hospedajes_insertados': {'type': 'integer', 'example': 63},
                                                'habitaciones_insertadas': {'type': 'integer', 'example': 189},
                                        }
                                }
                        },
                        500: {
                                'description': 'Error al ejecutar el seed',
                                'schema': {
                                        'type': 'object',
                                        'properties': {
                                                'msg': {'type': 'string', 'example': 'Error al ejecutar el seed'},
                                                'error': {'type': 'string'}
                                        }
                                }
                        }
                }
        })
        def post(self):
                """Ejecutar seed de inventario."""
                result = SeedHelper.reset_and_seed()

                if not result.get('ok'):
                        return {'msg': 'Error al ejecutar el seed', 'error': result.get('error')}, 500

                return {
                        'msg': 'Seed ejecutado correctamente',
                        'countries_insertados': result['countries_insertados'],
                        'hospedajes_insertados': result['hospedajes_insertados'],
                        'habitaciones_insertadas': result['habitaciones_insertadas'],
                }, 200

class HospedajeCollection(Resource):
        @swag_from({
                'tags': ['Hospedajes'],
                'parameters': [
                        {
                                'in': 'body',
                                'name': 'body',
                                'required': True,
                                'schema': {
                                        'type': 'object',
                                        'required': ['providerId', 'nombre', 'descripcion', 'countryCode', 'pais', 'ciudad', 'direccion', 'latitude', 'longitude', 'rating', 'reviews'],
                                        'properties': {
                                                'providerId': {'type': 'string', 'format': 'uuid', 'example': '123e4567-e89b-12d3-a456-426614174000'},
                                                'nombre': {'type': 'string', 'example': 'Hotel Andino'},
                                                'descripcion': {'type': 'string', 'example': 'Hotel céntrico con diseño moderno y excelente conectividad.'},
                                                'countryCode': {'type': 'string', 'example': 'CO'},
                                                'pais': {'type': 'string', 'example': 'Colombia'},
                                                'ciudad': {'type': 'string', 'example': 'Bogotá'},
                                                'direccion': {'type': 'string', 'example': 'Calle 123 #45-67'},
                                                'latitude': {'type': 'number', 'format': 'float', 'example': 4.7110},
                                                'longitude': {'type': 'number', 'format': 'float', 'example': -74.0721},
                                                'rating': {'type': 'number', 'format': 'float', 'example': 4.5},
                                                'reviews': {'type': 'integer', 'example': 120},
                                        }
                                }
                        }
                ],
                'responses': {
                        200: {
                                'description': 'Listado de hospedajes con providerId',
                                'schema': {
                                        'type': 'array',
                                        'items': {
                                                'type': 'object',
                                                'properties': {
                                                        'id': {'type': 'string', 'format': 'uuid'},
                                                        'providerId': {'type': 'string', 'format': 'uuid'},
                                                        'nombre': {'type': 'string'},
                                                        'countryCode': {'type': 'string'},
                                                        'ciudad': {'type': 'string'},
                                                }
                                        }
                                }
                        },
                        201: {
                                'description': 'Hospedaje creado exitosamente con providerId',
                                'schema': {
                                        'type': 'object',
                                        'properties': {
                                                'id': {'type': 'string', 'format': 'uuid'},
                                                'providerId': {'type': 'string', 'format': 'uuid'},
                                                'nombre': {'type': 'string'},
                                                'countryCode': {'type': 'string'},
                                                'ciudad': {'type': 'string'},
                                        }
                                }
                        },
                        400: {'description': 'Datos inválidos'},
                        500: {'description': 'Error en la base de datos'}
                }
        })
        def get(self):
                """Listar hospedajes, opcionalmente filtrados por país y ciudad."""
                country_code = (request.args.get('countryCode') or '').upper().strip()
                ciudad = (request.args.get('ciudad') or '').strip()

                hospedajes = inventario_CRUD.obtener_hospedajes(
                        country_code=country_code or None,
                        ciudad=ciudad or None,
                )

                if isinstance(hospedajes, DatababaseError):
                        return {'msg': hospedajes.message}, 500

                return hospedajes, 200

        def post(self):
                """Crear un hospedaje."""
                payload = request.get_json() or {}

                required_fields = ['providerId', 'nombre', 'descripcion', 'countryCode', 'pais', 'ciudad', 'direccion', 'latitude', 'longitude', 'rating', 'reviews']
                missing_fields = [field for field in required_fields if payload.get(field) in [None, '']]
                if missing_fields:
                        raise BadRequestError(f"Faltan campos requeridos: {', '.join(missing_fields)}")

                try:
                        payload['providerId'] = str(uuid.UUID(str(payload.get('providerId'))))
                except (ValueError, TypeError):
                        raise BadRequestError('El campo providerId debe tener formato UUID válido')

                try:
                        latitude = float(payload.get('latitude'))
                        longitude = float(payload.get('longitude'))
                        rating = float(payload.get('rating'))
                        reviews = int(payload.get('reviews'))
                except (TypeError, ValueError):
                        raise BadRequestError('Los campos latitude, longitude, rating y reviews deben ser numéricos válidos')

                if latitude < -90 or latitude > 90:
                        raise BadRequestError('El campo latitude debe estar entre -90 y 90')

                if longitude < -180 or longitude > 180:
                        raise BadRequestError('El campo longitude debe estar entre -180 y 180')

                if rating < 0 or rating > 5:
                        raise BadRequestError('El campo rating debe estar entre 0 y 5')

                if reviews < 0:
                        raise BadRequestError('El campo reviews debe ser un número entero mayor o igual a 0')

                payload['countryCode'] = str(payload.get('countryCode')).upper().strip()
                payload['latitude'] = latitude
                payload['longitude'] = longitude
                payload['rating'] = rating
                payload['reviews'] = reviews

                created = inventario_CRUD.crear_hospedaje(payload)

                if isinstance(created, DatababaseError):
                        return {'msg': created.message}, 500

                return created, 201

class HospedajeById(Resource):
        @swag_from({
                'tags': ['Hospedajes'],
                'parameters': [
                        {
                                'name': 'hospedaje_id',
                                'in': 'path',
                                'type': 'string',
                                'required': True,
                                'description': 'Id UUID del hospedaje',
                        },
                        {
                                'name': 'currency_code',
                                'in': 'path',
                                'type': 'string',
                                'required': True,
                                'description': 'Código de moneda del destino',
                        }
                ],
                'responses': {
                        200: {
                                'description': 'Hospedaje consultado exitosamente',
                                'schema': {
                                        'type': 'object',
                                        'properties': {
                                                'id': {'type': 'string', 'format': 'uuid'},
                                                'providerId': {'type': 'string', 'format': 'uuid'},
                                                'nombre': {'type': 'string'},
                                                'countryCode': {'type': 'string'},
                                                'habitaciones': {'type': 'array'},
                                        }
                                }
                        },
                        400: {'description': 'Id inválido'},
                        404: {'description': 'Hospedaje no encontrado'},
                        500: {'description': 'Error en la base de datos'}
                }
        })
        def get(self, hospedaje_id, currency_code):
                """Obtener un hospedaje por su id."""
                hospedaje = inventario_CRUD.obtener_hospedaje_por_id(hospedaje_id, currency_code)

                if isinstance(hospedaje, DatababaseError):
                        message = (hospedaje.message or '').lower()
                        if 'uuid' in message:
                                return {'msg': hospedaje.message}, 400
                        return {'msg': hospedaje.message}, 500

                if hospedaje is None:
                        return {'msg': f'Hospedaje no encontrado para id {hospedaje_id}'}, 404

                return hospedaje, 200

class HospedajeInfo(Resource):
       def get(self, habitacion_id, currency_code):
                #Traemos la información de la habitación a partir del id
                habitacion = inventario_CRUD.habitacionPorId(habitacion_id)

                #Validamos que la habitación exista
                if not habitacion:
                        return {'msg': f'No se encontró una habitación para el id {habitacion_id}'}, 404

                #Traemos la información del hospedaje al que pertenece la habitación
                hospedaje = inventario_CRUD.obtener_hospedaje_por_id(habitacion.propiedad_id, currency_code)

                #Validamos que el hospedaje exista
                if not hospedaje:
                        return {'msg': f'No se encontró el hospedaje para la habitación con id {habitacion_id}'}, 404

                #Filtramos informacion del hospedaje
                hospedaje_info = {
                       'nombre': hospedaje.get('nombre'),
                       'direccion': hospedaje.get('direccion'),
                       'ciudad': hospedaje.get('ciudad'),
                       'pais': hospedaje.get('pais'),
                       'amenidades': hospedaje.get('amenidades'),
                       'imagenes': hospedaje.get('imagenes'),
                }

                return hospedaje_info, 200

class SeedReservations(Resource):
    #Proporciona un listado de Id's para seeding de reservas.
    def get(self):
        result = SeedHelper.seed_reservations()
        return result, 200
