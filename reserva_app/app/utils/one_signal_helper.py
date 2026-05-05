from onesignal.rest import ApiException
from onesignal.api import default_api
import onesignal

class OneSignalHelper:
    def __init__(self, app_id, api_key):
        self.app_id = app_id
        self.api_key = api_key
        config = onesignal.Configuration(rest_api_key = self.api_key)
        self.client = default_api.DefaultApi(onesignal.ApiClient(config))

    def sendNotificacion(self, hotel_name, user_id):
        #Creamos notificacion
        notificacion = onesignal.Notification(
            app_id = self.app_id,
            contents = onesignal.StringMap(en = f"Tu reserva en el {hotel_name} ha sido confirmada."),
            headings = onesignal.StringMap(en = '¡Reserva Confirmada!'),
            include_subscription_ids = [user_id]
        )

        try:
            #Enviamos la notificacion
            self.client.create_notification(notificacion)
        
        except ApiException as e:
            raise Exception(f"Error al enviar la notificación a OneSignal: {e}")
