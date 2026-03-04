module "eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 18.31"

  cluster_name    = var.cluster_name
  cluster_version = var.k8s_cluster_version

  manage_aws_auth = true

  vpc_id     = data.aws_vpc.default.id
  subnet_ids = data.aws_subnets.all.ids

  cluster_endpoint_public_access = var.cluster_endpoint_public_access

  create_cloudwatch_log_group = false

  # Dejar que el módulo cree el IAM Role del cluster
  create_iam_role = true

  aws_auth_users = [
    {
      userarn  = "arn:aws:iam::387050840675:user/daniel"
      username = "daniel"
      groups   = ["system:masters"]
    }
  ]

  eks_managed_node_groups = {
    default = {

      # Dejar que el módulo cree el IAM Role de los nodes
      create_iam_role = true

      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t3.medium"]

      desired_size = 1
      min_size     = 1
      max_size     = 1
    }
  }

  # Reglas adicionales de seguridad para nodes
  node_security_group_additional_rules = {

    ingress_control_plane_to_nodes_webhook = {
      description                   = "Allow EKS Control Plane to connect to Ingress webhook"
      protocol                      = "tcp"
      from_port                     = 8443
      to_port                       = 8443
      type                          = "ingress"
      source_cluster_security_group = true
    }

    ingress_nodes_to_nodes_all_traffic = {
      description = "Allow nodes to communicate with each other"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }

    egress_nodes_to_internet = {
      description = "Allow nodes to connect to internet"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "egress"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  # IRSA deshabilitado por ahora
  enable_irsa = false

  # El módulo manejará automáticamente aws-auth
  create_aws_auth_configmap = false
  manage_aws_auth_configmap = false
}