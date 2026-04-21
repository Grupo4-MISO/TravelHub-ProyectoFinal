from app.utils.sqs_helper import SQSHelper
from app.utils.helper import Helper
import os

#URL de la cola de SQS y helper
SQS_PAGOS_URL = os.getenv('SQS_PAGOS_URL')
SQS_RESERVAS_URL = os.getenv('SQS_RESERVAS_URL')
sqs_helper = SQSHelper(SQS_PAGOS_URL, SQS_RESERVAS_URL)

def pagosWorker():
    while True:
        #Leemos la cola de SQS
        messages = sqs_helper.readMessages()
        
        for msg in messages:
            #Procesamos el mensaje
            response = sqs_helper.processMessage(msg)

            #Borramos el mensasje de la cola
            sqs_helper.deleteMessage(msg['ReceiptHandle'])

            #Enviamos mensaje a la cola de reservas
            reservas_message = Helper.reservasMessage(msg)
            sqs_helper.sendMessage(reservas_message)