terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. VPC Infrastructure
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "vehicure-vpc"
  cidr = var.vpc_cidr

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false
  enable_vpn_gateway = false

  tags = {
    Environment = var.environment
    Project     = "Vehicure"
  }
}

# 2. Amazon EKS Cluster (Kubernetes Workloads)
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "vehicure-eks-cluster"
  cluster_version = "1.28"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    general = {
      min_size     = 2
      max_size     = 10
      desired_size = 3

      instance_types = ["t3.xlarge"]
      capacity_type  = "ON_DEMAND"
    }
  }

  tags = {
    Environment = var.environment
    Project     = "Vehicure"
  }
}

# 3. Amazon RDS PostgreSQL 15 (3NF Core Database)
resource "aws_db_instance" "postgres" {
  identifier           = "vehicure-postgres-db"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t4g.large"
  allocated_storage    = 100
  max_allocated_storage = 500
  storage_type         = "gp3"
  
  db_name  = "vehicure_db"
  username = "vehicure_admin"
  password = var.db_password

  multi_az               = true
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = {
    Environment = var.environment
    Project     = "Vehicure"
  }
}

# 4. Amazon ElastiCache Redis (Bloom Filter & State Cache)
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "vehicure-redis-cache"
  engine               = "redis"
  node_type            = "cache.t4g.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  tags = {
    Environment = var.environment
    Project     = "Vehicure"
  }
}
