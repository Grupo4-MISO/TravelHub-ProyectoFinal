# =========================
# Cola SQS
# =========================
module "sqs_queue" {
  source     = "../../modules/sqs"
  queue_name = var.queue_name
}

# =========================
# Lambda email
# =========================
module "email" {
  source          = "../../modules/lambda"
  lambda_name     = var.email_config.lambda_name
  repository_name = var.email_config.repository_name
  image_version   = var.email_config.image_version

  env_variables = merge(
    var.email_config.env_variables,
    {
      SQS_QUEUE_URL = module.sqs_queue.sqs_queue_url,
    }
  )
}

# =========================
# Function URL (endpoint público)
# =========================
resource "aws_lambda_function_url" "email_url" {
  function_name      = module.email.lambda_name
  authorization_type = "NONE"
}

resource "aws_lambda_permission" "function_url_public" {
  statement_id  = "FunctionURLAllowPublicAccess"
  action        = "lambda:InvokeFunctionUrl"
  function_name = module.email.lambda_name
  principal     = "*"

  function_url_auth_type = "NONE"
}

# =========================
# SQS -> Lambda trigger
# =========================
resource "aws_lambda_event_source_mapping" "email_mapping" {
  event_source_arn = module.sqs_queue.sqs_queue_arn
  function_name    = module.email.lambda_name
  batch_size       = var.number_of_messages_to_process
  enabled          = true
}