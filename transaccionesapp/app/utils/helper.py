from app.errors.exceptions import DatababaseError, InternalServerError
from app.services.transactions_crud import PaymentCrud
import json

#Declaramos payement crud
payment_crud = PaymentCrud()

class Helper:
    @staticmethod
    def loadJSON(message):
        try:
            return json.loads(message['Body'])
        
        except Exception as e:
            raise InternalServerError(f'Error loading JSON from message: {str(e)}')

    def reservasMessage(payment_transaction):
        try:
            #Traemos la informacion de base de datos
            payment = payment_crud.get_payment_by_id(payment_transaction.payment_id)

            #Construimos el mensaje para la cola de reservas
            reservas_message = {
                'reserva_id': str(payment.reserva_id),
            }

            return reservas_message

        except Exception as e:
            raise DatababaseError(f'Error searching payment by id: {str(e)}')
        
