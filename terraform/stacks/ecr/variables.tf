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

variable "keep_tags_number" {
  description = "Number of tags to keep in the registry"
  type        = number
}

variable "inventarios_repository_name" {
  description = "Name of the repository to apps"
  type        = string
  nullable    = false
}

variable "reservas_repository_name" {
  description = "Name of the repository to apps"
  type        = string
  nullable    = false
}

variable "busquedas_repository_name" {
  description = "Name of the repository to apps"
  type        = string
  nullable    = false
}

variable "comentarios_repository_name" {
  description = "Name of the repository to apps"
  type        = string
  nullable    = false
}

variable "auth_repository_name" {
  description = "Name of the repository to apps"
  type        = string
  nullable    = false
}

variable "webhook_pagos_repository_name" {
  description = "Name of the repository to apps"
  type        = string
  nullable    = false
}

variable "transacciones_repository_name" {
  description = "Name of the repository to apps"
  type        = string
  nullable    = false
}