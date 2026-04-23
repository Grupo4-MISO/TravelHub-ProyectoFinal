from app.errors.exceptions import ExternalServiceError, DatababaseError
from app.utils.helper import ReservaHelper
import boto3

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
            # #Sacamos el body del mensaje
            # body = ReservaHelper.loadJSON(message['Body'])

            # #Actualizamos transaccion en base de datos
            # transaction_data = {
            #     'transaction_id': body.get('transaction_id'),
            #     'data': {
            #         'status': TransactionStatus[body.get('status')]
            #     }
            # }
            #TODO: crear el objeto transaccion payment (modelo de datos)
            #TODO: actualizar el status de payment (modelo de datos)
            # response = payment_transaction_crud.update_payment_transaction(transaction_data.get('transaction_id'), transaction_data.get('data'))
            response = True
            if not response:
                raise DatababaseError('Error updating payment transaction in database')

        except Exception as e:
            raise ExternalServiceError(f'Error processing message: {str(e)}')

    def deleteMessage(self, receipt_handle):
        try:
            #Borramos el mensaje de la cola
            self.sqs_client.delete_message(
                QueueUrl = self.reservas_queue_url,
                ReceiptHandle = receipt_handle
            )
        except Exception as e:
            raise ExternalServiceError(f'Error deleting message from SQS: {str(e)}')