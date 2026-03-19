from app.errors.exceptions import ExternalServiceError
import requests
import os

#Importamos ruta del endpoint
ENDPOINT_RESERVA = os.getenv('ENDPOINT_RESERVA')

class ReservaHelper:
    @staticmethod
    def disponibilidadReserva(reserva_url, habitacion_ids, check_in, check_out):
        #Payload para la consulta
        payload = {
            'habitacion_ids': habitacion_ids,
            'check_in': check_in,
            'check_out': check_out,
        }

        try:
            #Hacemos la consulta al microservicio de reservas
            response = requests.post(f"{reserva_url}{ENDPOINT_RESERVA}", json = payload)

            #Genera expecion si el status code es diferente a 200
            response.raise_for_status()

            return response.json()
        
        except requests.exceptions.RequestException as e:
            return ExternalServiceError(f"Error al consultar el microservicio de reservas: {str(e)}")