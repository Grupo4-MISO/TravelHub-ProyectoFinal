from app.utils.sqs_helper import SQSHelper
from app.utils.helper import Helper
from main import app
import os

#URL de la cola de SQS y helper
SQS_PAGOS_URL = os.getenv('SQS_PAGOS_URL')
SQS_RESERVAS_URL = os.getenv('SQS_RESERVAS_URL')
sqs_helper = SQSHelper(SQS_PAGOS_URL, SQS_RESERVAS_URL)

def pagosWorker():
    with app.app_context():
        while True:
            #Leemos la cola de SQS
            messages = sqs_helper.readMessages()
            
            for msg in messages:
                #Leemos el body del mensaje
                message = Helper.loadJSON(msg)

                #Procesamos el mensaje
                payment = sqs_helper.processMessage(message)

                #Borramos el mensasje de la cola
                sqs_helper.deleteMessage(msg['ReceiptHandle'])

                #Enviamos mensaje a la cola de reservas
                reservas_message = Helper.reservasMessage(payment, message)
                sqs_helper.sendMessage(reservas_message)