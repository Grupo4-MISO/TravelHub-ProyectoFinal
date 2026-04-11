from app.services.inventario_crud import InventarioCRUD
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
        ciudad = InventarioHelper.validacionCampoCiudad(ciudad)
        
        capacidad = InventarioHelper.validacionCampoCapacidad(capacidad)

        #Traemos las habitaciones disponibles segun los parametros de busqueda
        response = inventario_CRUD.habitacionesDisponibles(ciudad, capacidad)

        return response, 200
    

class buscarHotel(Resource):
    #Endpoint para identificar un hotel en inventario(por ahora busca por nombre) 
    def get(self):
        nombre_hotel = request.args.get('nombre')
        hotel = inventario_CRUD.buscarHotel(nombre_hotel)
        if hotel is None:
            return {'msg': 'Hotel no encontrado'}, 404
        
        response = {
            'id': str(hotel.id),
            'nombre': hotel.nombre,
            'pais': hotel.pais,
            'ciudad': hotel.ciudad,
            'direccion': hotel.direccion,
            'rating': hotel.rating
        }
        return response, 200

class HabitacionesporId(Resource):
    #Retorna los datos de una habitación a partir de su id, para el dashboard
    def get(self):
        id_hotel = request.args.get('id')

        habitaciones = inventario_CRUD.habitacionesporIdHotel(id_hotel)
        if habitaciones is None:
            response = []
        else:
            response = [
                {
                    'habitacion_id': str(habitacion.id),
                    'precio': habitacion.precio,
                    'capacidad': habitacion.capacidad,
                    'descripcion': habitacion.descripcion
                }
                for habitacion in habitaciones
            ]
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

class SeedReservations(Resource):
    #Proporciona un listado de Id's para seeding de reservas.
    def get(self):
        result = SeedHelper.seed_reservations()
        return result, 200
