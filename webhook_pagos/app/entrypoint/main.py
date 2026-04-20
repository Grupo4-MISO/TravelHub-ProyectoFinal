from app.utils.helper_queue import HelperQueue
import os

#Declaramos variables de entorno
SQS_PAGOS_URL = os.getenv('SQS_PAGOS_URL')

#Declaramos helper
sqs_helper = HelperQueue(SQS_PAGOS_URL)

def handler(event, context):
    #Enviamos mensaje a SQS
    response = sqs_helper.sendMessage(event)

    return response