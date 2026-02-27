from app.services.inventario_crud import InventarioCRUD
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

