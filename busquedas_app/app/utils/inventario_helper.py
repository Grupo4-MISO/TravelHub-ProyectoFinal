from app.errors.exceptions import ExternalServiceError
import requests
import os

#Importamos ruta del endpoint
ENDPOINT_INVENTARIO = os.getenv('ENDPOINT_INVENTARIO')

class InventarioHelper:
    @staticmethod
    def getInventario(inventario_url, ciudad, capacidad, currency_code):
        #Definimos los parametros de consulta
        params = {
            "ciudad": ciudad,
            "capacidad": capacidad,
            "currency_code": currency_code
        }

        try:
            #Hacemos la consulta al microservicio de inventario
            response = requests.get(f"{inventario_url}{ENDPOINT_INVENTARIO}", params = params)

            #Genera expecion si el status code es diferente a 200
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Error al consultar el microservicio de inventario: {str(e)}")
        
    @staticmethod
    def seed_reservas_ids(inventario_url):
        try:
            response = requests.get(f"{inventario_url}/api/v1/inventarios/seed-reservas")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Error al ejecutar el seed de reservas: {str(e)}")
        