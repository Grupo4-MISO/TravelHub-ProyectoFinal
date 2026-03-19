from app.services.inventario_crud import InventarioCRUD
from app.errors.exceptions import BadRequestError
from app.utils.helper import InventarioHelper
from app.utils.seedHelper import SeedHelper
from flask_restful import Resource
from flask import request

#Inicializamos el CRUD
inventario_CRUD = InventarioCRUD()

class InventarioHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class FiltroHabitaciones(Resource):
    def get(self):
        #Traemos los parametros de busqueda
        ciudad = request.args.get('ciudad')
        capacidad = request.args.get('capacidad')

        #Validamos los parametros de busqueda
        respuesta_validad_ciudad = InventarioHelper.validacionCampoCiudad(ciudad)
        if not respuesta_validad_ciudad:
            raise BadRequestError(respuesta_validad_ciudad)
        
        respuesta_validad_capacidad = InventarioHelper.validacionCampoCapacidad(capacidad)
        if not respuesta_validad_capacidad:
            raise BadRequestError(respuesta_validad_capacidad)

        #Traemos las habitaciones disponibles segun los parametros de busqueda
        response = inventario_CRUD.habitacionesDisponibles(ciudad, capacidad)

        return response, 200

class SeedDB(Resource):
    def post(self):
        result = SeedHelper.reset_and_seed()

        if not result.get('ok'):
            return {'msg': 'Error al ejecutar el seed', 'error': result.get('error')}, 500

        return {
            'msg': 'Seed ejecutado correctamente',
            'hospedajes_insertados': result['hospedajes_insertados'],
            'habitaciones_insertadas': result['habitaciones_insertadas'],
        }, 200

