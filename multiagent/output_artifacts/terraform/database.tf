# Enable necessary APIs
resource "google_project_service" "sql_admin_api" {
  project = var.project_id
  service = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

# 1. Private Services Access Connection (VPC Peering)
resource "google_service_networking_connection" "agfs_vpc_service_peering" {
  network                 = google_compute_network.agfs_core_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
  depends_on = [
    google_project_service.servicenetworking_api,
    google_compute_global_address.private_ip_alloc
  ]
}

# 2. Cloud SQL for PostgreSQL Instance
resource "google_sql_database_instance" "agfs_core_db" {
  name             = var.db_instance_name
  project          = var.project_id
  database_version = "POSTGRES_14" # As per blueprint
  region           = var.region
  settings {
    tier             = var.db_tier
    disk_size        = var.db_disk_size_gb
    disk_type        = "SSD"
    backup_configuration {
      enabled            = true
      binary_log_enabled = true # Required for point-in-time recovery
      start_time         = "03:00" # Daily backup window
      location           = var.region # Backup location
      transaction_log_retention_days = 7 # Retain transaction logs for 7 days
      retained_backups_count = 7 # Keep last 7 backups
    }

    ip_configuration {
      ipv4_enabled = false # Private IP only
      # Authorized networks to allow connections from GKE workload subnet
      authorized_networks {
        value           = var.subnet_workload_cidr
        display_name    = "GKE Workload Subnet"
      }
      # Potentially add management/bastion subnet if direct access is needed
      # authorized_networks {
      #   value        = var.subnet_mgmt_cidr
      #   display_name = "Management Subnet"
      # }
      require_ssl = true # Enforce SSL connections
    }
    # Point-in-time recovery (PITR)
    point_in_time_recovery_enabled = true

    # Database flags (example: for logging, performance tuning)
    # database_flags {
    #   name  = "log_connections"
    #   value = "on"
    # }
  }

  # Regional High Availability
  database_instance_type = "REGIONAL"

  # CMEK encryption
  settings_version = 1 # Required to ensure settings are applied correctly with CMEK
  disk_encryption_configuration {
    kms_key_name = google_kms_crypto_key.cloudsql_ledger_cmek.id
  }

  depends_on = [
    google_project_service.sql_admin_api,
    google_service_networking_connection.agfs_vpc_service_peering,
    google_kms_crypto_key_iam_member.cloudsql_cmek_decrypt # Ensure KMS permissions are set
  ]
}

# 3. Create a Database
resource "google_sql_database" "core_banking_db" {
  name     = var.db_database_name
  instance = google_sql_database_instance.agfs_core_db.name
  charset  = "UTF8"
  collation = "en_US.UTF8"
}

# 4. Create a Database User
resource "google_sql_user" "app_db_user" {
  name     = var.db_user_name
  instance = google_sql_database_instance.agfs_core_db.name
  host     = "%" # Allow connections from any host (within authorized networks)
  password = random_password.db_user_password.result # Using random_password for initial setup
  # For production, this password should come from a secure source like Secret Manager
  # and be managed by an external rotation process.
}

# Helper to generate a strong random password for the DB user (for initial setup)
resource "random_password" "db_user_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Optional: Store generated DB password in Secret Manager
resource "google_secret_manager_secret_version" "db_user_password_sm_version" {
  secret      = google_secret_manager_secret.db_password_secret.id
  secret_data = random_password.db_user_password.result
  lifecycle {
    ignore_changes = [secret_data] # Prevent Terraform from overwriting value if it changes externally
  }
}
