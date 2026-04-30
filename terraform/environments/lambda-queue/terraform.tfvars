region = "us-east-1"
owner  = "grupo4"

email_config = {
  lambda_name     = "email-app"
  repository_name = "email-app"
  image_version   = "v1.0.0"
  env_variables   = {
    LOG_LEVEL = "INFO"
  }
}

queue_name = "mail-sqs"
number_of_messages_to_process = 10