from app.services.inventario_crud import InventarioCRUD
from flask_restful import Resource
from flask import request

#Creamos instancia del CRUD
inventario_crud = InventarioCRUD()

class InventarioHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class HospedajeSearchResource(Resource):
    def get(self, ciudad, capacidad):
        #Creamos diccionario con parametros de busqueda
        busqueda_params = {
            'ciudad': ciudad,
            'capacidad': capacidad
        }

        #Traemos los hospedajes que cumplen con los parametros de busqueda
        hospedajes = inventario_crud.hospedajesCiudadCapacidadDB(busqueda_params)

        #Validamos si hubo un error en la consulta
        if isinstance(hospedajes, str):
            return {'msg': 'Error al buscar hospedajes', 'error': hospedajes}, 500
        
        return hospedajes, 200

