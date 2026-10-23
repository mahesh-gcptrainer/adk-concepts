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
