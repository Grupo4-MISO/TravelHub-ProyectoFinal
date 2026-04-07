from app.services.inventario_crud import InventarioCRUD
from app.utils.helper import InventarioHelper
from app.utils.seedHelper import SeedHelper
from flask_restful import Resource
from flask import request
from flasgger import swag_from

# Inicializamos el CRUD
inventario_CRUD = InventarioCRUD()


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
                'tags': ['Inventario'],
                'responses': {
                        200: {
                                'description': 'Seed ejecutado correctamente',
                                'schema': {
                                        'type': 'object',
                                        'properties': {
                                                'msg': {'type': 'string', 'example': 'Seed ejecutado correctamente'},
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
                        'hospedajes_insertados': result['hospedajes_insertados'],
                        'habitaciones_insertadas': result['habitaciones_insertadas'],
                }, 200

