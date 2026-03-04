from reserva_app.app.services.reserva_crud import ReservaCRUD
from app.utils.seedHelper import SeedHelper
from flask_restful import Resource
from datetime import datetime
from flask import request

#Instanciamos crud
reservas_crud = ReservaCRUD()

class ReservaHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class VerificarDisponibilidad(Resource):
    def post(self):
        #Obtenemos los datos del request
        data = request.get_json()

        #Obtenemos datos del request
        habitaciones_ids = data.get('habitacion_ids')
        check_in = datetime.strptime(data.get('check_in'), '%Y-%m-%d').date()
        check_out = datetime.strptime(data.get('check_out'), '%Y-%m-%d').date()

        #Verificamos disponibilidad
        disponibilidad = reservas_crud.verificarDisponibilidad(habitaciones_ids, check_in, check_out)

        #Validamos si hubo un error en la consulta
        if isinstance(disponibilidad, str):
            return {'msg': 'Error al verificar disponibilidad', 'error': disponibilidad}, 500
        
        #TODO: Mandamos habitaciones ids disponibles a cache
    
        return disponibilidad, 200

class VerificarCache(Resource):
    def get(self):
        #TODO: Implementar endpoint para verificar cache de disponibilidad
        pass

class SeedReservas(Resource):
    def post(self, cantidad):
        if cantidad <= 0:
            return {'msg': 'La cantidad debe ser un entero positivo'}, 400

        result = SeedHelper.reset_and_seed(cantidad)

        if not result.get('ok'):
            return {'msg': 'Error al ejecutar el seed', 'error': result.get('error')}, 500

        response = {
            'msg': 'Seed ejecutado correctamente',
            'solicitadas': result['solicitadas'],
            'reservas_insertadas': result['reservas_insertadas'],
        }

        if 'advertencia' in result:
            response['advertencia'] = result['advertencia']

        return response, 200

