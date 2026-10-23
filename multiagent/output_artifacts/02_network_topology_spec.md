The following network topology, IP addressing, and connectivity architecture are designed based on the Apex Global Financial Services Cloud Architecture Blueprint, ensuring high availability, robust security, and compliance.

---

### Network Topology, IP Addressing, and Connectivity Architecture for Apex Global Financial Services

**1. Network Architecture Overview & Topology Description**

The core banking and payment modernization initiative will be deployed within a **Single Custom Mode Virtual Private Cloud (VPC)**, named `agfs-core-vpc`, within a primary GCP region (e.g., `us-central1`). This approach provides granular control over IP addressing and network segmentation, aligning with the "Zero-Trust" security posture.

The VPC will be logically segmented into dedicated subnets to isolate different tiers of the application:
*   **Ingress Subnet:** Hosts the proxy-only subnets for the Global External HTTP(S) Load Balancer.
*   **Workload Subnet:** Dedicated for Google Kubernetes Engine (GKE) nodes, including secondary IP ranges for Pods and Services.
*   **Data/Persistence Subnet:** A logical subnet for potential future persistence-related client VMs or to maintain network segmentation, though primary Cloud SQL/Memorystore access is via Private Service Access (PSA).
*   **Management Subnet:** For administrative jump hosts (bastions) and management tools.

**Key Connectivity Flows:**
1.  **External Ingress:** Client requests enter via a Global External HTTP(S) Application Load Balancer, which terminates TLS 1.3, applies Cloud Armor WAF policies, and routes traffic to GKE services via Network Endpoint Groups (NEGs).
2.  **Internal GKE Communication:** Microservices within GKE communicate using Kubernetes' native service discovery (ClusterIP).
3.  **Managed Services Access:** GKE microservices access Cloud SQL for PostgreSQL and Memorystore Redis via **Private Services Access (PSA)**, which establishes a private peering connection to Google's service networking VPC.
4.  **Google API Access:** All subnets are configured with **Private Google Access (PGA)**, allowing resources with private IPs to securely access Google services (Cloud Storage, Pub/Sub, Cloud KMS, etc.) without public IPs or NAT, utilizing Google's internal network.
5.  **External Egress:** Outbound internet access for GKE nodes/pods (e.g., for OS updates, external APIs) is routed through a regional **Cloud NAT Gateway**, configured with Cloud Router, ensuring no public IPs are assigned to compute instances.
6.  **Management Access:** Secure administrative access is facilitated via bastion hosts in the Management Subnet, accessed via VPN or Cloud Interconnect from corporate networks (if hybrid connectivity was in scope).

**Topology Visualization (Conceptual Description):**

```
Internet
    |
    | (HTTPS/TLS 1.3)
    V
[Global External HTTP(S) Load Balancer]
  - Public IP, TLS termination, Cloud Armor WAF, URL Map
    |
    | (Private IP via Proxy-only Subnet)
    V
[GCP VPC: agfs-core-vpc (Region: us-central1)]
    +------------------------------------------------------------------------------------------------+
    |                                                                                                |
    |   Subnet: sbn-us-central1-ingress (10.0.0.0/24)                                                |
    |   [Proxy-only subnet for ALB]                                                                  |
    |                                                                                                |
    |   Subnet: sbn-us-central1-workload (10.0.1.0/20)                                               |
    |   [GKE Cluster Nodes]                                                                          |
    |     - Secondary IP Ranges: Pods (10.10.0.0/16), Services (10.20.0.0/20)                        |
    |     - Microservices (Account, Ledger, Payment Gateway)                                         |
    |     - Workload Identity Enabled                                                                |
    |     |                                                                                          |
    |     +-----> [Cloud NAT Gateway] (Public Egress IPs) -------> Internet (for OS updates, external APIs)
    |     |                                                                                          |
    |     +-----> [Private Google Access (PGA)] -----------------> Google Services (Cloud Storage, Pub/Sub, KMS)
    |     |                                                                                          |
    |     +-----> [Private Service Access (PSA) Peering: 10.250.0.0/16]                              |
    |                                                                                                |
    |   Subnet: sbn-us-central1-data (10.0.2.0/24)                                                   |
    |   [Persistence Client Access / Future Data Services]                                           |
    |                                                                                                |
    |   Subnet: sbn-us-central1-mgmt (10.0.3.0/28)                                                   |
    |   [Bastion Hosts / Management Tools]                                                           |
    |                                                                                                |
    +------------------------------------------------------------------------------------------------+
                                       |
                                       | (via PSA Peering 10.250.0.0/16)
                                       V
                       [Google Managed Services VPC]
                          |           |
                          V           V
                     [Cloud SQL PostgreSQL]  [Memorystore Redis]
                       (Private IP)          (Private IP)
```

**2. Complete Subnet Allocation & CIDR IP Addressing Table**

**GCP Project:** `agfs-core-banking-prod` (example)
**GCP Region:** `us-central1` (example: Iowa)
**VPC Network Name:** `agfs-core-vpc`
**VPC Primary CIDR Range:** `10.0.0.0/16`

| Component Category                | Subnet Name                 | Region/Zones   | Primary IP Range   | Secondary IP Ranges (GKE)                                | Purpose                                                                             | Private Google Access |
| :-------------------------------- | :-------------------------- | :------------- | :----------------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------- | :-------------------- |
| **VPC Custom Mode Subnets**       |                             |                |                    |                                                          |                                                                                     |                       |
| Ingress / Proxy                   | `sbn-us-central1-ingress`   | `us-central1`  | `10.0.0.0/24`      | N/A                                                      | Global External HTTP(S) Load Balancer Proxy-only Subnet                             | Enabled               |
| GKE Workload Nodes                | `sbn-us-central1-workload`  | `us-central1`  | `10.0.1.0/20`      | `gke-pods: 10.10.0.0/16` <br> `gke-services: 10.20.0.0/20` | GKE nodes, Pods, and Services for microservices (Account, Ledger, Payment Gateway) | Enabled               |
| Persistence (Client Access)       | `sbn-us-central1-data`      | `us-central1`  | `10.0.2.0/24`      | N/A                                                      | Future persistence-related VMs, data processing clients, or network appliances      | Enabled               |
| Management / Bastion              | `sbn-us-central1-mgmt`      | `us-central1`  | `10.0.3.0/28`      | N/A                                                      | Administrative access, jump hosts, monitoring agents                                | Enabled               |
| **Reserved for Private Services Access (PSA)** | `agfs-core-psa-range`       | N/A            | `10.250.0.0/16`    | N/A                                                      | Dedicated IP range for Google-managed services (Cloud SQL, Memorystore) peering     | N/A                   |
| **Cloud NAT Egress IPs**          | `agfs-core-nat-external-ips` | `us-central1`  | (Public IP pool)   | N/A                                                      | Pool of static public IP addresses for outbound internet access from `agfs-core-vpc` | N/A                   |

**Rationale for CIDR Sizes:**
*   `/16` for VPC provides a large address space for future expansion.
*   `/24` for Ingress proxy-only subnet is standard practice.
*   `/20` for GKE nodes supports over 4,000 nodes, sufficient for expected high transaction volumes and future scaling.
*   `/16` for GKE Pods (65,536 IPs) ensures ample capacity for high pod density across multiple node pools and services.
*   `/20` for GKE Services (4,096 IPs) allows for a large number of internal Kubernetes services.
*   `/24` for data and `/28` for management provide adequate, segmented capacity.
*   `/16` for PSA is a recommended practice to avoid IP exhaustion when integrating with various managed services over time.

**3. Ingress, Egress, and Load Balancing Design**

*   **Ingress Traffic (External):**
    *   **Global External HTTP(S) Application Load Balancer:** This will be the primary entry point for all external client traffic.
        *   **Frontend:** Configured with a static global public IP address, a Google-managed SSL certificate, and an SSL Policy enforcing TLS 1.3 for secure communication.
        *   **URL Map:** Routes incoming requests based on host headers or URL paths (e.g., `/payment/*`, `/account/*`) to the appropriate backend services.
        *   **Backend Services:** Target GKE Kubernetes Services exposed via Ingress resources. These services leverage **Container Native Load Balancing (CNLB)** via **Network Endpoint Groups (NEGs)**, ensuring efficient load distribution directly to Pod IPs.
        *   **Health Checks:** Robust health checks are configured for backend services to ensure traffic is only sent to healthy GKE pods.
        *   **Security:** **Google Cloud Armor** will be integrated with the load balancer to provide Web Application Firewall (WAF) capabilities (OWASP Top 10 protection, SQLi, XSS) and sophisticated rate-limiting policies to protect against DDoS and application-layer attacks.
*   **Internal Traffic (Microservice-to-Microservice):**
    *   **Kubernetes Service Discovery (ClusterIP):** Within the GKE cluster, microservices will communicate using Kubernetes `ClusterIP` services, leveraging GKE's built-in CoreDNS for efficient, low-latency service discovery and routing.
    *   **Internal Load Balancers (Optional/Future):** If complex L7 routing between GKE clusters or to non-GKE internal services becomes necessary, Internal HTTP(S) Load Balancers could be deployed. However, for the described microservices on a single GKE cluster, `ClusterIP` is generally sufficient.
*   **Egress Traffic (Outbound):**
    *   **Cloud NAT Gateway:** A regional Cloud NAT Gateway will be configured in `us-central1` to provide secure, non-public internet egress for GKE nodes and pods within the `agfs-core-vpc`. A pool of static public IP addresses will be assigned to the NAT Gateway. This ensures GKE instances do not require public IPs for outbound internet access (e.g., pulling container images from public registries, OS updates, third-party API calls).
    *   **Cloud Router:** Implicitly used for the NAT Gateway configuration and forms the foundation for dynamic routing within the VPC, even without explicit hybrid connectivity.
    *   **Private Google Access (PGA):** Enabled on all core subnets (`sbn-us-central1-ingress`, `sbn-us-central1-workload`, `sbn-us-central1-data`, `sbn-us-central1-mgmt`). This allows GKE workloads and other instances to reach Google API endpoints (e.g., Cloud Storage, Pub/Sub, Cloud KMS, Artifact Registry) via Google's internal network, preventing outbound traffic from traversing the internet or consuming NAT bandwidth.

**4. Private Connectivity (PGA, PSC, PSA) & Hybrid Routing**

*   **Private Google Access (PGA):**
    *   **Configuration:** PGA will be enabled on all relevant subnets within `agfs-core-vpc`.
    *   **Benefit:** Allows GKE nodes, pods, and any other VMs with private IP addresses to securely access Google services (e.g., Cloud Storage, Cloud Pub/Sub, Cloud Logging, Cloud Monitoring, Artifact Registry, Cloud KMS) using internal Google IP addresses instead of public internet paths. This is a critical component of the Zero-Trust security model.
*   **Private Services Access (PSA):**
    *   **Reserved IP Range:** The `10.250.0.0/16` CIDR range (`agfs-core-psa-range`) within `agfs-core-vpc` will be exclusively reserved for Private Services Access.
    *   **VPC Network Peering:** A VPC Network Peering connection will be established between `agfs-core-vpc` and Google's `servicenetworking` VPC. This enables private IP connectivity to Google-managed services.
    *   **Service Integration:** Cloud SQL for PostgreSQL and Memorystore Redis instances will be deployed with private IP connectivity, utilizing this PSA peering to allow GKE microservices to access them securely using private IP addresses.
*   **Hybrid Access / On-premises Connectivity:**
    *   The provided blueprint does not explicitly state a requirement for hybrid connectivity to on-premises data centers. Therefore, **Cloud VPN (HA VPN) or Cloud Interconnect is not included in the initial scope of this network design.**
    *   **Future Consideration:** Should Apex Global Financial Services require secure, low-latency connectivity to its on-premises infrastructure, HA VPN (with dynamic BGP routing via Cloud Router) or Cloud Interconnect (Partner or Dedicated) would be implemented, connecting to `agfs-core-vpc`. This would require reserving additional IP ranges within the VPC (e.g., for VPN tunnels, Cloud Router interfaces) and potentially configuring Cloud DNS forwarding.

**5. Firewall Policies & Segmentation**

A strict **default-deny security posture** will be enforced for both ingress and egress traffic at the VPC firewall level, followed by highly granular allow rules.

**GCP VPC Firewall Rules:**

| Rule Name                      | Direction | Action | Source Filters                                    | Destination Filters              | Protocols/Ports | Target (Service Account/Tags)                                 | Description                                                                     |
| :----------------------------- | :-------- | :----- | :------------------------------------------------ | :------------------------------- | :-------------- | :------------------------------------------------------------ | :------------------------------------------------------------------------------ |
| `allow-ingress-ssh-mgmt`       | INGRESS   | ALLOW  | `<Corporate-VPN-IPs>/32` (or similar trusted source) | `10.0.3.0/28` (sbn-us-central1-mgmt) | TCP:22          | `agfs-mgmt-bastion`                                           | Allow SSH to bastion hosts from trusted IPs.                                    |
| `allow-ingress-lb-health-check` | INGRESS   | ALLOW  | `35.191.0.0/16`, `130.211.0.0/22`                  | `agfs-gke-nodes` (network tag)   | TCP:`<NodePortRange>` | `agfs-gke-nodes`                                              | Allow Google Load Balancer health checks to GKE nodes.                          |
| `allow-ingress-alb-to-gke`     | INGRESS   | ALLOW  | `10.0.0.0/24` (sbn-us-central1-ingress)            | `agfs-gke-nodes` (network tag)   | TCP:`<NodePortRange>` | `agfs-gke-nodes`                                              | Allow traffic from ALB proxy to GKE backend services.                           |
| `allow-internal-gke-control`   | INGRESS   | ALLOW  | `10.0.1.0/20` (sbn-us-central1-workload)          | `agfs-gke-nodes`                 | TCP:10250       | `agfs-gke-nodes`                                              | Allow GKE control plane to node communication (e.g., kubelet).                  |
| `allow-internal-pod-to-pod`    | INGRESS   | ALLOW  | `10.10.0.0/16` (gke-pods secondary)                | `10.10.0.0/16`                   | ALL             | `agfs-gke-pods`                                               | Allow Pod-to-Pod communication within the GKE cluster. (Refined by NetPol)      |
| `allow-egress-psa`             | EGRESS    | ALLOW  | `10.0.0.0/16` (agfs-core-vpc)                      | `10.250.0.0/16` (agfs-core-psa-range) | ALL             | `agfs-gke-nodes`, `agfs-gke-pods` (or broader if needed)      | Allow egress to PSA-peered managed services (Cloud SQL, Memorystore).           |
| `allow-egress-nat`             | EGRESS    | ALLOW  | `10.0.0.0/16` (agfs-core-vpc)                      | `0.0.0.0/0` (excluding internal) | ALL             | `agfs-gke-nodes`                                              | Allow all compute instances egress to the internet via Cloud NAT.               |
| `deny-all-ingress`             | INGRESS   | DENY   | `0.0.0.0/0`                                        | `0.0.0.0/0`                      | ALL             | ALL (lowest priority)                                         | Default deny all ingress traffic not explicitly allowed.                        |
| `deny-all-egress`              | EGRESS    | DENY   | `0.0.0.0/0`                                        | `0.0.0.0/0`                      | ALL             | ALL (lowest priority)                                         | Default deny all egress traffic not explicitly allowed.                         |

*   **GKE Network Policies:** For fine-grained, Zero-Trust control *within* the GKE cluster, Kubernetes Network Policies will be deployed. These policies will control ingress and egress at the pod level, specifying which microservices can communicate with each other (e.g., `Payment Gateway` can talk to `Ledger Service` and `Account Service`, but not directly to fraud analytics backend unless explicitly permitted). This enhances security beyond VPC firewall rules.
*   **Service Accounts & Network Tags:** Firewall rules will heavily utilize GCP Service Accounts (e.g., `agfs-gke-nodes-sa`, `agfs-mgmt-bastion-sa`) and network tags (e.g., `agfs-gke-nodes`) for precise targeting, reducing the risk of misconfigurations and improving maintainability.

**6. Cloud DNS & Name Resolution Architecture**

The DNS architecture will ensure reliable and secure name resolution for both internal and external services.

*   **Private Managed DNS Zones (Cloud DNS):**
    *   **`agfs-core-internal.net`:** A private managed zone will be created in Cloud DNS, visible only within `agfs-core-vpc`. This zone will host custom A records for internal resources not directly managed by Kubernetes (e.g., bastion hosts, any future internal load balancers, or management tools).
*   **GKE Internal DNS (CoreDNS):**
    *   **Automatic Resolution:** GKE clusters use CoreDNS (or kube-dns) to provide service discovery within the cluster. Kubernetes Services (e.g., `account-service.default.svc.cluster.local`) will be automatically resolvable by pods within the GKE cluster.
*   **Private Services Access (PSA) DNS Integration:**
    *   **Automatic Resolution:** When Cloud SQL and Memorystore instances are provisioned with private IP connectivity via PSA, Google Cloud automatically registers their internal DNS hostnames in a peered DNS zone, making them resolvable by instances within `agfs-core-vpc` without additional manual configuration.
*   **Private Google Access (PGA) DNS Behavior:**
    *   Resources configured with PGA will resolve Google API public endpoints (e.g., `storage.googleapis.com`, `pubsub.googleapis.com`) to special internal IP addresses (e.g., `199.36.153.4/30` or `199.36.153.8/30`), directing traffic over Google's internal network rather than the public internet.
*   **External DNS:** For resolving public internet domains, the standard Google Public DNS resolvers will be used by default.
*   **No Split-Horizon DNS:** As hybrid connectivity is not in scope for the initial deployment, a complex split-horizon DNS setup is not required. If on-premises integration is added later, Cloud DNS forwarding policies could be configured to route queries for on-premises domains to corporate DNS servers.

---