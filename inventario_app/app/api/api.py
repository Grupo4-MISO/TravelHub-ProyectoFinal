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
    
class ListadoCiudades(Resource):
    def get(self):
        #Traemos el listado de ciudades disponibles en el inventario
        ciudades = inventario_CRUD.listadoCiudades()

        return ciudades, 200

class ListadoPaises(Resource):
    def get(self):
        #Traemos el listado de paises disponibles en el inventario
        paises = inventario_CRUD.listadoPaises()

        return paises, 200

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

