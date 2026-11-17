variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "Region for Cloud Run and Artifact Registry"
  default     = "us-central1"
}

variable "vertex_location" {
  type        = string
  description = "Vertex AI location used for Gemini calls"
  default     = "us-central1"
}

variable "image" {
  type        = string
  description = "Container image to deploy. Default is Google's hello placeholder; replace after your first build."
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}
