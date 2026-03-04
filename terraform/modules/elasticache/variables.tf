variable "name" { 
  description = "Nombre de redis."
  type        = string
  nullable    = false
}

variable "subnet_ids" {
  type = list(string)
}
variable "security_group_ids" {
  type = list(string)
}
variable "node_type" {
  default = "cache.t3.micro"
}
variable "tags" {
  type = map(string)
}