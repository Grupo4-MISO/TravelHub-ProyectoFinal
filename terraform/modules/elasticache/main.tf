resource "aws_security_group" "redis_sg" {
  name   = "${var.name}-sg"
  vpc_id = var.vpc_id

  tags = var.tags
}

resource "aws_security_group_rule" "allow_eks_to_redis" {
  type                     = "ingress"
  from_port                = 6379
  to_port                  = 6379
  protocol                 = "tcp"
  security_group_id        = aws_security_group.redis_sg.id
  source_security_group_id = var.eks_node_sg_id
}

resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = "${var.name}-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = var.name
  description                = "Redis cluster for ${var.name}"

  engine                     = "redis"
  engine_version             = var.engine_version
  node_type                  = var.node_type
  port                       = 6379

  num_cache_clusters         = 1

  security_group_ids         = [aws_security_group.redis_sg.id]
  subnet_group_name          = aws_elasticache_subnet_group.redis_subnet_group.name

  automatic_failover_enabled = false
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  tags = var.tags
}