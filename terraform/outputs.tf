output "eks_cluster_endpoint" {
  description = "EKS Kubernetes Cluster Endpoint"
  value       = module.eks.cluster_endpoint
}

output "postgres_endpoint" {
  description = "RDS PostgreSQL Database Endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis Endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}
