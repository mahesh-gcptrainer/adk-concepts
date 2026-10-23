# Enable necessary APIs
resource "google_project_service" "cloudkms_api" {
  project = var.project_id
  service = "cloudkms.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild_api" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager_api" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudarmor_api" {
  project = var.project_id
  service = "compute.googleapis.com" # Cloud Armor uses Compute Engine API
  disable_on_destroy = false
}

# 1. Cloud KMS Key Ring and CryptoKeys (CMEK)
resource "google_kms_key_ring" "agfs_core_banking_kr" {
  name     = "agfs-${var.environment}-core-banking-kr"
  project  = var.project_id
  location = var.region
  depends_on = [google_project_service.cloudkms_api]
}

resource "google_kms_crypto_key" "cloudsql_ledger_cmek" {
  name            = "agfs-${var.environment}-cloudsql-ledger-cmek"
  key_ring        = google_kms_key_ring.agfs_core_banking_kr.id
  rotation_period = var.kms_key_rotation_period # 90 days

  lifecycle {
    prevent_destroy = true # Prevent accidental key deletion
  }
}

resource "google_kms_crypto_key" "gcs_statements_cmek" {
  name            = "agfs-${var.environment}-gcs-statements-cmek"
  key_ring        = google_kms_key_ring.agfs_core_banking_kr.id
  rotation_period = var.kms_key_rotation_period

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "gke_pd_cmek" {
  name            = "agfs-${var.environment}-gke-pd-cmek"
  key_ring        = google_kms_key_ring.agfs_core_banking_kr.id
  rotation_period = var.kms_key_rotation_period

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "secrets_cmek" {
  name            = "agfs-${var.environment}-secrets-cmek"
  key_ring        = google_kms_key_ring.agfs_core_banking_kr.id
  rotation_period = var.kms_key_rotation_period

  lifecycle {
    prevent_destroy = true
  }
}

# 2. Dedicated Service Accounts
# GKE Node Service Account
resource "google_service_account" "gke_nodes_sa" {
  account_id   = "agfs-${var.environment}-gke-nodes-sa"
  display_name = "GKE Node Service Account for ${var.environment}"
  project      = var.project_id
}

# GKE Workload Identity Service Account (Generic App SA for demonstration)
resource "google_service_account" "gke_app_sa" {
  account_id   = "agfs-${var.environment}-gke-app-sa"
  display_name = "GKE Application Workload Identity SA for ${var.environment}"
  project      = var.project_id
}

# CI/CD Deployment Service Account
resource "google_service_account" "cicd_sa" {
  account_id   = "agfs-${var.environment}-cicd-sa"
  display_name = "CI/CD Deployment Service Account for ${var.environment}"
  project      = var.project_id
}

# Management/Bastion Service Account
resource "google_service_account" "mgmt_bastion_sa" {
  account_id   = "agfs-${var.environment}-mgmt-bastion-sa"
  display_name = "Management Bastion Service Account for ${var.environment}"
  project      = var.project_id
}

# 3. IAM Bindings (Least Privilege)
# GKE Nodes SA permissions
resource "google_project_iam_member" "gke_nodes_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_nodes_sa.email}"
}

resource "google_project_iam_member" "gke_nodes_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_nodes_sa.email}"
}

resource "google_project_iam_member" "gke_nodes_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_nodes_sa.email}"
}

# GKE App SA permissions (example roles)
resource "google_project_iam_member" "gke_app_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gke_app_sa.email}"
}

resource "google_project_iam_member" "gke_app_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.gke_app_sa.email}"
}

resource "google_project_iam_member" "gke_app_secretmanager_viewer" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.gke_app_sa.email}"
}

# Cloud SQL Service Account needs KMS decrypt permission
# This SA is automatically created by Cloud SQL. We need to grant it.
# Format: service-<project-number>@gcp-sa-cloud-sql.iam.gserviceaccount.com
data "google_project" "project" {
  project_id = var.project_id
}

resource "google_kms_crypto_key_iam_member" "cloudsql_cmek_decrypt" {
  crypto_key_id = google_kms_crypto_key.cloudsql_ledger_cmek.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-cloud-sql.iam.gserviceaccount.com"
}

# Cloud Storage Service Account needs KMS decrypt permission
# Format: service-<project-number>@gs-project-accounts.iam.gserviceaccount.com
resource "google_kms_crypto_key_iam_member" "gcs_cmek_decrypt" {
  crypto_key_id = google_kms_crypto_key.gcs_statements_cmek.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
}


# 4. Cloud Armor Security Policy
resource "google_compute_security_policy" "agfs_cloud_armor_policy" {
  name    = var.cloud_armor_policy_name
  project = var.project_id
  description = "Cloud Armor WAF policy for Apex Global Financial Services core banking application."
  depends_on = [google_project_service.cloudarmor_api]

  # Default rule: allow all traffic
  default_rule {
    action   = "allow"
    priority = "2147483647" # Lowest priority
  }

  # Rule 1: Block SQL Injection (OWASP CRS)
  rule {
    action   = "deny-403"
    priority = "100"
    match {
      versioned_expr = "SRC_IPS_V1"
      expr           = "evaluateCloudArmorManagedRule('owasp-crs-v030301-SQLI-942990')"
    }
    description = "Block SQL Injection attempts."
  }

  # Rule 2: Block Cross-Site Scripting (OWASP CRS)
  rule {
    action   = "deny-403"
    priority = "110"
    match {
      versioned_expr = "SRC_IPS_V1"
      expr           = "evaluateCloudArmorManagedRule('owasp-crs-v030301-XSS-941320')"
    }
    description = "Block Cross-Site Scripting attempts."
  }

  # Rule 3: Rate Limiting Example (1000 requests per minute per IP)
  rule {
    action   = "throttle"
    priority = "200"
    match {
      versioned_expr = "SRC_IPS_V1"
      expr           = "true" # Apply to all requests
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny-429" # Too Many Requests
      enforce_on_key = "IP"
      # Maximum number of requests to allow in the interval
      rate_limit_threshold {
        count        = 1000
        interval_sec = 60
      }
    }
    description = "Rate limit requests to 1000 per minute per IP."
  }

  # Add more OWASP rules as needed, e.g., RFI, LFI, Command Injection
  # rule {
  #   action   = "deny-403"
  #   priority = "120"
  #   match {
  #     versioned_expr = "SRC_IPS_V1"
  #     expr           = "evaluateCloudArmorManagedRule('owasp-crs-v030301-LFI-930120')"
  #   }
  #   description = "Block Local File Inclusion attempts."
  # }
}

# 5. Secret Manager - Placeholder for DB password
resource "google_secret_manager_secret" "db_password_secret" {
  secret_id = "agfs-${var.environment}-db-password"
  project   = var.project_id
  replication {
    automatic = true
  }
  # Optional CMEK encryption for Secret Manager
  kms_key_name = google_kms_crypto_key.secrets_cmek.id
  depends_on = [google_project_service.secretmanager_api]
}

# Initial secret version (WARNING: DO NOT store actual passwords in IaC for production)
resource "google_secret_manager_secret_version" "db_password_secret_version" {
  secret      = google_secret_manager_secret.db_password_secret.id
  secret_data = "initial-secure-password-please-change" # Replace with actual secure method (e.g., K-pop, external secret management)
  # For production, this should be fetched from a secure source or managed by a rotation process.
  lifecycle {
    ignore_changes = [secret_data] # Prevent Terraform from overwriting value if it changes externally
  }
}
