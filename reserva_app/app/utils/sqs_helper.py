from app.errors.exceptions import InternalServerError, ExternalServiceError
from app.services.reserva_crud import ReservaCRUD
import boto3

#Creamos instancia de ReservaCRUD
reserva_crud = ReservaCRUD()

class SQSHelper:
    def __init__(self, reservas_sqs_url: str):
        #Creamos cliente de SQS
        self.sqs_client = boto3.client('sqs', region_name = 'us-east-1')

        #Guardamos la URL de la cola
        self.reservas_queue_url = reservas_sqs_url

    def readMessages(self):
        try:
            #Leemos la cola sqs de pagos
            messages = self.sqs_client.receive_message(
                QueueUrl = self.reservas_queue_url,
                MaxNumberOfMessages = 10,
                WaitTimeSeconds = 20).get("Messages", [])
            
            if not messages:
                return []

            return messages

        except Exception as e:
            raise ExternalServiceError(f'Error reading messages from SQS: {str(e)}')
    
    def processMessage(self, message):
        try:
            #Cambiamos el estado de la reserva
            reserva_crud.cambiarEstadoReserva(message)

        except Exception as e:
            raise InternalServerError(f'Error processing message: {str(e)}')

    def deleteMessage(self, receipt_handle):
        try:
            #Borramos el mensaje de la cola
            self.sqs_client.delete_message(
                QueueUrl = self.reservas_queue_url,
                ReceiptHandle = receipt_handle
            )
        except Exception as e:
            raise ExternalServiceError(f'Error deleting message from SQS: {str(e)}')