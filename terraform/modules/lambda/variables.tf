variable "lambda_name" {
  description = "Lambda function name"
  type        = string
}

variable "image_version" {
  description = "major.minor.patch version of the image"
  type        = string
  nullable    = false
}

variable "repository_name" {
  description = "Name of the image repository in the ECR service"
  type        = string
  nullable    = false
}

variable "env_variables" {
  description = "Map object with environment variables for the lambda function. Empty by default."
  type        = map(string)
  default     = {}
}

variable "role_arn" {
  description = "ARN de un rol existente para la Lambda"
  type        = string
  default     = null
}

variable "create_role" {
  description = "Indica si el módulo debe crear un rol"
  type        = bool
  default     = true
}