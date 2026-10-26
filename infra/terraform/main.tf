terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.25"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Cloud Storage Buckets (Snapshots, Model Artifacts, Audit Exports)
resource "google_storage_bucket" "snapshots" {
  name                     = "${var.project_id}-sbh-snapshots-${var.environment}"
  location                 = var.region
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "exports" {
  name                     = "${var.project_id}-sbh-exports-${var.environment}"
  location                 = var.region
  uniform_bucket_level_access = true
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# 2. Cloud SQL PostgreSQL 16
resource "random_id" "db_suffix" {
  byte_length = 4
}

resource "google_sql_database_instance" "postgres" {
  name             = "sbh-pg-${var.environment}-${random_id.db_suffix.hex}"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier = var.db_tier
    ip_configuration {
      ipv4_enabled    = true
      require_ssl     = true
    }
    backup_configuration {
      enabled    = true
      start_time = "02:00"
    }
  }
  deletion_protection = var.environment == "production"
}

resource "google_sql_database" "sbh_db" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

# 3. Secret Manager Secrets
resource "google_secret_manager_secret" "db_credentials" {
  secret_id = "sbh-db-credentials-${var.environment}"
  replication {
    auto {}
  }
}

# 4. Cloud Tasks Queue for Asynchronous Scans
resource "google_cloud_tasks_queue" "scan_queue" {
  name     = "sbh-scan-queue-${var.environment}"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = 10
    max_dispatches_per_second = 5
  }

  retry_config {
    max_attempts       = 5
    min_backoff        = "5s"
    max_backoff        = "300s"
    max_doublings      = 3
  }
}

# 5. Service Account for Cloud Run API & Workers
resource "google_service_account" "api_sa" {
  account_id   = "sbh-api-${var.environment}"
  display_name = "Social Bot Hunter API Service Account"
}

resource "google_project_iam_member" "sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "gcs_user" {
  project = var.project_id
  role    = "roles/storage.objectUser"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

# 6. Cloud Run API Service
resource "google_cloud_run_v2_service" "api" {
  name     = "sbh-api-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.api_sa.email
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = "gcr.io/${var.project_id}/sbh-api:latest"
      resources {
        limits = {
          cpu    = "2000m"
          memory = "2Gi"
        }
      }
      env {
        name  = "SBH_ENV"
        value = var.environment
      }
      env {
        name  = "GCS_SNAPSHOT_BUCKET"
        value = google_storage_bucket.snapshots.name
      }
    }
  }
}
