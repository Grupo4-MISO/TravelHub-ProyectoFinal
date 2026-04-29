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
            return json.loads(message['Body'])
        
        except Exception as e:
            raise InternalServerError(f'Error loading JSON from message: {str(e)}')
    
    @staticmethod
    def normalizeUUID(id: str):
        return uuid.UUID(str(id))
        

    
        
