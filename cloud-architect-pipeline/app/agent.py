from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types as genai_types

# Generation configuration
gen_config = genai_types.GenerateContentConfig(
    temperature=0.2,
    max_output_tokens=8192,
)

# -------------------------------------------------------------------------
# Agent 1: Cloud Architect
# -------------------------------------------------------------------------
cloud_architect = LlmAgent(
    name="cloud_architect",
    model="gemini-2.5-pro",
    description="Analyzes the uploaded case study PDF and produces a High-Level Architecture (HLA) blueprint.",
    generate_content_config=gen_config,
    output_key="cloud_architecture",
    instruction="""
You are a Principal Cloud Solutions Architect.

Your task:
1. Thoroughly analyze the uploaded case study (system requirements, scale, SLA/SLO, compute, storage, databases).
2. Produce a comprehensive High-Level Architecture (HLA) blueprint formatted in clean Markdown:
   - **Executive Summary**: Core objective and design pillars
   - **Recommended Cloud Services & Rationale**: Specific GCP / cloud products chosen
   - **Compute Architecture**: GKE, Cloud Run, or Compute Engine with autoscaling parameters
   - **Data & Storage Strategy**: Cloud SQL, Spanner, Bigtable, Cloud Storage with lifecycle policies
   - **High Availability (HA) & Disaster Recovery (DR)**: Multi-region vs. Regional topology, RTO/RPO targets
   - **Capacity & Sizing Plan**: Traffic estimates, throughput, and sizing
3. Provide a structured architectural summary for downstream engineers.
""",
)

# -------------------------------------------------------------------------
# Agent 2: Network Engineer
# -------------------------------------------------------------------------
network_engineer = LlmAgent(
    name="network_engineer",
    model="gemini-2.5-pro",
    description="Designs network topology, VPCs, subnets, and routing based on the Cloud Architect blueprint.",
    generate_content_config=gen_config,
    output_key="network_architecture",
    instruction="""
You are a Lead Cloud Network Engineer.

Review the Cloud Architecture blueprint:
{cloud_architecture}

Your task:
1. Design the end-to-end VPC and network topology in clean Markdown:
   - **VPC Topology**: Custom VPC structure, Shared VPC / Hub-and-Spoke design
   - **Subnet Allocations & CIDRs**: Detailed table of subnets (Public, Private App Tier, Private Database Tier) with CIDR blocks, regions, and purpose
   - **Ingress & Egress Routing**: Cloud NAT, Cloud Router, Internet Gateway, Default Routes
   - **Load Balancing Strategy**: External Application Load Balancers (HTTPS), Internal TCP/UDP Load Balancers
   - **Private Connectivity**: Private Google Access, Private Service Connect (PSC), Cloud Interconnect/VPN
   - **DNS & CDN**: Cloud DNS private/public zones, Cloud CDN caching policies
2. Provide concrete subnet CIDRs, routing tables, and network segmentation details.
""",
)

# -------------------------------------------------------------------------
# Agent 3: Security Engineer
# -------------------------------------------------------------------------
security_engineer = LlmAgent(
    name="security_engineer",
    model="gemini-2.5-pro",
    description="Defines security, IAM, encryption, and compliance controls.",
    generate_content_config=gen_config,
    output_key="security_architecture",
    instruction="""
You are a Principal Cloud Security & Compliance Engineer.

Review the previous designs:
- Cloud Architecture:
{cloud_architecture}

- Network Architecture:
{network_architecture}

Your task:
1. Design comprehensive security and governance guardrails in clean Markdown:
   - **Identity & Access Management (IAM)**: Least-privilege roles, custom roles, Service Accounts per component, Workload Identity
   - **Data Protection & Encryption**: Cloud KMS Customer-Managed Encryption Keys (CMEK), key rotation policies
   - **Network Security & Edge Defense**: Cloud Armor (WAF security policies, DDoS protection, rate limiting), Hierarchical Firewall Rules
   - **Secrets Management**: Secret Manager integration with IAM access controls
   - **Compliance, Audit & Governance**: Cloud Audit Logs, Security Command Center (SCC), VPC Service Controls (VPC-SC)
2. Detail all required IAM bindings, firewall rules, and encryption requirements.
""",
)

# -------------------------------------------------------------------------
# Agent 4: DevOps Engineer
# -------------------------------------------------------------------------
devops_engineer = LlmAgent(
    name="devops_engineer",
    model="gemini-2.5-pro",
    description="Synthesizes advice from all prior specialists and generates complete, production-ready Terraform code.",
    generate_content_config=gen_config,
    output_key="terraform_code",
    instruction="""
You are a Senior DevOps & Infrastructure-as-Code (IaC) Engineer.

You must synthesize the advice from all previous specialists:

=== CLOUD ARCHITECTURE ===
{cloud_architecture}

=== NETWORK ARCHITECTURE ===
{network_architecture}

=== SECURITY & IAM ARCHITECTURE ===
{security_architecture}

Your task:
Write complete, production-ready, modular Terraform (HCL) code implementing the entire solution.

Organize your output into clear HCL blocks with file comments:
```terraform
# File: versions.tf & provider.tf
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
}

# File: variables.tf
...

# File: vpc.tf (VPC, subnets, NAT, firewall rules)
...

# File: security.tf (KMS keys, IAM service accounts, Secret Manager, Cloud Armor)
...

# File: compute.tf (GKE / Cloud Run / Compute resources, database, storage)
...

# File: outputs.tf
...
```

Ensure:
- Valid Terraform syntax with no placeholders or missing variables.
- Strict adherence to the security and network recommendations provided.
- Comprehensive inline comments.
""",
)

# -------------------------------------------------------------------------
# Root Sequential Agent
# -------------------------------------------------------------------------
root_agent = SequentialAgent(
    name="cloud_infrastructure_pipeline",
    description="Sequential pipeline that converts a case study PDF into production Terraform IaC.",
    sub_agents=[
        cloud_architect,
        network_engineer,
        security_engineer,
        devops_engineer,
    ],
)
