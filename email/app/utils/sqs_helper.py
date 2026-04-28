import boto3

class SQSHelper:
    def __init__(self, sqs_url: str):
        #Creamos cliente de SQS
        self.sqs_client = boto3.client('sqs', region_name = 'us-east-1')

        #Guardamos la URL de la cola
        self.sqs_queue_url = sqs_url

    def deleteMessage(self, receipt_handle):
        try:
            #Borramos el mensaje de la cola
            self.sqs_client.delete_message(
                QueueUrl = self.sqs_queue_url,
                ReceiptHandle = receipt_handle
            )
        except Exception as e:
            return f"Error deleting message from SQS: {str(e)}"