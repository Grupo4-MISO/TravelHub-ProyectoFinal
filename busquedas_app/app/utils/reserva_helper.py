from app.errors.exceptions import ExternalServiceError
import requests
import os

#Importamos ruta del endpoint
ENDPOINT_RESERVA = os.getenv('ENDPOINT_RESERVA', '/api/v1/reservas/disponibilidad')


def _build_service_url(base_url, endpoint):
    if not base_url:
        raise ExternalServiceError('La variable RESERVAS_URL no esta configurada')

    if not endpoint:
        raise ExternalServiceError('La variable ENDPOINT_RESERVA no esta configurada')

    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

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
            reservas_service_url = _build_service_url(reserva_url, ENDPOINT_RESERVA)
            response = requests.post(reservas_service_url, json = payload)

            #Genera expecion si el status code es diferente a 200
            response.raise_for_status()

            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Error al consultar el microservicio de reservas: {str(e)}")
        
    @staticmethod
    def seedReservas(reservas_url, cantidad, payload):
        try:
            response = requests.post(f"{reservas_url}/api/v1/reservas/seed/{cantidad}", json = payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Error al ejecutar el seed en el microservicio de reservas: {str(e)}")