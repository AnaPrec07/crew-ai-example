# Terraform configuration for Crew AI Example on GCP Cloud Run

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "vertex_ai" {
  service = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_run" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build" {
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# Create service account for Cloud Run
resource "google_service_account" "crew_ai_sa" {
  account_id   = "crew-ai-runner"
  display_name = "Crew AI Service Account"
  description  = "Service account for Crew AI application running on Cloud Run"
}

# Grant Vertex AI User role to service account
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.crew_ai_sa.email}"
}

# Grant Vertex AI Service Agent role for full access
resource "google_project_iam_member" "vertex_ai_service_agent" {
  project = var.project_id
  role    = "roles/aiplatform.serviceAgent"
  member  = "serviceAccount:${google_service_account.crew_ai_sa.email}"
}

# Grant logging permissions
resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.crew_ai_sa.email}"
}

# Create Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "crew_ai_repo" {
  location      = var.region
  repository_id = "crew-ai-images"
  description   = "Docker repository for Crew AI application"
  format        = "DOCKER"
  
  depends_on = [google_project_service.artifact_registry]
}

# Cloud Run service
resource "google_cloud_run_v2_service" "crew_ai" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  
  template {
    service_account = google_service_account.crew_ai_sa.email
    
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
    
    containers {
      image = var.container_image
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "GCP_LOCATION"
        value = var.region
      }
      
      env {
        name  = "SERPER_API_KEY"
        value = var.serper_api_key
      }
      
      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }
      
      startup_probe {
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
        
        http_get {
          path = "/"
          port = 8080
        }
      }
    }
    
    timeout = "300s"
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  
  depends_on = [
    google_project_service.cloud_run,
    google_project_service.vertex_ai,
    google_project_iam_member.vertex_ai_user,
  ]
}

# Allow unauthenticated access (optional - remove if you want authenticated access only)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = google_cloud_run_v2_service.crew_ai.project
  location = google_cloud_run_v2_service.crew_ai.location
  name     = google_cloud_run_v2_service.crew_ai.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Grant Cloud Build service account permissions to deploy
data "google_project" "project" {
  project_id = var.project_id
}

resource "google_project_iam_member" "cloud_build_sa_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloud_build_sa_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}
