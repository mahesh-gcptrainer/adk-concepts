"""Generates a realistic enterprise Case Study PDF for testing and demonstration."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_case_study_pdf(filename: str = "sample_case_study.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1a73e8"),
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#5f6368"),
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#202124"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#3c4043"),
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "BulletItem",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#3c4043"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("Enterprise Case Study: Core Banking & Payment Modernization", title_style))
    story.append(Paragraph("Customer: Apex Global Financial Services | Platform: Google Cloud Platform (GCP)", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a73e8"), spaceAfter=10))

    # Section 1: Executive Summary & Background
    story.append(Paragraph("1. Executive Summary & Current Challenges", heading_style))
    story.append(Paragraph(
        "Apex Global Financial Services is a tier-1 multinational banking institution providing retail "
        "and commercial banking, payment settlement, and real-time fraud monitoring to over 15 million customers. "
        "The bank currently operates a legacy monolithic core banking platform hosted across two aging on-premises "
        "data centers. During peak market opening hours and end-of-month reconciliation, transaction spikes cause "
        "severe latency degradations and periodic outages. The current manual disaster recovery process requires "
        "an unacceptably high 8-hour Recovery Time Objective (RTO).",
        body_style
    ))

    # Section 2: Business & Technical Objectives
    story.append(Paragraph("2. Strategic Business & Technical Objectives", heading_style))
    story.append(Paragraph("• <b>High Availability & SLA:</b> Target 99.99% system availability with automated regional multi-zone failover.", bullet_style))
    story.append(Paragraph("• <b>Disaster Recovery:</b> RTO < 15 minutes and RPO < 1 minute for all transactional ledger data.", bullet_style))
    story.append(Paragraph("• <b>Latency Targets:</b> Sub-50ms 95th percentile response times for all customer-facing payment APIs.", bullet_style))
    story.append(Paragraph("• <b>Elastic Scalability:</b> Seamlessly handle 10,000 transactions per second (TPS) during peak trading periods.", bullet_style))
    story.append(Paragraph("• <b>Zero-Trust Security:</b> Eliminate all public compute and database IPs; mandate end-to-end data encryption.", bullet_style))

    # Section 3: Key Architectural Requirements
    story.append(Paragraph("3. Core Workload & Infrastructure Specifications", heading_style))
    story.append(Paragraph(
        "The modernized cloud platform must be organized into decoupled, cloud-native services:",
        body_style
    ))
    story.append(Paragraph("• <b>Compute & Microservices:</b> Containerized microservices (Account Service, Ledger Service, Payment Gateway) running on private Google Kubernetes Engine (GKE) clusters with autoscaling and Shielded Nodes.", bullet_style))
    story.append(Paragraph("• <b>Relational Persistence:</b> Cloud SQL for PostgreSQL configured with Regional High Availability (multi-zone replication), automated point-in-time recovery, and private IP only.", bullet_style))
    story.append(Paragraph("• <b>In-Memory Caching:</b> Google Cloud Memorystore (Redis) for real-time account balance lookups and session state caching.", bullet_style))
    story.append(Paragraph("• <b>Event Streaming:</b> Google Cloud Pub/Sub for real-time asynchronous message publishing to fraud analytics and ledger audit pipelines.", bullet_style))
    story.append(Paragraph("• <b>Object Storage:</b> Cloud Storage buckets with uniform bucket-level access for statements, receipts, and regulatory reports.", bullet_style))

    # Section 4: Networking & Connectivity Requirements
    story.append(Paragraph("4. Network Topology & Connectivity Requirements", heading_style))
    story.append(Paragraph("• <b>VPC Isolation:</b> Dedicated Custom Mode VPC partitioned into Ingress, Workload, Database, and Management subnets.", bullet_style))
    story.append(Paragraph("• <b>Secondary CIDR Ranges:</b> Subnets must allocate dedicated secondary CIDR ranges for Kubernetes Pods and Services to prevent IP exhaustion.", bullet_style))
    story.append(Paragraph("• <b>Ingress & Load Balancing:</b> Global External HTTP(S) Application Load Balancer with TLS 1.3 termination, SSL policies, and URL map path routing.", bullet_style))
    story.append(Paragraph("• <b>Egress Control:</b> Cloud NAT with Cloud Router for private instances to safely pull external patches and API updates without public IPs.", bullet_style))
    story.append(Paragraph("• <b>Private Connectivity:</b> Private Google Access (PGA) on all subnets and Private Service Connect (PSC) for Google managed services.", bullet_style))

    # Section 5: Security & Compliance Requirements
    story.append(Paragraph("5. Security, Hardening & Regulatory Compliance", heading_style))
    story.append(Paragraph("• <b>Compliance Mandates:</b> Strict adherence to PCI-DSS 4.0, SOC 2 Type II, and the CIS GCP Foundations Benchmark v2.0.", bullet_style))
    story.append(Paragraph("• <b>Identity & Workload Identity:</b> GKE Workload Identity enabled; zero static service account keys in pods or VM disks.", bullet_style))
    story.append(Paragraph("• <b>Data Encryption:</b> Customer-Managed Encryption Keys (CMEK) managed via Cloud KMS with 90-day automatic key rotation for all disks, buckets, and databases.", bullet_style))
    story.append(Paragraph("• <b>Web Application Defense:</b> Google Cloud Armor attached to the external load balancer with pre-configured WAF rules against OWASP Top 10 (SQLi, XSS) and rate limiting.", bullet_style))
    story.append(Paragraph("• <b>Secrets Management:</b> Cloud Secret Manager for all database credentials, certificates, and API tokens.", bullet_style))
    story.append(Paragraph("• <b>Audit Logging:</b> Comprehensive Cloud Audit Logs (Admin Activity & Data Access) exported to BigQuery for security analytics.", bullet_style))

    # Section 6: Infrastructure as Code (DevOps) Requirements
    story.append(Paragraph("6. DevOps Automation & Delivery Requirements", heading_style))
    story.append(Paragraph(
        "All infrastructure must be declared and automated using Terraform (HCL) modular code. "
        "Configurations must be parameterized for environments (dev, staging, prod), use remote GCS backend "
        "state storage with state locking, and be ready for automated CI/CD pipeline deployment.",
        body_style
    ))

    doc.build(story)
    print(f"Sample case study PDF generated successfully: {filename}")
    return filename

if __name__ == "__main__":
    generate_case_study_pdf()
