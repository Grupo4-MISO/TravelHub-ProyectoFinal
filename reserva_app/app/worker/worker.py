from reserva_app.app.utils.bus_helper import BusHelper
from app.utils.helper import ReservaHelper
from app.utils.sqs_helper import SQSHelper
from main import app
import os



#Inventarios URL
INVENTARIOS_URL = os.getenv('INVENTARIOS_URL')

#URL de la cola de SQS y helper
SQS_RESERVAS_URL = os.getenv('SQS_RESERVAS_URL')
SQS_MAIL_URL = os.getenv('SQS_MAIL_URL')
sqs_helper = SQSHelper(SQS_RESERVAS_URL, SQS_MAIL_URL)

#Variables de entorno para la conexion a Azure Service Bus
SERVICE_BUS_CONNECTION_STR = os.getenv('SERVICE_BUS_CONNECTION_STR')
QUEUE_NAME = os.getenv('QUEUE_NAME')
bus_helper = BusHelper(SERVICE_BUS_CONNECTION_STR, QUEUE_NAME)

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

                #Consultamos la reserva en la base de datos
                reserva = ReservaHelper.reservaInfo(message.get('reserva_id'))

                #Consultamos inventario
                currency_code = message.get('payment_info').get('currency')
                hospedaje_info = ReservaHelper.hospedajeInfo(INVENTARIOS_URL, reserva.get('habitacion_id'), currency_code)

                #Enviamos notificación a OneSignal
                notification_title = f"Confirmación reserva: {reserva.get('public_id')}"
                notification_message = f"Tu reserva en el hotel {hospedaje_info.get('nombre')} ha sido confirmada del {reserva.get('check_in')} al {reserva.get('check_out')}."
                bus_helper.sendNotification(notification_title, notification_message, reserva.get('user_id'))

                #Enviamos mensaje a cola de mail
                mail_message = ReservaHelper.mailMessage(reserva, hospedaje_info, message)
                sqs_helper.sendMessage(mail_message)