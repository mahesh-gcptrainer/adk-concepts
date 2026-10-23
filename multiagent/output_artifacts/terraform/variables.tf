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
