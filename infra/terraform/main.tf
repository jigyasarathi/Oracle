terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  apis = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
    "cloudtrace.googleapis.com",
  ]
  runtime_roles = [
    "roles/bigquery.jobUser",   # run queries
    "roles/bigquery.dataViewer", # read-only. Scope to your own dataset when you use private data.
    "roles/aiplatform.user",     # call Gemini on Vertex AI
    "roles/cloudtrace.agent",    # write traces
  ]
}

resource "google_project_service" "apis" {
  for_each           = toset(local.apis)
  service            = each.value
  disable_on_destroy = false
}

resource "google_service_account" "oracle" {
  account_id   = "oracle-runtime"
  display_name = "ORACLE runtime (read-only)"
  depends_on   = [google_project_service.apis]
}

resource "google_project_iam_member" "oracle_roles" {
  for_each = toset(local.runtime_roles)
  project  = var.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.oracle.email}"
}

resource "google_artifact_registry_repository" "oracle" {
  location      = var.region
  repository_id = "oracle"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

resource "google_cloud_run_v2_service" "oracle" {
  name     = "oracle"
  location = var.region

  template {
    service_account = google_service_account.oracle.email

    containers {
      image = var.image

      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "TRUE"
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.vertex_location
      }
      env {
        name  = "BQ_PROJECT"
        value = var.project_id
      }
      env {
        name  = "RETRIEVER_BACKEND"
        value = "tfidf"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }
  }

  depends_on = [google_project_service.apis]
}
