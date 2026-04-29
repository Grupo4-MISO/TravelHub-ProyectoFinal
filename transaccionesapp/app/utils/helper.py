from app.errors.exceptions import InternalServerError
from app.services.transactions_crud import PaymentCrud
import json
import uuid

#Declaramos payement crud
payment_crud = PaymentCrud()

class Helper:
    @staticmethod
    def loadJSON(message):
        try:
            return json.loads(json.loads(message['Body'])['body'])
        
        except Exception as e:
            raise InternalServerError(f'Error loading JSON from message: {str(e)}')
    
    @staticmethod
    def normalizeUUID(id: str):
        return uuid.UUID(str(id))

    @staticmethod
    def reservasMessage(payment, message):
        #Definimos diccionario de salida
        reservas_message = dict()

        #Agregamos id de reserva, status y email al mensaje
        reservas_message['reserva_id'] = str(payment.reserva_id)
        reservas_message['status'] = message.get('status')
        reservas_message['email'] = message.get('metadata').get('customer_email')

        return reservas_message
        

    
        
