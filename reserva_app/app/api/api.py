from app.services.reserva_crud import ReservaCRUD
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

