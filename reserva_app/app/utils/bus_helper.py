from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import ServiceBusError
import json

class BusHelper:
    def __init__(self, queue_name, service_bus_connection_str):
        self.queue_name = queue_name
        self.client = ServiceBusClient.from_connection_string(conn_str = service_bus_connection_str)

    def sendNotificacion(self, title, message, user_id):
        #Creamos payload para enviar a Azure Service Bus
        payload = {
            'title': title,
            'message': message,
            'user_id': user_id
        }

        try:
            #Enviamos el mensaje a Azure Service Bus
            with self.client:
                sender = self.client.get_queue_sender(queue_name = self.queue_name)

                with sender:
                    message = ServiceBusMessage(json.dumps(payload))
                    sender.send_messages(message)
                    print(f"Mensaje enviado a Azure Service Bus: {payload}")
        
        except ServiceBusError as e:
            raise Exception(f"Error al enviar mensaje a Azure Service Bus: {str(e)}")

        except Exception as e:
            raise Exception(f"Error inesperado al enviar mensaje a Azure Service Bus: {str(e)}")