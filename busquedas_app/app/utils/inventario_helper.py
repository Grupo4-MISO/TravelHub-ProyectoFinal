import requests

class InventarioHelper:
    @staticmethod
    def getInventario(inventario_url, ciudad, capacidad):
        #Definimos los parametros de consulta
        params = {
            "ciudad": ciudad,
            "capacidad": capacidad
        }

        try:
            #Hacemos la consulta al microservicio de inventario
            response = requests.get(inventario_url, params = params)

            #Genera expecion si el status code es diferente a 200
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            return str(e)