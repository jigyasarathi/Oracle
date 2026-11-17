output "service_url" {
  value = google_cloud_run_v2_service.oracle.uri
}

output "artifact_registry" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.oracle.repository_id}"
}
