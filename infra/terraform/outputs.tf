output "api_service_uri" {
  description = "Public URL of the deployed Cloud Run API service"
  value       = google_cloud_run_v2_service.api.uri
}

output "cloud_sql_instance_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "snapshots_bucket_name" {
  description = "GCS bucket for raw snapshots"
  value       = google_storage_bucket.snapshots.name
}

output "exports_bucket_name" {
  description = "GCS bucket for evidence exports"
  value       = google_storage_bucket.exports.name
}
