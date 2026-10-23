terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Remote backend configuration for state management
  # Replace 'YOUR_TERRAFORM_STATE_BUCKET_NAME' with your actual GCS bucket name
  backend "gcs" {
    bucket  = "agfs-terraform-state-bucket" # This bucket must exist and be globally unique
    prefix  = "terraform/state"
  }
}

# provider.tf
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}
