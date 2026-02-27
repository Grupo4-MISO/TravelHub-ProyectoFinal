from flask_restful import Resource
from flask import request
import requests
import os

#Traemos las variables de entorno para las URLs de los microservicios
INVENTARIOS_URL = os.getenv('INVENTARIOS_URL')
RESERVAS_URL = os.getenv('RESERVAS_URL')

class SearchHealth(Resource):
    def get(self):
        return {'status': 'healthy'}, 200

class Search(Resource):
    def get(self, ciudad, capacidad, fecha_inicio, fecha_fin):
        #Traeamos hospedajes disponibles del microservicio de inventarios
        inventarios_response = requests.get(f'{INVENTARIOS_URL}/api/v1/hospedajes/search', params = {
            'ciudad': ciudad,
            'capacidad': capacidad
        }).json()

        #Traemos las reservas del microservicio de reservas
        reservas_response = requests.get(f'{RESERVAS_URL}/api/v1/reservas/search', params = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }, json = inventarios_response).json()

        #Filtramos los hospedajes disponibles segun reservas
        hospedajes_disponibles = []