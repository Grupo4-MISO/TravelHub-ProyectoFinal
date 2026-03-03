from app.services.inventario_crud import InventarioCRUD
from app.utils.seedHelper import SeedHelper
from flask import request, jsonify
from flask_restful import Resource

#Inicializamos el CRUD
inventario_CRUD = InventarioCRUD()

class InventarioHealth(Resource):
    def get(self):
        return jsonify({'status': 'healthy'}), 200

class FiltroHabitaciones(Resource):
    def get(self):
        #Traemos los parametros de busqueda
        ciudad = request.args.get('ciudad')
        capacidad = request.args.get('capacidad')

        #Traemos las habitaciones disponibles segun los parametros de busqueda
        response = inventario_CRUD.habitacionesDisponibles(ciudad, capacidad)

        #Validamos que la respuesta no sea error
        if isinstance(response, str):
            return jsonify({'msg': 'Error al buscar habitaciones', 'error': response}), 500

        return jsonify(response), 200


class SeedDB(Resource):
    def post(self):
        result = SeedHelper.reset_and_seed()

        if not result.get('ok'):
            return jsonify({'msg': 'Error al ejecutar el seed', 'error': result.get('error')}), 500

        return jsonify({
            'msg': 'Seed ejecutado correctamente',
            'hospedajes_insertados': result['hospedajes_insertados'],
            'habitaciones_insertadas': result['habitaciones_insertadas'],
        }), 200

