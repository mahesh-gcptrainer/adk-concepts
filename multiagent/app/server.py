"""FastAPI Server exposing an interactive Web UI and REST API for Cloud Run."""

import os
import sys
import io
import zipfile
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure app package is on path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from google.adk.runners import InMemoryRunner
from google.genai import types
from app.agent import root_agent
from app.tools.pdf_loader import extract_pdf_text, load_pdf_as_adk_content

app = FastAPI(
    title="ADK Multi-Agent Cloud Infrastructure System",
    description="Sequential Multi-Agent System analyzing Case Study PDFs to generate Cloud Architecture and Terraform IaC.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = BASE_DIR / "output_artifacts"
TERRAFORM_DIR = OUTPUT_DIR / "terraform"
SAMPLE_PDF = BASE_DIR / "sample_case_study.pdf"


@app.get("/health")
def health_check():
    """Cloud Run health check endpoint."""
    return {"status": "healthy", "service": "multiagent-cloud-infrastructure"}


@app.get("/", response_class=HTMLResponse)
def index_page():
    """Serves the interactive web user interface."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google ADK - Multi-Agent Cloud Infrastructure System</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    .markdown-body pre { background: #1e293b; color: #f8fafc; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-top: 0.5rem; margin-bottom: 0.5rem; }
    .markdown-body code { font-family: monospace; background: #e2e8f0; padding: 0.15rem 0.35rem; border-radius: 0.25rem; font-size: 0.875rem; }
    .markdown-body pre code { background: transparent; padding: 0; }
    .markdown-body h1, .markdown-body h2, .markdown-body h3 { font-weight: bold; margin-top: 1rem; margin-bottom: 0.5rem; }
    .markdown-body h1 { font-size: 1.5rem; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.3rem; }
    .markdown-body h2 { font-size: 1.25rem; color: #1e293b; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.2rem; }
    .markdown-body h3 { font-size: 1.1rem; color: #334155; }
    .markdown-body ul { list-style-type: disc; padding-left: 1.5rem; margin-top: 0.5rem; margin-bottom: 0.5rem; }
    .markdown-body table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    .markdown-body th, .markdown-body td { border: 1px solid #cbd5e1; padding: 0.5rem 0.75rem; text-align: left; }
    .markdown-body th { background: #f1f5f9; font-weight: 600; }
  </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen">
  <!-- Header -->
  <header class="bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-900 text-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between">
      <div class="flex items-center space-x-3 mb-4 md:mb-0">
        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow">
          <i class="fa-solid fa-network-wired text-blue-600 text-xl"></i>
        </div>
        <div>
          <h1 class="text-2xl font-bold tracking-tight">Google ADK Multi-Agent System</h1>
          <p class="text-blue-100 text-xs">Sequential Cloud Architecture, Security & Terraform IaC Automation</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500 text-white">
          <i class="fa-solid fa-circle-check mr-1.5"></i> Cloud Run Live
        </span>
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/50 text-white border border-blue-300/40">
          Gemini 2.5 Flash
        </span>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
    
    <!-- Pipeline Sequence Tracker -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
      <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">Orchestration Sequence (SequentialAgent Root Class)</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Step 1 -->
        <div id="step-card-1" class="border border-slate-200 rounded-lg p-4 bg-slate-50 flex items-center space-x-3 transition-all duration-300">
          <div id="step-icon-1" class="w-9 h-9 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-sm">1</div>
          <div>
            <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">Step 1</div>
            <div class="font-semibold text-slate-800 text-sm">Cloud Architect</div>
            <div class="text-[11px] text-slate-500">Requirements & Blueprint</div>
          </div>
        </div>
        <!-- Step 2 -->
        <div id="step-card-2" class="border border-slate-200 rounded-lg p-4 bg-slate-50 flex items-center space-x-3 transition-all duration-300">
          <div id="step-icon-2" class="w-9 h-9 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-sm">2</div>
          <div>
            <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">Step 2</div>
            <div class="font-semibold text-slate-800 text-sm">Network Engineer</div>
            <div class="text-[11px] text-slate-500">VPC, Subnets & CIDR</div>
          </div>
        </div>
        <!-- Step 3 -->
        <div id="step-card-3" class="border border-slate-200 rounded-lg p-4 bg-slate-50 flex items-center space-x-3 transition-all duration-300">
          <div id="step-icon-3" class="w-9 h-9 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-sm">3</div>
          <div>
            <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">Step 3</div>
            <div class="font-semibold text-slate-800 text-sm">Security Engineer</div>
            <div class="text-[11px] text-slate-500">KMS, IAM & Compliance</div>
          </div>
        </div>
        <!-- Step 4 -->
        <div id="step-card-4" class="border border-slate-200 rounded-lg p-4 bg-slate-50 flex items-center space-x-3 transition-all duration-300">
          <div id="step-icon-4" class="w-9 h-9 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-sm">4</div>
          <div>
            <div class="text-xs font-bold text-slate-500 uppercase tracking-wider">Step 4</div>
            <div class="font-semibold text-slate-800 text-sm">DevOps Engineer</div>
            <div class="text-[11px] text-slate-500">Terraform (HCL) Code</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload & Action Area -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
      <h2 class="text-lg font-bold text-slate-800 mb-2">Upload Case Study PDF</h2>
      <p class="text-sm text-slate-500 mb-6">Select your enterprise architecture case study PDF or test directly with the preloaded FinTech Core Banking case study.</p>

      <form id="upload-form" class="space-y-4">
        <div class="flex flex-col sm:flex-row gap-4 items-center">
          <div class="flex-1 w-full">
            <label class="block text-xs font-semibold text-slate-600 mb-1">Choose PDF File (Optional):</label>
            <input type="file" id="pdf-file-input" accept="application/pdf"
                   class="block w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border border-slate-300 rounded-lg cursor-pointer bg-white" />
          </div>
          <div class="flex gap-2 w-full sm:w-auto mt-2 sm:mt-5">
            <button type="submit" id="run-btn"
                    class="w-full sm:w-auto inline-flex items-center justify-center px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg shadow transition focus:outline-none focus:ring-2 focus:ring-blue-500">
              <i class="fa-solid fa-play mr-2"></i> Execute Multi-Agent Pipeline
            </button>
            <button type="button" id="sample-btn"
                    class="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-sm rounded-lg border border-slate-300 transition">
              <i class="fa-solid fa-file-pdf mr-2 text-rose-600"></i> Use Preloaded Case Study
            </button>
          </div>
        </div>
      </form>

      <!-- Status banner -->
      <div id="status-box" class="hidden mt-6 p-4 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 text-sm flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
          <span id="status-text" class="font-medium">Pipeline running... Please wait.</span>
        </div>
        <span class="text-xs text-blue-600 font-mono" id="status-timer">00:00</span>
      </div>
    </div>

    <!-- Results Display -->
    <div id="results-area" class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <!-- Tabs header -->
      <div class="border-b border-slate-200 bg-slate-50/75 px-4 flex flex-wrap items-center justify-between">
        <div class="flex space-x-2 py-2" id="tabs-nav">
          <button onclick="switchTab('arch')" id="tab-btn-arch" class="px-4 py-2 text-xs sm:text-sm font-semibold rounded-md bg-white text-blue-700 shadow-sm border border-slate-200">
            <i class="fa-solid fa-cubes mr-1.5 text-blue-600"></i> Cloud Architecture
          </button>
          <button onclick="switchTab('net')" id="tab-btn-net" class="px-4 py-2 text-xs sm:text-sm font-semibold rounded-md text-slate-600 hover:text-slate-900">
            <i class="fa-solid fa-network-wired mr-1.5 text-emerald-600"></i> Network Topology
          </button>
          <button onclick="switchTab('sec')" id="tab-btn-sec" class="px-4 py-2 text-xs sm:text-sm font-semibold rounded-md text-slate-600 hover:text-slate-900">
            <i class="fa-solid fa-shield-halved mr-1.5 text-amber-600"></i> Security & Hardening
          </button>
          <button onclick="switchTab('tf')" id="tab-btn-tf" class="px-4 py-2 text-xs sm:text-sm font-semibold rounded-md text-slate-600 hover:text-slate-900">
            <i class="fa-solid fa-code mr-1.5 text-purple-600"></i> DevOps & Terraform
          </button>
        </div>
        <div class="py-2">
          <a href="/api/download-zip" id="download-zip-btn" class="inline-flex items-center px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-md shadow-sm transition">
            <i class="fa-solid fa-file-zipper mr-1.5"></i> Download Terraform Package (.zip)
          </a>
        </div>
      </div>

      <!-- Tab Contents -->
      <div class="p-6">
        <div id="tab-content-arch" class="markdown-body">
          <p class="text-slate-400 italic">No output yet. Run the pipeline to generate Cloud Architecture Blueprint.</p>
        </div>
        <div id="tab-content-net" class="markdown-body hidden">
          <p class="text-slate-400 italic">No output yet. Run the pipeline to generate Network Topology specifications.</p>
        </div>
        <div id="tab-content-sec" class="markdown-body hidden">
          <p class="text-slate-400 italic">No output yet. Run the pipeline to generate Security Hardening policies.</p>
        </div>
        <div id="tab-content-tf" class="markdown-body hidden">
          <p class="text-slate-400 italic">No output yet. Run the pipeline to generate Terraform (HCL) modular code.</p>
        </div>
      </div>
    </div>
  </main>

  <script>
    let activeTab = 'arch';
    let timerInterval = null;
    let startTime = null;

    function switchTab(tab) {
      activeTab = tab;
      ['arch', 'net', 'sec', 'tf'].forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        const content = document.getElementById(`tab-content-${t}`);
        if (t === tab) {
          btn.className = "px-4 py-2 text-xs sm:text-sm font-semibold rounded-md bg-white text-blue-700 shadow-sm border border-slate-200";
          content.classList.remove('hidden');
        } else {
          btn.className = "px-4 py-2 text-xs sm:text-sm font-semibold rounded-md text-slate-600 hover:text-slate-900";
          content.classList.add('hidden');
        }
      });
    }

    function setStepStatus(stepNum, status) {
      const card = document.getElementById(`step-card-${stepNum}`);
      const icon = document.getElementById(`step-icon-${stepNum}`);
      if (status === 'active') {
        card.className = "border border-blue-400 rounded-lg p-4 bg-blue-50/70 flex items-center space-x-3 transition-all duration-300 ring-2 ring-blue-400";
        icon.className = "w-9 h-9 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-sm animate-pulse";
      } else if (status === 'done') {
        card.className = "border border-emerald-300 rounded-lg p-4 bg-emerald-50/50 flex items-center space-x-3 transition-all duration-300";
        icon.className = "w-9 h-9 rounded-full bg-emerald-600 text-white font-bold flex items-center justify-center text-sm";
        icon.innerHTML = '<i class="fa-solid fa-check"></i>';
      } else {
        card.className = "border border-slate-200 rounded-lg p-4 bg-slate-50 flex items-center space-x-3 transition-all duration-300";
        icon.className = "w-9 h-9 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-sm";
        icon.innerText = stepNum;
      }
    }

    function startTimer() {
      startTime = Date.now();
      const timerElem = document.getElementById('status-timer');
      timerInterval = setInterval(() => {
        const delta = Math.floor((Date.now() - startTime) / 1000);
        const mins = String(Math.floor(delta / 60)).padStart(2, '0');
        const secs = String(delta % 60).padStart(2, '0');
        timerElem.innerText = `${mins}:${secs}`;
      }, 1000);
    }

    function stopTimer() {
      if (timerInterval) clearInterval(timerInterval);
    }

    async function executePipeline(fileToUpload = null) {
      const statusBox = document.getElementById('status-box');
      const statusText = document.getElementById('status-text');
      const runBtn = document.getElementById('run-btn');

      statusBox.classList.remove('hidden');
      runBtn.disabled = true;
      runBtn.classList.add('opacity-50');

      [1, 2, 3, 4].forEach(i => setStepStatus(i, 'idle'));
      setStepStatus(1, 'active');
      statusText.innerText = "Step 1/4: Cloud Architect Agent analyzing requirements...";
      startTimer();

      const formData = new FormData();
      if (fileToUpload) {
        formData.append("pdf_file", fileToUpload);
      }

      try {
        const response = await fetch('/api/run', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Render Markdown into tabs
        document.getElementById('tab-content-arch').innerHTML = marked.parse(data.cloud_architecture_spec || 'No architecture output');
        document.getElementById('tab-content-net').innerHTML = marked.parse(data.network_spec || 'No network output');
        document.getElementById('tab-content-sec').innerHTML = marked.parse(data.security_spec || 'No security output');
        document.getElementById('tab-content-tf').innerHTML = marked.parse(data.devops_terraform_spec || 'No terraform output');

        [1, 2, 3, 4].forEach(i => setStepStatus(i, 'done'));
        statusText.innerText = "✔ Sequential Pipeline completed successfully across all 4 agents!";
        statusBox.className = "mt-6 p-4 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center justify-between";
      } catch (err) {
        statusText.innerText = "Execution failed: " + err.message;
        statusBox.className = "mt-6 p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center justify-between";
      } finally {
        stopTimer();
        runBtn.disabled = false;
        runBtn.classList.remove('opacity-50');
      }
    }

    document.getElementById('upload-form').addEventListener('submit', function(e) {
      e.preventDefault();
      const input = document.getElementById('pdf-file-input');
      const file = input.files.length > 0 ? input.files[0] : null;
      executePipeline(file);
    });

    document.getElementById('sample-btn').addEventListener('click', function() {
      executePipeline(null);
    });

    // Auto-load existing artifacts if present
    window.addEventListener('DOMContentLoaded', async () => {
      try {
        const res = await fetch('/api/latest-results');
        if (res.ok) {
          const data = await res.json();
          if (data.cloud_architecture_spec) {
            document.getElementById('tab-content-arch').innerHTML = marked.parse(data.cloud_architecture_spec);
            document.getElementById('tab-content-net').innerHTML = marked.parse(data.network_spec || '');
            document.getElementById('tab-content-sec').innerHTML = marked.parse(data.security_spec || '');
            document.getElementById('tab-content-tf').innerHTML = marked.parse(data.devops_terraform_spec || '');
            [1, 2, 3, 4].forEach(i => setStepStatus(i, 'done'));
          }
        }
      } catch(e) {}
    });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


@app.get("/api/latest-results")
def get_latest_results():
    """Returns the most recently generated design artifacts from disk."""
    results = {}
    mapping = {
        "cloud_architecture_spec": OUTPUT_DIR / "01_cloud_architecture_spec.md",
        "network_spec": OUTPUT_DIR / "02_network_topology_spec.md",
        "security_spec": OUTPUT_DIR / "03_security_hardening_spec.md",
        "devops_terraform_spec": OUTPUT_DIR / "04_devops_terraform_spec.md",
    }
    for key, path in mapping.items():
        if path.exists():
            results[key] = path.read_text(encoding="utf-8")
        else:
            results[key] = ""
    return results


@app.post("/api/run")
async def run_pipeline_api(pdf_file: Optional[UploadFile] = File(None)):
    """Runs the SequentialAgent pipeline on an uploaded or default case study PDF."""
    temp_pdf = None
    try:
        if pdf_file and pdf_file.filename:
            temp_path = BASE_DIR / f"temp_{pdf_file.filename}"
            content = await pdf_file.read()
            with open(temp_path, "wb") as f:
                f.write(content)
            target_pdf = temp_path
            temp_pdf = temp_path
        else:
            target_pdf = SAMPLE_PDF

        if not target_pdf.exists():
            raise HTTPException(status_code=404, detail="Case study PDF not found.")

        # Create ADK InMemoryRunner
        runner = InMemoryRunner(agent=root_agent, app_name="app")
        session = await runner.session_service.create_session(
            app_name="app",
            user_id="cloudrun_user"
        )

        user_content = load_pdf_as_adk_content(
            pdf_path=str(target_pdf),
            prompt_text=(
                "Please review the attached Case Study PDF. Execute the complete sequential infrastructure "
                "workflow: 1. Architecture Requirements Analysis -> 2. Network Topology & Connectivity -> "
                "3. Security Hardening & Compliance -> 4. Terraform Implementation."
            ),
        )

        agent_outputs = {}
        async for event in runner.run_async(
            user_id="cloudrun_user",
            session_id=session.id,
            new_message=user_content,
        ):
            author = event.author
            if event.content and event.content.parts:
                for part in event.content.parts:
                    text = getattr(part, "text", "")
                    if text:
                        agent_outputs[author] = agent_outputs.get(author, "") + text

        # Retrieve state
        session_obj = await runner.session_service.get_session(
            app_name="app",
            user_id="cloudrun_user",
            session_id=session.id,
        )
        state = session_obj.state if session_obj else {}

        response_data = {
            "session_id": session.id,
            "cloud_architecture_spec": state.get("cloud_architecture_spec") or agent_outputs.get("cloud_architect_agent", ""),
            "network_spec": state.get("network_spec") or agent_outputs.get("network_engineer_agent", ""),
            "security_spec": state.get("security_spec") or agent_outputs.get("security_engineer_agent", ""),
            "devops_terraform_spec": state.get("devops_terraform_spec") or agent_outputs.get("devops_engineer_agent", ""),
        }

        # Update disk output files
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if response_data["cloud_architecture_spec"]:
            (OUTPUT_DIR / "01_cloud_architecture_spec.md").write_text(response_data["cloud_architecture_spec"], encoding="utf-8")
        if response_data["network_spec"]:
            (OUTPUT_DIR / "02_network_topology_spec.md").write_text(response_data["network_spec"], encoding="utf-8")
        if response_data["security_spec"]:
            (OUTPUT_DIR / "03_security_hardening_spec.md").write_text(response_data["security_spec"], encoding="utf-8")
        if response_data["devops_terraform_spec"]:
            (OUTPUT_DIR / "04_devops_terraform_spec.md").write_text(response_data["devops_terraform_spec"], encoding="utf-8")

        return response_data

    finally:
        if temp_pdf and temp_pdf.exists():
            try:
                temp_pdf.unlink()
            except Exception:
                pass


@app.get("/api/download-zip")
def download_terraform_zip():
    """Packages all generated Terraform files into a downloadable ZIP archive."""
    TERRAFORM_DIR.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in TERRAFORM_DIR.glob("*"):
            if file_path.is_file():
                zip_file.write(file_path, arcname=file_path.name)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=terraform_infrastructure_package.zip"},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app.server:app", host="0.0.0.0", port=port, reload=False)
