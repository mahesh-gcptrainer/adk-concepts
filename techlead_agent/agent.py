from google.adk import Agent
from pydantic import BaseModel, Field

# 1. Define Standard Tools
def extract_pdf_content(file_path: str) -> str:
    """Extracts text content from an uploaded case study PDF."""
    # In a real environment, you would integrate PyPDF2, pdfplumber, or the Gemini File API here.
    return "Simulated PDF Content: Client requires a highly available 3-tier web architecture with private networking, strict IAM controls, and infrastructure as code."

# 2. Define Pydantic Schemas for Structured Outputs
class TerraformPlan(BaseModel):
    main_tf: str = Field(description="The complete main.tf configuration")
    variables_tf: str = Field(description="The variables.tf configuration")
    summary: str = Field(description="A brief explanation of what the Terraform code provisions")

# 3. Define Sub-Agents
cloud_architect = Agent(
    name="cloud_architect",
    model="gemini-2.5-flash",
    mode="single_turn",
    instruction=(
        "You are a Cloud Architect. Analyze the provided case study text and design the core infrastructure. "
        "Recommend specific compute (e.g., GKE, Compute Engine), storage, and database services. "
        "Focus on scalability, high availability, and cost optimization. Return a clear design specification."
    )
)

network_engineer = Agent(
    name="network_engineer",
    model="gemini-2.5-flash",
    mode="single_turn",
    instruction=(
        "You are a Cloud Network Engineer. Analyze the provided case study text and design the network topology. "
        "Specify the VPC layout, subnets, IP CIDR ranges, load balancers, and routing strategies. "
        "Return a clear networking specification."
    )
)

security_engineer = Agent(
    name="security_engineer",
    model="gemini-2.5-flash",
    mode="single_turn",
    instruction=(
        "You are a Cloud Security Engineer. Analyze the provided case study text and define the security posture. "
        "Specify IAM roles, firewall rules (ingress/egress), encryption strategies (KMS), and VPC Service Controls. "
        "Return a strict security specification."
    )
)

devops_engineer = Agent(
    name="devops_engineer",
    model="gemini-2.5-flash",
    mode="task",
    instruction=(
        "You are a Cloud DevOps Engineer. Your task is to synthesize the design specifications provided by the "
        "Cloud Architect, Network Engineer, and Security Engineer. Translate their combined recommendations "
        "into production-ready Google Cloud Terraform code. Output ONLY valid Terraform code."
    )
)

# 4. Define Root Agent (Orchestrator)
root_agent = Agent(
    name="lead_solutions_architect",
    model="gemini-2.5-flash",
    tools=[extract_pdf_content],
    sub_agents=[
        cloud_architect, 
        network_engineer, 
        security_engineer, 
        devops_engineer
    ],
    instruction=(
        "You are the Lead Solutions Architect orchestrating an infrastructure design pipeline. "
        "When the user provides a case study PDF: "
        "1. Use the extract_pdf_content tool to read the document. "
        "2. Pass the extracted text to the cloud_architect, network_engineer, and security_engineer to get their designs. "
        "3. Collect their three design specifications and pass them all to the devops_engineer. "
        "4. Present the final Terraform plan to the user, alongside a brief executive summary of the architecture."
    )
)