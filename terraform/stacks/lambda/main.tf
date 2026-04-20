module "webhook" {
  source          = "../../modules/lambda"
  lambda_name     = var.webhook_config.lambda_name
  repository_name = var.webhook_config.repository_name
  image_version   = var.webhook_config.image_version
  env_variables   = merge(
    var.webhook_config.env_variables,
    {
      SQS_PAGOS_URL = "https://sqs.us-east-1.amazonaws.com/387050840675/pagos-sqs"
    }
  )
}

resource "aws_lambda_function_url" "webhook_url" {
  function_name      = module.webhook.lambda_name
  authorization_type = "NONE"
}
