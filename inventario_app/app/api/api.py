from app.services.inventario_crud import InventarioCRUD, CountriesCRUD
from app.utils.helper import InventarioHelper
from app.utils.seedHelper import SeedHelper
from app.errors.exceptions import BadRequestError, DatababaseError
from flask_restful import Resource
from flask import request
from flasgger import swag_from

# Inicializamos el CRUD
inventario_CRUD = InventarioCRUD()
countries_CRUD = CountriesCRUD()

POPULAR_CITIES_BY_COUNTRY = {
        "CO": ["Cartagena", "Bogotá", "Medellín", "Cali", "Santa Marta", "San Andrés", "Eje Cafetero", "Villa de Leyva"],
        "PE": ["Lima", "Cusco", "Arequipa", "Puno", "Trujillo", "Máncora", "Paracas", "Iquitos"],
        "EC": ["Quito", "Guayaquil", "Cuenca", "Galápagos", "Montañita", "Baños", "Manta", "Otavalo"],
        "MX": ["Ciudad de México", "Cancún", "Playa del Carmen", "Guadalajara", "Puerto Vallarta", "Oaxaca", "Tulum", "Los Cabos"],
        "CL": ["Santiago", "Valparaíso", "Viña del Mar", "Puerto Varas", "San Pedro de Atacama", "Punta Arenas", "La Serena", "Concepción"],
        "AR": ["Buenos Aires", "Mendoza", "Bariloche", "Córdoba", "Salta", "Puerto Madryn", "Ushuaia", "Mar del Plata"],
}

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

                cities = POPULAR_CITIES_BY_COUNTRY.get(country_code)
                if cities is None:
                        return {
                                'msg': f'No hay ciudades configuradas para el código de país {country_code}'
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

                ciudad = InventarioHelper.validacionCampoCiudad(ciudad)
                capacidad = InventarioHelper.validacionCampoCapacidad(capacidad)

                response = inventario_CRUD.habitacionesDisponibles(ciudad, capacidad)

                return response, 200

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
                                        'required': ['nombre', 'countryCode', 'pais', 'ciudad', 'direccion', 'rating', 'reviews'],
                                        'properties': {
                                                'nombre': {'type': 'string', 'example': 'Hotel Andino'},
                                                'countryCode': {'type': 'string', 'example': 'CO'},
                                                'pais': {'type': 'string', 'example': 'Colombia'},
                                                'ciudad': {'type': 'string', 'example': 'Bogotá'},
                                                'direccion': {'type': 'string', 'example': 'Calle 123 #45-67'},
                                                'rating': {'type': 'number', 'format': 'float', 'example': 4.5},
                                                'reviews': {'type': 'integer', 'example': 120},
                                        }
                                }
                        }
                ],
                'responses': {
                        201: {'description': 'Hospedaje creado exitosamente'},
                        400: {'description': 'Datos inválidos'},
                        500: {'description': 'Error en la base de datos'}
                }
        })
        def post(self):
                """Crear un hospedaje."""
                payload = request.get_json() or {}

                required_fields = ['nombre', 'countryCode', 'pais', 'ciudad', 'direccion', 'rating', 'reviews']
                missing_fields = [field for field in required_fields if payload.get(field) in [None, '']]
                if missing_fields:
                        raise BadRequestError(f"Faltan campos requeridos: {', '.join(missing_fields)}")

                try:
                        rating = float(payload.get('rating'))
                        reviews = int(payload.get('reviews'))
                except (TypeError, ValueError):
                        raise BadRequestError('Los campos rating y reviews deben ser numéricos válidos')

                if rating < 0 or rating > 5:
                        raise BadRequestError('El campo rating debe estar entre 0 y 5')

                if reviews < 0:
                        raise BadRequestError('El campo reviews debe ser un número entero mayor o igual a 0')

                payload['countryCode'] = str(payload.get('countryCode')).upper().strip()
                payload['rating'] = rating
                payload['reviews'] = reviews

                created = inventario_CRUD.crear_hospedaje(payload)

                if isinstance(created, DatababaseError):
                        return {'msg': created.message}, 500

                return created, 201

