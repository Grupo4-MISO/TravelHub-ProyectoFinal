from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from app.utils.email_helper import EmailHelper
import json
import os

#Declaramos variables de entorno
SQS_URL = os.getenv('SQS_URL')

@event_source(data_class = SQSEvent)
def handler(event: SQSEvent, context):
    for record in event.records:
        #Sacamos el body del mensaje de SQS
        body = json.loads(record.body)

        #Creamos el header del mensaje de email
        header_message = EmailHelper.headerEmailMessage(body)

        #Creamos el cuerpo del mensaje de email
        email_message = EmailHelper.createEmailMessage(header_message)

        #Enviamos email
        EmailHelper.sendEmail(email_message)


