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
