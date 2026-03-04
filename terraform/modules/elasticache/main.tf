resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.name}-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id          = var.name
  description                   = "Redis replication group"
  engine                        = "redis"
  engine_version                = "7.0"
  node_type                     = var.node_type
  port                          = 6379

  num_cache_clusters            = 1

  subnet_group_name             = aws_elasticache_subnet_group.this.name
  security_group_ids            = var.security_group_ids

  automatic_failover_enabled    = false
  multi_az_enabled              = false

  at_rest_encryption_enabled    = true
  transit_encryption_enabled    = true

  tags = var.tags
}

resource "aws_security_group" "redis_sg" {
  name   = "redis-sg"
  vpc_id = data.aws_vpc.default.id
}

resource "aws_security_group_rule" "allow_eks_to_redis" {
  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  security_group_id        = aws_security_group.redis_sg.id
  source_security_group_id = var.eks_node_sg_id
}