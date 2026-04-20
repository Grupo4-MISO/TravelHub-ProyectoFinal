module "pagos_queue_name" {
  source     = "../../modules/sqs"
  queue_name = var.pagos_queue_name
}

module "reservas_queue_name" {
  source     = "../../modules/sqs"
  queue_name = var.reservas_queue_name
}
