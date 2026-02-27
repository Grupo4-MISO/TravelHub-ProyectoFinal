from reserva_app.app.services.reserva_crud import ReservaCRUD
from flask_restful import Resource
from flask import request

#Creamos instancia del CRUD
reserva_crud = ReservaCRUD()

class ReservaHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class ReservaSearchResource(Resource):
    def get(self, fecha_inicio, fecha_fin, habitaciones):
        #Obtenemos las reservas disponibles para las fechas y habitaciones dadas
        reservas_disponibles = reserva_crud.habitacionesReservasDisponiblesDB(fecha_inicio, fecha_fin, habitaciones)

        if isinstance(reservas_disponibles, str):
            return {'msg': 'Error al buscar reservas disponibles', 'error': reservas_disponibles}, 500
        
        return reservas_disponibles, 200

