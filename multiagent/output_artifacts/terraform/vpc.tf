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
