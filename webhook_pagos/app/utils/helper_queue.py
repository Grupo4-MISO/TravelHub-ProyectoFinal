from botocore.exceptions import ClientError
from app.utils.helper import Helper
import boto3

class HelperQueue:
    def __init__(self, queue_url):
        self.queue_url = queue_url
        self.sqs_client = boto3.client('sqs')
    
    def sendMessage(self, message_body):
        try:
            #Enviamos mensaje a SQS
            response = self.sqs_client.send_message(
                QueueUrl = self.queue_url,
                MessageBody = message_body
            )

            return Helper.response(status_code = 200, message = response)

        except ClientError as e:
            return Helper.response(status_code = 400, message = e.response['Error']['Message'])

        except Exception as e:
            return Helper.response(status_code = 500, message = str(e))