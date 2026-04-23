from app.utils.sqs_helper import SQSHelper
import os

#URL de la cola de SQS y helper
SQS_RESERVAS_URL = os.getenv('SQS_RESERVAS_URL')
sqs_helper = SQSHelper(SQS_RESERVAS_URL)

def reservasWorker():
    while True:
        #Leemos la cola de SQS
        messages = sqs_helper.readMessages()
        
        for msg in messages:
            #Procesamos el mensaje
            response = sqs_helper.processMessage(msg)

            #Borramos el mensasje de la cola
            sqs_helper.deleteMessage(msg['ReceiptHandle'])