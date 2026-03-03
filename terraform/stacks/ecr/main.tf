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
