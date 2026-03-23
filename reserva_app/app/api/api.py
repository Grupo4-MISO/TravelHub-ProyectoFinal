from app.services.reserva_crud import ReservaCRUD
from app.utils.seedHelper import SeedHelper
from app.utils.helper import ReservaHelper
from flask_restful import Resource
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

        #Validamos campos de fechas
        check_in, check_out = ReservaHelper.validacionCampoFechas(data.get('check_in'), data.get('check_out'))

        #Obtenemos datos del request de ids
        habitaciones_ids = data.get('habitacion_ids')

        #Verificamos disponibilidad
        disponibilidad = reservas_crud.verificarDisponibilidad(habitaciones_ids, check_in, check_out)
    
        return disponibilidad, 200

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

