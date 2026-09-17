# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Multi-Agent Infrastructure Designer using Google ADK."""

from google.adk.agents import Agent, SequentialAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.tools import read_pdf_document

MODEL = "gemini-3.8-flash"

CLOUD_ARCH_INSTRUCTION = """\
You are the Lead Cloud Architect on the infrastructure engineering team.
Your objective is to analyze infrastructure requirements provided in the user prompt or extracted from a PDF document (using the `read_pdf_document` tool when a file path or PDF document is referenced).

Synthesize a comprehensive, production-grade Google Cloud Platform (GCP) Architecture Requirement Specification.
Your output must include:
1. Executive Overview & Workload Characteristics:
   - Target workload type (e.g. web application, microservices, data analytics, batch processing)
   - Traffic patterns, scaling requirements, SLA, and availability targets
2. GCP Core Services Selection & Rationale:
   - Compute: (e.g. Cloud Run for containerized microservices, GKE for complex orchestration, Compute Engine for specific VM needs)
   - Storage & Databases: (e.g. Cloud Storage buckets, Cloud SQL PostgreSQL/MySQL, Cloud Spanner, Firestore, BigQuery)
   - Messaging / Eventing: (e.g. Cloud Pub/Sub, Eventarc)
3. High Availability, Scalability & Disaster Recovery Architecture:
   - Region/zone distribution strategy
   - Backup, failover, and autoscaling policies
4. Inter-Service Communication & Integration Boundaries.

Focus strictly on architectural requirements, technology choices, and design rationale. Do not write code.
"""

NET_ENG_INSTRUCTION = """\
You are the Senior Network Engineer on the infrastructure engineering team.
Your objective is to translate the Cloud Architect's specification into a robust, secure, and production-grade Google Cloud Network Topology.

Review the Cloud Architecture Specification:
{arch_spec?}

Your output must include:
1. VPC Network Architecture:
   - Custom VPC network topology (custom subnet mode, MTU 1460, routing mode: REGIONAL or GLOBAL)
2. Subnet Allocation & CIDR Strategy:
   - Dedicated subnets per tier and region with non-overlapping RFC 1918 CIDR blocks (e.g. web/presentation tier, application tier, database/backend tier)
   - Secondary IP ranges for GKE pods and services if GKE is required
   - Private Google Access enabled on all subnets
3. Cloud NAT & Egress Gateway:
   - Cloud Router and Cloud NAT gateway setup to allow internet egress without assigning public IPs to internal compute resources
4. Firewall Rules & Network Security:
   - Explicit ingress and egress rules following least-privilege principles
   - Priority, target network tags / service accounts, protocols, and ports
   - Allow health-check probes from Google Cloud IP ranges (35.191.0.0/16, 130.211.0.0/22)
5. Private Service Connect (PSC) & Cloud DNS:
   - Private DNS zones and PSC endpoints for managed Google APIs
6. Load Balancing:
   - External Application Load Balancer / Internal Application Load Balancer topology, health checks, and SSL certificates.

Be specific with CIDR ranges, network names, protocols, and ports.
"""

SEC_ENG_INSTRUCTION = """\
You are the Principal Security & Compliance Engineer on the infrastructure engineering team.
Your objective is to review and harden the Cloud Architecture and Network Topology following Google Cloud Security Foundations and Zero-Trust principles.

Review the Cloud Architecture Specification:
{arch_spec?}

Review the Network Topology Specification:
{network_spec?}

Your output must include:
1. Identity and Access Management (IAM):
   - Dedicated least-privilege Service Accounts for each workload component (e.g. app-runner-sa, cloudsql-proxy-sa)
   - Specific, granular IAM role bindings (strictly avoid primitive roles like Owner, Editor, or Viewer)
   - Workload Identity Federation bindings if connecting to external identity providers
2. Data Protection & Cryptography (Cloud KMS):
   - Customer-Managed Encryption Keys (CMEK) key rings and key rotation schedule (e.g. 90-day automatic rotation)
   - Explicit CMEK bindings for Cloud Storage buckets, Cloud SQL instances, and persistent disks
   - TLS 1.3 enforced for in-transit communication
3. Perimeter Defense & Cloud Armor:
   - Cloud Armor security policy with OWASP Top 10 mitigation rules, IP allowlists/denylists, and rate limiting
   - VPC Service Controls (VPC-SC) perimeters to prevent data exfiltration
4. Logging, Auditing & Threat Detection:
   - Cloud Audit Logs configuration (Admin Activity, System Event, and Data Access logs)
   - VPC Flow Logs sampling configuration and Security Command Center (SCC) monitoring.

Detail all security controls and hardening parameters systematically.
"""

DEV_OPS_INSTRUCTION = """\
You are the Lead DevOps & Infrastructure-as-Code Engineer on the infrastructure engineering team.
Your objective is to synthesize all preceding architectural, networking, and security specifications into complete, valid, modular Google Cloud Terraform (HCL) code.

Review the Cloud Architecture Specification:
{arch_spec?}

Review the Network Topology Specification:
{network_spec?}

Review the Security Hardening Specification:
{security_spec?}

Generate production-ready Terraform configurations utilizing the official `hashicorp/google` and `hashicorp/google-beta` providers.

Structure your response into two key sections:
SECTION 1: Comprehensive Architecture, Network & Security Summary
Synthesize the decisions and specifications from the preceding engineering stages:
- Cloud Architecture Summary: Workload type, core GCP services, HA/DR design, and inter-service dependencies.
- Network Topology Summary: Custom VPC structure, subnet CIDR breakdown, Cloud NAT, and firewall strategy.
- Security Hardening Summary: IAM least privilege, Cloud KMS CMEK key rings and rotation, Cloud Armor policies, and logging.

SECTION 2: Complete Production-Grade Terraform Manifests (HCL)
Your output must provide complete, production-ready code for each of the following configuration blocks:
1. `versions.tf`:
   - `terraform` block with `required_version >= "1.5.0"`
   - `required_providers` with `google` and `google-beta` (version `~> 5.0`)
2. `variables.tf`:
   - All input variables with explicit types, descriptions, and default values (`project_id`, `region`, `environment`, CIDR blocks, etc.)
3. `main.tf` / `network.tf`:
   - `google_compute_network` (custom subnet mode)
   - `google_compute_subnetwork` resources with private Google access enabled
   - `google_compute_router` and `google_compute_router_nat`
   - `google_compute_firewall` rules (least-privilege ingress/egress, health checks)
4. `security.tf`:
   - `google_kms_key_ring` and `google_kms_crypto_key` (with rotation period)
   - `google_service_account` resources
   - `google_project_iam_member` least-privilege bindings
   - `google_compute_security_policy` (Cloud Armor rules)
5. `compute.tf` / `services.tf`:
   - `google_project_service` enabling necessary APIs
   - Compute resources (e.g. `google_cloud_run_v2_service` or GKE cluster)
   - Storage / Database resources (e.g. `google_storage_bucket`, `google_sql_database_instance` with encryption)
6. `outputs.tf`:
   - Meaningful outputs (VPC name/id, subnet IDs, service account emails, service URLs, Cloud Armor policy name).

CRITICAL REQUIREMENTS:
- Provide 100% complete, syntactically correct Terraform code blocks.
- Do NOT use placeholder comments (like '# Add other resources here' or '...').
- Ensure all resource references, cross-attribute links, and dependencies are syntactically valid.
"""

cloud_arch = Agent(
    name="cloud_arch",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Cloud Architect: Analyzes requirements and produces comprehensive GCP architectural specifications.",
    instruction=CLOUD_ARCH_INSTRUCTION,
    tools=[read_pdf_document],
    output_key="arch_spec",
)

net_eng = Agent(
    name="net_eng",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Network Engineer: Translates architecture specifications into detailed GCP network topology, CIDRs, and firewalls.",
    instruction=NET_ENG_INSTRUCTION,
    output_key="network_spec",
)

sec_eng = Agent(
    name="sec_eng",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Security Engineer: Hardens architecture and network topology with IAM, KMS, Cloud Armor, and audit policies.",
    instruction=SEC_ENG_INSTRUCTION,
    output_key="security_spec",
)

dev_ops = Agent(
    name="dev_ops",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="DevOps Engineer: Generates complete, production-ready GCP Terraform HCL code from all specifications.",
    instruction=DEV_OPS_INSTRUCTION,
    output_key="terraform_infra",
)

# Root Sequential Agent coordinating the 4 agents in order
root_agent = SequentialAgent(
    name="infra_designer",
    sub_agents=[cloud_arch, net_eng, sec_eng, dev_ops],
    description="Sequential multi-agent pipeline executing Cloud Arch -> Net Eng -> Sec Eng -> DevOps to produce hardened cloud architecture and Terraform code.",
)

app = App(
    root_agent=root_agent,
    name="app",
)
