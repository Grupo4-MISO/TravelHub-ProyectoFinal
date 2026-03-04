variable "name" {
  description = "Nombre del cluster Redis"
  type        = string
}

variable "vpc_id" {
  description = "VPC donde se desplegará Redis"
  type        = string
}

variable "subnet_ids" {
  description = "Subnets privadas para Redis"
  type        = list(string)
}

variable "eks_node_sg_id" {
  description = "Security Group de los nodos de EKS"
  type        = string
}

variable "node_type" {
  description = "Tipo de instancia Redis"
  type        = string
  default     = "cache.t3.micro"
}

variable "engine_version" {
  description = "Versión de Redis"
  type        = string
  default     = "7.0"
}

variable "tags" {
  type    = map(string)
  default = {}
}