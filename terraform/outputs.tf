# Service Account Outputs
output "service_account_email" {
  description = "Email of the service account used by Cloud Run"
  value       = google_service_account.crew_ai_sa.email
}

output "service_account_id" {
  description = "ID of the service account"
  value       = google_service_account.crew_ai_sa.account_id
}

# Cloud Run Outputs
output "cloud_run_service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.crew_ai.uri
}

output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.crew_ai.name
}

# Artifact Registry Outputs
output "artifact_registry_repository" {
  description = "Artifact Registry repository for Docker images"
  value       = google_artifact_registry_repository.crew_ai_repo.id
}

output "docker_repository_url" {
  description = "URL for pushing Docker images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.crew_ai_repo.repository_id}"
}

# Deployment Information
output "deployment_commands" {
  description = "Commands to build and deploy the application"
  value = <<-EOT
    # Build and push Docker image:
    gcloud builds submit --tag ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.crew_ai_repo.repository_id}/crew-ai:latest

    # Update Terraform with new image:
    terraform apply -var="container_image=${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.crew_ai_repo.repository_id}/crew-ai:latest"
  EOT
}
