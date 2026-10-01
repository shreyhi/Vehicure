variable "aws_region" {
  description = "AWS Cloud region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Target deployment environment (dev/prod)"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_password" {
  description = "RDS PostgreSQL Master Password"
  type        = string
  sensitive   = true
  default     = "VehicureSecurePassword2026!"
}
