region = "us-east-1"
owner  = "grupo4"

webhook_config = {
  lambda_name     = "webhook-pagos-app"
  repository_name = "webhook-pagos-app"
  image_version   = "v1.0.0"
  env_variables   = {
    LOG_LEVEL = "INFO"
  }
}