variable "region" { 
  description = "La región de AWS donde se desplegarán los recursos."
  type        = string
  nullable    = false
}

variable "owner" {
  description = "Dueño de los recursos. Para propósito acadmémico."
  type        = string
  nullable    = false
}

variable "pagos_queue_name" {
  description = "Name of the SQS queue"
  type        = string
  nullable    = false
}

variable "reservas_queue_name" {
  description = "Name of the SQS queue"
  type        = string
  nullable    = false
}