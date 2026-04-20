variable "region" {
  type    = string
  default = "us-east-1"
}

variable "owner" {
  description = "Owner tag for resources"
  type        = string
  nullable    = false
}

variable "webhook_config" {
  description = "Configuration for the consumer lambda function"
  type = object({
    lambda_name     = string
    repository_name = string
    image_version   = string
    env_variables   = map(string)
  })
}
