# Project Configuration
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

# Cloud Run Configuration
variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "crew-ai-travel-agent"
}

variable "container_image" {
  description = "Container image to deploy (format: region-docker.pkg.dev/project/repository/image:tag)"
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"  # Default placeholder
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cpu_limit" {
  description = "CPU limit for Cloud Run container"
  type        = string
  default     = "2"
}

variable "memory_limit" {
  description = "Memory limit for Cloud Run container"
  type        = string
  default     = "2Gi"
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access to Cloud Run service"
  type        = bool
  default     = false
}

# Application Configuration
variable "serper_api_key" {
  description = "Serper API key for search functionality"
  type        = string
  sensitive   = true
  default     = ""
}
