from app.errors.exceptions import ExternalServiceError
import requests
import os

#Importamos ruta del endpoint
ENDPOINT_INVENTARIO = os.getenv('ENDPOINT_INVENTARIO', '/api/v1/inventarios/filtro-economico')

def _build_service_url(base_url, endpoint):
    if not base_url:
        raise ExternalServiceError('La variable INVENTARIOS_URL no esta configurada')

    if not endpoint:
        raise ExternalServiceError('La variable ENDPOINT_INVENTARIO no esta configurada')

    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

class InventarioHelper:
    @staticmethod
    def getInventario(inventario_url, ciudad, capacidad, currency_code=None):
        #Definimos los parametros de consulta
        params = {
            "ciudad": ciudad,
            "capacidad": capacidad,
        }
        if currency_code:
            params["currency_code"] = currency_code

        try:
            #Hacemos la consulta al microservicio de inventario
            inventario_service_url = _build_service_url(inventario_url, ENDPOINT_INVENTARIO)
            response = requests.get(inventario_service_url, params = params)

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
        