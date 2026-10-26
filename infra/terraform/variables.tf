variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (staging, production)"
  type        = string
  default     = "production"
}

variable "db_tier" {
  description = "Cloud SQL database tier"
  type        = string
  default     = "db-custom-2-7680"
}

variable "db_name" {
  description = "Cloud SQL database name"
  type        = string
  default     = "social_bot_hunter"
}

variable "db_user" {
  description = "Cloud SQL username"
  type        = string
  default     = "sbh_admin"
}
