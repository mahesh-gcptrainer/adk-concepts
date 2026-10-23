Here is the production-ready Terraform HCL code synthesized from all preceding architectural, networking, and security recommendations for Apex Global Financial Services.

---

### Terraform Configuration

This Terraform configuration sets up the core infrastructure for Apex Global Financial Services' Core Banking & Payment Modernization on Google Cloud Platform. It adheres to best practices for security, high availability, and network segmentation.

---

#### 1. `versions.tf` & `provider.tf`

```terraform
# versions.tf
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
```

---

#### 2. `variables.tf`

```terraform
# variables.tf

variable "project_id" {
  description = "The GCP project ID."
  type        = string
  validation {
    condition     = length(var.project_id) > 0
    error_message = "The project_id must not be empty."
  }
}

variable "region" {
  description = "The GCP region to deploy resources into."
  type        = string
  default     = "us-central1"
  validation {
    condition     = contains(["us-central1", "us-east1", "europe-west1"], var.region) # Example regions
    error_message = "The region must be a valid GCP region (e.g., us-central1)."
  }
}

variable "environment" {
  description = "The deployment environment (e.g., prod, dev, staging)."
  type        = string
  default     = "prod"
  validation {
    condition     = contains(["prod", "dev", "staging"], var.environment)
    error_message = "The environment must be 'prod', 'dev', or 'staging'."
  }
}

variable "vpc_name" {
  description = "The name of the VPC network."
  type        = string
  default     = "agfs-core-vpc"
}

variable "vpc_primary_cidr" {
  description = "The primary CIDR range for the VPC network."
  type        = string
  default     = "10.0.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_primary_cidr, 0))
    error_message = "Invalid VPC primary CIDR format."
  }
}

variable "subnet_ingress_cidr" {
  description = "CIDR range for the Ingress/Proxy subnet."
  type        = string
  default     = "10.0.0.0/24"
  validation {
    condition     = can(cidrhost(var.subnet_ingress_cidr, 0))
    error_message = "Invalid Ingress subnet CIDR format."
  }
}

variable "subnet_workload_cidr" {
  description = "CIDR range for the GKE Workload subnet."
  type        = string
  default     = "10.0.1.0/20"
  validation {
    condition     = can(cidrhost(var.subnet_workload_cidr, 0))
    error_message = "Invalid Workload subnet CIDR format."
  }
}

variable "subnet_data_cidr" {
  description = "CIDR range for the Persistence/Data subnet."
  type        = string
  default     = "10.0.2.0/24"
  validation {
    condition     = can(cidrhost(var.subnet_data_cidr, 0))
    error_message = "Invalid Data subnet CIDR format."
  }
}

variable "subnet_mgmt_cidr" {
  description = "CIDR range for the Management/Bastion subnet."
  type        = string
  default     = "10.0.3.0/28"
  validation {
    condition     = can(cidrhost(var.subnet_mgmt_cidr, 0))
    error_message = "Invalid Management subnet CIDR format."
  }
}

variable "gke_pods_secondary_cidr" {
  description = "Secondary CIDR range for GKE Pods."
  type        = string
  default     = "10.10.0.0/16"
  validation {
    condition     = can(cidrhost(var.gke_pods_secondary_cidr, 0))
    error_message = "Invalid GKE Pods secondary CIDR format."
  }
}

variable "gke_services_secondary_cidr" {
  description = "Secondary CIDR range for GKE Services."
  type        = string
  default     = "10.20.0.0/20"
  validation {
    condition     = can(cidrhost(var.gke_services_secondary_cidr, 0))
    error_message = "Invalid GKE Services secondary CIDR format."
  }
}

variable "psa_range_name" {
  description = "Name for the IP range reserved for Private Services Access."
  type        = string
  default     = "agfs-core-psa-range"
}

variable "psa_cidr_range" {
  description = "CIDR range for Private Services Access (PSA)."
  type        = string
  default     = "10.250.0.0/16"
  validation {
    condition     = can(cidrhost(var.psa_cidr_range, 0))
    error_message = "Invalid PSA CIDR format."
  }
}

variable "gke_node_count" {
  description = "Number of nodes per GKE node pool. Initial estimate, will autoscale."
  type        = number
  default     = 3 # Minimum for regional HA
  validation {
    condition     = var.gke_node_count >= 1
    error_message = "GKE node count must be at least 1."
  }
}

variable "gke_machine_type" {
  description = "Machine type for GKE nodes."
  type        = string
  default     = "e2-standard-4" # Balanced choice for production
}

variable "gke_kubernetes_version" {
  description = "The Kubernetes version for the GKE cluster. Use a stable recent version."
  type        = string
  default     = "1.27" # Specify a major.minor version, GKE will pick latest patch.
}

variable "db_tier" {
  description = "Cloud SQL machine type (tier)."
  type        = string
  default     = "db-custom-4-16384" # 4 vCPU, 16GB RAM for high load
}

variable "db_disk_size_gb" {
  description = "Cloud SQL disk size in GB."
  type        = number
  default     = 200 # Initial size, can be increased
}

variable "db_instance_name" {
  description = "Name of the Cloud SQL instance."
  type        = string
  default     = "agfs-core-db"
}

variable "db_database_name" {
  description = "Name of the primary database."
  type        = string
  default     = "core-banking-db"
}

variable "db_user_name" {
  description = "Username for the Cloud SQL database."
  type        = string
  default     = "app_user"
}

variable "kms_key_rotation_period" {
  description = "KMS key rotation period in seconds (90 days = 7776000s)."
  type        = string
  default     = "7776000s" # 90 days
}

variable "cloud_armor_policy_name" {
  description = "Name for the Cloud Armor Security Policy."
  type        = string
  default     = "agfs-prod-core-banking-security-policy"
}

variable "trusted_management_cidrs" {
  description = "List of CIDRs from which management access (e.g., SSH to bastions) is allowed."
  type        = list(string)
  default     = ["0.0.0.0/0"] # WARNING: This should be restricted to your corporate IPs.
}
```

---

#### 3. `vpc.tf`

```terraform
# vpc.tf

# Enable necessary APIs
resource "google_project_service" "compute_api" {
  project = var.project_id
  service = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "servicenetworking_api" {
  project = var.project_id
  service = "servicenetworking.googleapis.com"
  disable_on_destroy = false
}

# 1. Custom Mode VPC Network
resource "google_compute_network" "agfs_core_vpc" {
  name                    = var.vpc_name
  project                 = var.project_id
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  mtu                     = 1460 # Recommended for GKE
  depends_on              = [google_project_service.compute_api]
}

# 2. Subnets with Private Google Access
resource "google_compute_subnetwork" "sbn_ingress" {
  name                     = "${var.vpc_name}-sbn-${var.region}-ingress"
  ip_cidr_range            = var.subnet_ingress_cidr
  region                   = var.region
  network                  = google_compute_network.agfs_core_vpc.id
  private_ip_google_access = true
  description              = "Subnet for Global External HTTP(S) Load Balancer proxy-only."
}

resource "google_compute_subnetwork" "sbn_workload" {
  name                     = "${var.vpc_name}-sbn-${var.region}-workload"
  ip_cidr_range            = var.subnet_workload_cidr
  region                   = var.region
  network                  = google_compute_network.agfs_core_vpc.id
  private_ip_google_access = true
  description              = "Subnet for GKE nodes, pods, and services."

  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = var.gke_pods_secondary_cidr
  }
  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = var.gke_services_secondary_cidr
  }
}

resource "google_compute_subnetwork" "sbn_data" {
  name                     = "${var.vpc_name}-sbn-${var.region}-data"
  ip_cidr_range            = var.subnet_data_cidr
  region                   = var.region
  network                  = google_compute_network.agfs_core_vpc.id
  private_ip_google_access = true
  description              = "Subnet for persistence-related VMs or future data services."
}

resource "google_compute_subnetwork" "sbn_mgmt" {
  name                     = "${var.vpc_name}-sbn-${var.region}-mgmt"
  ip_cidr_range            = var.subnet_mgmt_cidr
  region                   = var.region
  network                  = google_compute_network.agfs_core_vpc.id
  private_ip_google_access = true
  description              = "Subnet for bastion hosts and management tools."
}

# Reserve IP range for Private Services Access (PSA)
resource "google_compute_global_address" "private_ip_alloc" {
  provider      = google-beta # Required for private IP allocations
  project       = var.project_id
  name          = var.psa_range_name
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16 # /16 as per spec
  network       = google_compute_network.agfs_core_vpc.id
}

# 3. Cloud Router
resource "google_compute_router" "agfs_cloud_router" {
  name    = "${var.vpc_name}-${var.region}-router"
  project = var.project_id
  region  = var.region
  network = google_compute_network.agfs_core_vpc.id
}

# 4. Cloud NAT Gateway
resource "google_compute_router_nat" "agfs_nat_gateway" {
  name                               = "${var.vpc_name}-${var.region}-nat"
  project                            = var.project_id
  router                             = google_compute_router.agfs_cloud_router.name
  region                             = google_compute_router.agfs_cloud_router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  log_config {
    enable = true
    filter = "ERRORS_ONLY" # Log errors only, can be ALL
  }
}

# 5. VPC Firewall Rules (Default-deny implied, explicit allows)
# Rule to allow Google Health Checks (Load Balancer to GKE nodes)
resource "google_compute_firewall" "allow_lb_health_check" {
  name    = "allow-lb-health-check"
  project = var.project_id
  network = google_compute_network.agfs_core_vpc.name
  direction = "INGRESS"
  priority = 1000 # Default

  source_ranges = [
    "130.211.0.0/22", # Google Load Balancer health check IPs
    "35.191.0.0/16"
  ]
  target_tags = ["gke-node-pool"] # GKE node pool will have this tag

  allow {
    protocol = "tcp"
    ports    = ["10250", "30000-32767"] # Kubelet port, NodePort range for services
  }
  description = "Allow Google Load Balancer health checks to GKE nodes."
}

# Rule to allow traffic from ALB proxy to GKE backend services
resource "google_compute_firewall" "allow_alb_to_gke" {
  name    = "allow-alb-to-gke"
  project = var.project_id
  network = google_compute_network.agfs_core_vpc.name
  direction = "INGRESS"
  priority = 990 # Higher priority than default

  source_ranges = [
    var.subnet_ingress_cidr # Proxy-only subnet IP range
  ]
  target_tags = ["gke-node-pool"]

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080", "8443", "30000-32767"] # Common service ports and NodePort range
  }
  description = "Allow traffic from ALB proxy-only subnet to GKE node ports."
}

# Rule to allow GKE control plane to node communication (kubelet)
# This is often handled by GKE's auto-created firewalls but good to be explicit for private clusters
resource "google_compute_firewall" "allow_gke_control_plane" {
  name    = "allow-gke-control-plane"
  project = var.project_id
  network = google_compute_network.agfs_core_vpc.name
  direction = "INGRESS"
  priority = 980

  # Source ranges will be GKE master IPs or GKE internal control plane ranges
  # For private clusters, this is usually the master IP range provided by GKE
  # For simplicity, we allow from the workload subnet where GKE master could communicate
  # GKE usually manages this rule. This is a placeholder or for custom setups.
  source_ranges = [var.subnet_workload_cidr] # Master authorized networks will also need access
  target_tags = ["gke-node-pool"]

  allow {
    protocol = "tcp"
    ports    = ["10250"] # Kubelet
  }
  description = "Allow GKE control plane to node communication (kubelet)."
}

# Rule to allow internal Pod-to-Pod communication within GKE (further refined by Network Policies)
resource "google_compute_firewall" "allow_internal_gke_pod_comm" {
  name    = "allow-internal-gke-pod-comm"
  project = var.project_id
  network = google_compute_network.agfs_core_vpc.name
  direction = "INGRESS"
  priority = 970

  source_ranges = [
    var.gke_pods_secondary_cidr,
    var.gke_services_secondary_cidr # Services CIDR might need to reach pods
  ]
  target_tags = ["gke-node-pool"] # Apply to GKE nodes where pods run

  allow {
    protocol = "all"
  }
  description = "Allow Pod-to-Pod communication within GKE cluster (broad, refined by NetPol)."
}

# Rule to allow egress to Private Services Access (PSA) peered networks
resource "google_compute_firewall" "allow_egress_psa" {
  name    = "allow-egress-psa"
  project = var.project_id
  network = google_compute_network.agfs_core_vpc.name
  direction = "EGRESS"
  priority = 1000 # Default

  destination_ranges = [google_compute_global_address.private_ip_alloc.address_with_prefix]
  target_tags        = ["gke-node-pool"] # Apply to GKE nodes and potentially pods

  allow {
    protocol = "all"
  }
  description = "Allow egress to Private Services Access (Cloud SQL, Memorystore)."
}

# Rule to allow egress to the internet via Cloud NAT for GKE nodes
resource "google_compute_firewall" "allow_egress_nat" {
  name    = "allow-egress-nat"
  project = var.project_id
  network = google_compute_network.agfs_core_vpc.name
  direction = "EGRESS"
  priority = 1010 # Lower priority than PSA, higher than default deny

  destination_ranges = ["0.0.0.0/0"]
  # Exclude internal VPC ranges from this rule if other specific internal egress rules exist
  # For simplicity, allowing 0.0.0.0/0 here, Cloud NAT will handle non-internal routes.
  target_tags = ["gke-node-pool"]

  allow {
    protocol = "all"
  }
  description = "Allow egress to the internet for GKE nodes via Cloud NAT."
}

# Rule to allow SSH to management subnet (bastion hosts) from trusted IPs
resource "google_compute_firewall" "allow_ingress_ssh_mgmt" {
  name    = "allow-ingress-ssh-mgmt"
  project = var.project_id
  network = google_compute_network.agfs_core_vpc.name
  direction = "INGRESS"
  priority = 900 # High priority

  source_ranges = var.trusted_management_cidrs
  destination_ranges = [var.subnet_mgmt_cidr] # Only target the management subnet

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  description = "Allow SSH to management subnet from trusted IPs."
}
```

---

#### 4. `security.tf`

```terraform
# security.tf

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
```

---

#### 5. `compute.tf` / `workload.tf`

```terraform
# compute.tf

# Enable necessary APIs
resource "google_project_service" "container_api" {
  project = var.project_id
  service = "container.googleapis.com"
  disable_on_destroy = false
}

# 1. Private GKE Cluster
resource "google_container_cluster" "agfs_gke_cluster" {
  name                     = "agfs-${var.environment}-gke-cluster"
  project                  = var.project_id
  location                 = var.region
  initial_node_count       = 1 # Managed by node pool, set to 1 for initial creation
  remove_default_node_pool = true
  network                  = google_compute_network.agfs_core_vpc.name
  subnetwork               = google_compute_subnetwork.sbn_workload.name
  logging_service          = "logging.googleapis.com/kubernetes"
  monitoring_service       = "monitoring.googleapis.com/kubernetes"
  # For regional clusters, specify all zones within the region for HA
  node_locations           = [for zone_suffix in ["a", "b", "c"] : "${var.region}-${zone_suffix}"] # Example zones

  # Private Cluster Configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = true # Access to control plane via private IP
    master_ipv4_cidr_block  = "172.16.0.0/28" # Example CIDR for master
    # Master authorized networks (from where control plane can be accessed)
    # Add your internal management CIDRs, or leave empty for full private endpoint control
    master_authorized_networks_config {
      cidr_blocks {
        display_name = "VPC Internal Access"
        cidr_block   = var.vpc_primary_cidr # Allow access from anywhere in the VPC
      }
      # Add corporate IP ranges if needed
      # cidr_blocks {
      #   display_name = "Corporate Network"
      #   cidr_block   = "YOUR_CORP_CIDR/XX"
      # }
    }
  }

  # IP Allocation Policy (using secondary ranges)
  ip_allocation_policy {
    cluster_secondary_range_name  = google_compute_subnetwork.sbn_workload.secondary_ip_range[0].range_name # gke-pods
    services_secondary_range_name = google_compute_subnetwork.sbn_workload.secondary_ip_range[1].range_name # gke-services
  }

  # Workload Identity Configuration
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Release Channel for automatic upgrades
  release_channel {
    channel = "REGULAR" # Stable and predictable updates
  }

  # Security Features
  enable_shielded_nodes = true # Cluster-wide default for new nodes
  # GKE Control Plane logging (Audit logs)
  cluster_autoscaling {
    enabled = true
  }

  # Disabling basic auth and client certificates
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  # Binary Authorization (optional but recommended for production)
  # binary_authorization {
  #   evaluation_mode = "PROJECT_SINGLETON"
  # }

  depends_on = [
    google_project_service.container_api,
    google_compute_subnetwork.sbn_workload
  ]
}

# 2. GKE Node Pool
resource "google_container_node_pool" "agfs_gke_node_pool" {
  name       = "agfs-${var.environment}-default-pool"
  project    = var.project_id
  location   = var.region
  cluster    = google_container_cluster.agfs_gke_cluster.name
  node_count = var.gke_node_count # Initial count

  version = var.gke_kubernetes_version

  node_config {
    machine_type = var.gke_machine_type
    disk_type    = "pd-ssd" # High performance SSD
    disk_size_gb = 100      # Sufficient disk size

    # Associate with dedicated service account
    service_account = google_service_account.gke_nodes_sa.email

    # Add network tag for firewall rules
    tags = ["gke-node-pool"]

    # Shielded GKE Nodes (VM integrity monitoring)
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # CMEK encryption for node boot disks
    disk_encryption_key {
      kms_key_self_link = google_kms_crypto_key.gke_pd_cmek.self_link
    }

    # Use preemptible nodes for non-critical workloads or batch jobs if applicable
    # preemptible = false
  }

  # Node pool autoscaling
  autoscaling {
    min_node_count = 3 # Minimum nodes, adjust based on baseline load
    max_node_count = 10 # Maximum nodes, adjust based on peak load estimates
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  depends_on = [
    google_container_cluster.agfs_gke_cluster,
    google_service_account.gke_nodes_sa
  ]
}
```

---

#### 6. `database.tf`

```terraform
# database.tf

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
```

---

#### 7. `outputs.tf`

```terraform
# outputs.tf

output "vpc_id" {
  description = "The ID of the VPC network."
  value       = google_compute_network.agfs_core_vpc.id
}

output "vpc_self_link" {
  description = "The self_link of the VPC network."
  value       = google_compute_network.agfs_core_vpc.self_link
}

output "subnet_ids" {
  description = "IDs of the created subnets."
  value = {
    ingress  = google_compute_subnetwork.sbn_ingress.id
    workload = google_compute_subnetwork.sbn_workload.id
    data     = google_compute_subnetwork.sbn_data.id
    mgmt     = google_compute_subnetwork.sbn_mgmt.id
  }
}

output "cluster_name" {
  description = "Name of the GKE cluster."
  value       = google_container_cluster.agfs_gke_cluster.name
}

output "cluster_endpoint" {
  description = "Endpoint of the GKE cluster master."
  value       = google_container_cluster.agfs_gke_cluster.endpoint
}

output "kms_key_ring_id" {
  description = "ID of the KMS Key Ring."
  value       = google_kms_key_ring.agfs_core_banking_kr.id
}

output "cloud_armor_policy_id" {
  description = "ID of the Cloud Armor Security Policy."
  value       = google_compute_security_policy.agfs_cloud_armor_policy.id
}

output "cloud_sql_instance_connection_name" {
  description = "Connection name for the Cloud SQL instance (for database clients)."
  value       = google_sql_database_instance.agfs_core_db.connection_name
}

output "cloud_sql_private_ip_address" {
  description = "Private IP address of the Cloud SQL instance."
  value       = google_sql_database_instance.agfs_core_db.private_ip_address
}

output "gke_app_service_account_email" {
  description = "Email of the GKE Application Service Account for Workload Identity."
  value       = google_service_account.gke_app_sa.email
}
```

---

#### 8. `terraform.tfvars.example`

```terraform
# terraform.tfvars.example
# Rename this file to terraform.tfvars and fill in your values.

project_id = "your-gcp-project-id" # REQUIRED: Replace with your actual GCP Project ID
region     = "us-central1"
environment = "prod"

# Example: Overriding default variable values if needed
# vpc_name = "agfs-production-vpc"
# gke_node_count = 5
# db_tier = "db-custom-8-32768" # Larger DB tier for production
# trusted_management_cidrs = ["203.0.113.0/24", "198.51.100.0/24"] # Your corporate IP ranges
```

---

#### 9. Execution & CI/CD Guide

**Local Execution Steps:**

1.  **GCP Authentication:** Ensure your `gcloud` CLI is configured and authenticated to your GCP project.
    ```bash
    gcloud auth application-default login
    gcloud config set project your-gcp-project-id
    ```
2.  **Initialize Terraform:** Navigate to the directory containing your Terraform files and initialize the backend and providers. **Before this, ensure you have created the GCS bucket specified in `versions.tf` (`agfs-terraform-state-bucket`) for remote state.**
    ```bash
    terraform init
    ```
3.  **Review the Plan:** Generate an execution plan and review the resources Terraform will create, modify, or destroy.
    ```bash
    terraform plan -out=tfplan
    ```
4.  **Apply the Configuration:** Apply the planned changes.
    ```bash
    terraform apply tfplan
    ```
5.  **Destroy (Optional):** To tear down all resources (use with extreme caution in production):
    ```bash
    terraform destroy
    ```

**CI/CD Pipeline Recommendations:**

*   **Version Control:** Store your Terraform code in a Git repository (e.g., GitHub, GitLab, Cloud Source Repositories).
*   **Pipeline Tool:** Use a CI/CD tool like GitHub Actions, GitLab CI/CD, Google Cloud Build, or Jenkins.
*   **Service Account:** The CI/CD pipeline should execute Terraform using a dedicated GCP Service Account (e.g., `agfs-prod-cicd-sa` defined in `security.tf`) with appropriate permissions (`roles/owner` or more granular custom roles for infrastructure management).
*   **Workflow:**
    *   **`terraform fmt`**: Run on every commit/PR to ensure consistent code formatting.
    *   **`terraform validate`**: Run on every commit/PR to check syntax and configuration.
    *   **`terraform plan`**: Run on pull requests to show proposed changes before merging. Attach the plan output as a comment to the PR.
    *   **`terraform apply`**: Triggered on merge to `main`/`master` branch (or specific deployment branches). Often requires manual approval for production environments.
*   **State Locking:** GCS backend automatically provides state locking, preventing concurrent `terraform apply` operations from corrupting the state file.
*   **Secrets Management:** Avoid hardcoding sensitive values in `terraform.tfvars`. Instead, inject them as environment variables into the CI/CD pipeline, or fetch them from a secure vault (e.g., Google Secret Manager, HashiCorp Vault) during pipeline execution.
*   **Environment-Specific Deployments:** Use different `terraform.tfvars` files (or directories with `terraform workspace`) for `dev`, `staging`, and `prod` environments to manage environment-specific configurations.

---