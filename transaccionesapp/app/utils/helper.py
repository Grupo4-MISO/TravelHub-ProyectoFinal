from app.errors.exceptions import ExternalServiceError, InternalServerError
import json

class Helper:
    @staticmethod
    def loadJSON(message):
        try:
            return json.loads(message['Body'])
        
        except Exception as e:
            raise InternalServerError(f'Error loading JSON from message: {str(e)}')

    def reservasMessage(message):
        try:
            #Cargamos el body del mensaje original
            body = Helper.loadJSON(message['Body'])

            #Creamos el nuevo mensaje para la cola de reservas
            reservas_message = {
                'reserva_id': body.get('reserva_id'),
                'status': body.get('status'),
            }

            return reservas_message

        except Exception as e:
            raise InternalServerError(f'Error creating reservas message: {str(e)}')
