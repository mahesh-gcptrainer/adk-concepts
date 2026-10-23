"""CLI runner to execute the Sequential Multi-Agent Cloud Infrastructure Pipeline."""

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import InMemoryRunner
from app.agent import root_agent
from app.tools.pdf_loader import load_pdf_as_adk_content

console = Console()

AGENT_TITLES = {
    "cloud_architect_agent": ("1/4", "Cloud Architect Agent", "cyan"),
    "network_engineer_agent": ("2/4", "Network Engineer Agent", "green"),
    "security_engineer_agent": ("3/4", "Security Engineering Agent", "yellow"),
    "devops_engineer_agent": ("4/4", "DevOps Engineering Agent", "magenta"),
}


def extract_terraform_files(terraform_text: str, output_dir: Path):
    """Parses code blocks from DevOps agent output and saves individual .tf files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_patterns = [
        ("versions.tf", r"```(?:hcl|terraform)?\s*(?:#\s*versions\.tf\b[\s\S]*?)?([\s\S]*?terraform\s*\{[\s\S]*?\})\s*```"),
        ("provider.tf", r"```(?:hcl|terraform)?\s*(#\s*provider\.tf[\s\S]*?)```"),
        ("variables.tf", r"```(?:hcl|terraform)?\s*(#\s*variables\.tf[\s\S]*?)```"),
        ("vpc.tf", r"```(?:hcl|terraform)?\s*(#\s*vpc\.tf[\s\S]*?)```"),
        ("security.tf", r"```(?:hcl|terraform)?\s*(#\s*security\.tf[\s\S]*?)```"),
        ("compute.tf", r"```(?:hcl|terraform)?\s*(#\s*compute\.tf[\s\S]*?)```"),
        ("database.tf", r"```(?:hcl|terraform)?\s*(#\s*database\.tf[\s\S]*?)```"),
        ("outputs.tf", r"```(?:hcl|terraform)?\s*(#\s*outputs\.tf[\s\S]*?)```"),
        ("terraform.tfvars.example", r"```(?:hcl|terraform)?\s*(#\s*terraform\.tfvars\.example[\s\S]*?)```"),
    ]

    # Generalized extraction based on header comments e.g. # versions.tf or filename in markdown
    regex = r"```(?:hcl|terraform)?\s*(?:#+\s*([a-zA-Z0-9_\-\.]+))?\n([\s\S]*?)```"
    matches = re.findall(regex, terraform_text)
    saved_files = []

    for name, content in matches:
        if name and (name.endswith(".tf") or name.endswith(".tfvars") or name.endswith(".example")):
            file_path = output_dir / name
            file_path.write_text(content.strip() + "\n", encoding="utf-8")
            saved_files.append(name)

    # Save full text as devops_complete.tf if no individual files were parsed
    full_tf_path = output_dir / "main.tf"
    full_tf_path.write_text(terraform_text, encoding="utf-8")
    return saved_files


async def run_pipeline(pdf_path: str, output_dir: str = "output_artifacts"):
    pdf_file = Path(pdf_path).resolve()
    if not pdf_file.exists():
        console.print(f"[bold red]Error:[/bold red] PDF file not found at: {pdf_file}")
        sys.exit(1)

    console.print(
        Panel.fit(
            f"[bold blue]Google Agent Development Kit (ADK)[/bold blue]\n"
            f"[bold white]Sequential Multi-Agent Infrastructure Pipeline[/bold white]\n"
            f"[dim]Input PDF:[/dim] [green]{pdf_file.name}[/green] ([dim]{pdf_file}[/dim])\n"
            f"[dim]Pipeline Flow:[/dim] Cloud Architect → Network Engineer → Security Engineer → DevOps Engineer",
            border_style="blue",
        )
    )

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Initialize ADK InMemoryRunner
    runner = InMemoryRunner(agent=root_agent, app_name="app")
    session = await runner.session_service.create_session(
        app_name="app",
        user_id="cloud_infra_user"
    )

    # Build multimodal content containing the uploaded case study PDF
    user_content = load_pdf_as_adk_content(
        pdf_path=str(pdf_file),
        prompt_text=(
            "Please review the attached Case Study PDF. Execute the complete sequential infrastructure "
            "workflow: 1. Architecture Requirements Analysis -> 2. Network Topology & Connectivity -> "
            "3. Security Hardening & Compliance -> 4. Terraform Implementation."
        ),
    )

    console.print(f"\n[bold green]► Session Started:[/bold green] ID = {session.id}")
    console.print("[dim]Executing sequential pipeline... This will stream each agent's analysis in order.[/dim]\n")

    current_agent = None
    agent_outputs = {}

    async for event in runner.run_async(
        user_id="cloud_infra_user",
        session_id=session.id,
        new_message=user_content,
    ):
        author = event.author
        if author in AGENT_TITLES and author != current_agent:
            current_agent = author
            step, title, color = AGENT_TITLES[author]
            console.print(f"\n[bold {color}]{'='*80}[/bold {color}]")
            console.print(f"[bold {color}]► [Step {step}] {title} is executing...[/bold {color}]")
            console.print(f"[bold {color}]{'='*80}[/bold {color}]\n")

        if event.content and event.content.parts:
            for part in event.content.parts:
                text = getattr(part, "text", "")
                if text:
                    agent_outputs[author] = agent_outputs.get(author, "") + text
                    console.print(text, end="")

    # Fetch updated session state
    updated_session = await runner.session_service.get_session(
        app_name="app",
        user_id="cloud_infra_user",
        session_id=session.id,
    )
    state = updated_session.state if updated_session else {}

    console.print(f"\n\n[bold green]{'='*80}[/bold green]")
    console.print("[bold green]✔ Multi-Agent Pipeline Completed Successfully![/bold green]")
    console.print(f"[bold green]{'='*80}[/bold green]\n")

    # Persist agent outputs to disk
    reports = [
        ("01_cloud_architecture_spec.md", state.get("cloud_architecture_spec") or agent_outputs.get("cloud_architect_agent", "")),
        ("02_network_topology_spec.md", state.get("network_spec") or agent_outputs.get("network_engineer_agent", "")),
        ("03_security_hardening_spec.md", state.get("security_spec") or agent_outputs.get("security_engineer_agent", "")),
        ("04_devops_terraform_spec.md", state.get("devops_terraform_spec") or agent_outputs.get("devops_engineer_agent", "")),
    ]

    for fname, content in reports:
        if content:
            file_dest = out_path / fname
            file_dest.write_text(content, encoding="utf-8")
            console.print(f"[green]Saved Report:[/green] {file_dest}")

    # Extract Terraform code into a dedicated terraform directory
    tf_dir = out_path / "terraform"
    devops_text = state.get("devops_terraform_spec") or agent_outputs.get("devops_engineer_agent", "")
    if devops_text:
        extracted = extract_terraform_files(devops_text, tf_dir)
        console.print(f"[green]Saved Terraform Configurations in:[/green] {tf_dir}")
        if extracted:
            for tf_name in extracted:
                console.print(f"  • {tf_name}")

    console.print("\n[bold cyan]All deliverables generated and stored in:[/bold cyan] " + str(out_path))


def main():
    parser = argparse.ArgumentParser(
        description="Run ADK Sequential Multi-Agent Cloud Infrastructure Pipeline on a Case Study PDF."
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default="sample_case_study.pdf",
        help="Path to case study PDF file (default: sample_case_study.pdf)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output_artifacts",
        help="Directory to save generated specifications and Terraform code",
    )
    args = parser.parse_args()

    asyncio.run(run_pipeline(pdf_path=args.pdf, output_dir=args.output_dir))


if __name__ == "__main__":
    main()
