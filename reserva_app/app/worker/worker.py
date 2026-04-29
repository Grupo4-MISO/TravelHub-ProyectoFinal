from app.utils.helper import ReservaHelper
from app.utils.sqs_helper import SQSHelper
from main import app
import os

#URL de la cola de SQS y helper
SQS_RESERVAS_URL = os.getenv('SQS_RESERVAS_URL')
SQS_MAIL_URL = os.getenv('SQS_MAIL_URL')
sqs_helper = SQSHelper(SQS_RESERVAS_URL, SQS_MAIL_URL)

def reservasWorker():
    with app.app_context():
        while True:
            #Leemos la cola de SQS
            messages = sqs_helper.readMessages()
            
            for msg in messages:
                #Sacamos el cuerpo del mensaje
                message = ReservaHelper.loadJSON(msg)

                #Procesamos el mensaje
                sqs_helper.processMessage(message)

                #Borramos el mensasje de la cola
                sqs_helper.deleteMessage(msg['ReceiptHandle'])

                #Enviamos mensaje a cola de mail
                sqs_helper.sendMessage(message.get('email'))