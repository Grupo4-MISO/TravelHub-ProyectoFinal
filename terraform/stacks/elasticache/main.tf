data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    bucket = "proyecto-final-1-grupo-4"
    key    = "eks/terraform.tfstate"
    region = "us-east-1"
  }
}

module "redis" {
  source = "../../modules/elasticache"

  name           = var.name
  vpc_id         = data.aws_vpc.default.id
  subnet_ids     = data.aws_subnets.private.ids
  eks_node_sg_id = data.terraform_remote_state.eks.outputs.node_security_group_id
}