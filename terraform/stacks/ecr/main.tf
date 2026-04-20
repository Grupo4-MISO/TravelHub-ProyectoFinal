# This can be improved by using a for_each loop if the number of repositories increases
module "inventarios_repository_name" {
  source = "../../modules/ecr"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.inventarios_repository_name
}

module "reservas_repository_name" {
  source = "../../modules/ecr"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.reservas_repository_name
}

module "busquedas_repository_name" {
  source = "../../modules/ecr"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.busquedas_repository_name
}

module "comentarios_repository_name" {
  source = "../../modules/ecr"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.comentarios_repository_name
}

module "auth_repository_name" {
  source = "../../modules/ecr"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.auth_repository_name
}

module "webhook_pagos_repository_name" {
  source = "../../modules/ecr"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.webhook_pagos_repository_name
}