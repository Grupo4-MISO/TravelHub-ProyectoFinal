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