from onesignal.model.notification import Notification
from onesignal import ApiClient, Configuration
from onesignal.rest import ApiException
from onesignal.api import default_api

class OneSignalHelper:
    def __init__(self, app_id, api_key):
        self.app_id = app_id
        self.api_key = api_key
        config = Configuration(rest_api_key = self.api_key)
        self.client = default_api.DefaultApi(ApiClient(config))

    def sendNotificacion(self, title, message, user_id):
        #Creamos notificacion
        notificacion = Notification(
            app_id = self.app_id,
            contents = {"en": message},
            headings = {"en": title},
            include_external_user_ids = [user_id]
        )

        try:
            #Enviamos la notificacion
            response = self.client.create_notification(notificacion)
            print(f"Notificación enviada a OneSignal: {response}")
        
        except ApiException as e:
            raise Exception(f"Error al enviar la notificación a OneSignal: {e}")
