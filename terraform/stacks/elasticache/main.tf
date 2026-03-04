module "redis" {
  source = "../../modules/elasticache"

  name            = var.name
  vpc_id          = data.aws_vpc.default.id
  subnet_ids      = data.aws_subnets.private.ids
  eks_node_sg_id  = module.eks_cluster.node_security_group_id

  tags = {
    Environment = "dev"
  }
}