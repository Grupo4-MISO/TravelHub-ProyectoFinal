from app.errors.exceptions import ExternalServiceError, DatababaseError
from app.services.transactions_crud import PaymentTransactionCrud
from app.db.models import TransactionStatus
from app.utils.helper import Helper
import boto3
import json

#Instancia de transaction CRUD
payment_transaction_crud = PaymentTransactionCrud()

class SQSHelper:
    def __init__(self, pagos_sqs_url: str, reservas_sqs_url: str):
        #Creamos cliente de SQS
        self.sqs_client = boto3.client('sqs')

        #Guardamos la URL de la cola
        self.pagos_queue_url = pagos_sqs_url
        self.reservas_queue_url = reservas_sqs_url

    def readMessages(self):
        try:
            #Leemos la cola sqs de pagos
            messages = self.sqs_client.receive_message(
                QueueUrl = self.pagos_queue_url,
                MaxNumberOfMessages = 10,
                WaitTimeSeconds = 20).get("Messages", [])
            
            if not messages:
                return []

            return messages

        except Exception as e:
            raise ExternalServiceError(f'Error reading messages from SQS: {str(e)}')
    
    def processMessage(self, message):
        try:
            #Sacamos el body del mensaje
            body = Helper.loadJSON(message['Body'])

            #Actualizamos transaccion en base de datos
            transaction_data = {
                'transaction_id': body.get('transaction_id'),
                'data': {
                    'status': TransactionStatus[body.get('status')]
                }
            }
            response = payment_transaction_crud.update_payment_transaction(transaction_data.get('transaction_id'), transaction_data.get('data'))

            if not response:
                raise DatababaseError('Error updating payment transaction in database')

        except Exception as e:
            raise ExternalServiceError(f'Error processing message: {str(e)}')

    def deleteMessage(self, receipt_handle):
        try:
            #Borramos el mensaje de la cola
            self.sqs_client.delete_message(
                QueueUrl = self.pagos_queue_url,
                ReceiptHandle = receipt_handle
            )
        except Exception as e:
            raise ExternalServiceError(f'Error deleting message from SQS: {str(e)}')

    def sendMessage(self, message_body):
        try:
            #Enviamos mensaje a la cola
            self.sqs_client.send_message(
                QueueUrl = self.reservas_queue_url,
                MessageBody = json.dumps(message_body)
            )
        except Exception as e:
            raise ExternalServiceError(f'Error sending message to SQS: {str(e)}')