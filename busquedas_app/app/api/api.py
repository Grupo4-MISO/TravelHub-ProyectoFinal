from app.utils.inventario_helper import InventarioHelper
from app.utils.reserva_helper import ReservaHelper
from flask_restful import Resource
from flask import request
import os

#Traemos las variables de entorno para las URLs de los microservicios
INVENTARIOS_URL = os.getenv('INVENTARIOS_URL')
RESERVAS_URL = os.getenv('RESERVAS_URL')

class SearchHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class Search(Resource):
    def get(self):
        #Extraemos parametros de busqueda
        ciudad = request.args.get('ciudad')
        capacidad = request.args.get('capacidad')
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')

        #Consulta al microservicio de inventario
        habitaciones = InventarioHelper.getInventario(INVENTARIOS_URL, ciudad, capacidad)

        #Validamos que la respuesta no sea error
        if isinstance(habitaciones, str):
            return {'msg': 'Error al buscar habitaciones', 'error': habitaciones}, 500

        #Construimos los ids de habitaciones
        habitaciones_ids = [habitacion.get('id') for habitacion in habitaciones]

        #Consulta al microservicio de reservas
        disponibilidad = ReservaHelper.disponibilidadReserva(RESERVAS_URL, habitaciones_ids, check_in, check_out)

        #Validamos que la respuesta no sea error
        if isinstance(disponibilidad, str):
            return {'msg': 'Error al verificar disponibilidad', 'error': disponibilidad}, 500

        #Filtramos habitaciones disponibles
        disponibles = list()

        for habitacion in habitaciones:
            #Extraemos habitacion_id
            habitacion_id = str(habitacion.get('id'))

            #Validamos disponibilidad
            if disponibilidad.get(habitacion_id) is True:
                disponibles.append(habitacion)
        
        return disponibles, 200