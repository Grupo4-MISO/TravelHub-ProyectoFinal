from app.errors.exceptions import InternalServerError, DatababaseError, ExternalServiceError
from app.services.transactions_crud import PaymentTransactionCrud, PaymentCrud
from app.db.models import TransactionStatus, PaymentStatus
from app.utils.helper import Helper
import boto3
import json

#Instancia de transaction CRUD
payment_crud = PaymentCrud()
payment_transaction_crud = PaymentTransactionCrud()

class SQSHelper:
    def __init__(self, pagos_sqs_url: str, reservas_sqs_url: str):
        #Creamos cliente de SQS
        self.sqs_client = boto3.client('sqs', region_name = 'us-east-1')

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
    
    def processMessage(self, message_body):
        try:
            #Construimos dicionarios para crear objeto de pago de transaccion 
            transaccion_data = {
                'payment_id': message_body.get('payment_id'),
                'status': TransactionStatus[message_body.get('status')],
                'provider_transaction_id': message_body.get('external_payment_id'),
                'response': message_body
            }
            payment_transaction = payment_transaction_crud.create_payment_transaction(transaccion_data)

            #Validamos que se haya creado la transaccion
            if not payment_transaction:
                raise DatababaseError('Error creating payment transaction in the database')

            #Actualizamos el estado del pago
            payment_id = Helper.normalizeUUID(message_body.get('payment_id'))
            status = PaymentStatus.authorized if message_body.get('status') == 'success' else PaymentStatus.pending
            data_update_payment = {
                'status': status
            }
            payment = payment_crud.update_payment(payment_id, data_update_payment)
            
            return payment
        
        except Exception as e:
            raise InternalServerError(f'Error processing message: {str(e)}')

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