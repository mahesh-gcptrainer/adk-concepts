import os
import json
import uuid
import logging
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types
from app.agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloud_architect_app")

app = FastAPI(
    title="ADK Dev UI - Cloud Architecture & Terraform Pipeline",
    description="Multi-agent Google ADK pipeline running Cloud Architect, Network, Security, and DevOps sequential agents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runner = InMemoryRunner(
    agent=root_agent,
    app_name="cloud_architect_app",
)

# ---------------------------------------------------------------------------
# ADK Standard Dev UI HTML Template
# ---------------------------------------------------------------------------
DEV_UI_HTML = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google ADK • Dev UI</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Marked for Markdown -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <!-- Highlight.js for Syntax Highlighting -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/terraform.min.js"></script>
  <!-- Google Fonts: Inter & Roboto Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['Roboto Mono', 'monospace'],
          },
          colors: {
            google: {
              blue: '#8ab4f8',
              blueDark: '#1a73e8',
              surface: '#131314',
              card: '#1e1f20',
              cardHover: '#282a2c',
              border: '#333537',
              textMuted: '#9aa0a6',
              green: '#81c995',
              yellow: '#fdd663',
              red: '#f28b82',
            }
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #131314; color: #e3e3e3; }
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #131314; }
    ::-webkit-scrollbar-thumb { background: #333537; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #444746; }
    .prose-dark { color: #e3e3e3; }
    .prose-dark h1, .prose-dark h2, .prose-dark h3 { color: #8ab4f8; font-weight: 600; margin-top: 1.25rem; margin-bottom: 0.5rem; }
    .prose-dark h1 { font-size: 1.5rem; }
    .prose-dark h2 { font-size: 1.25rem; }
    .prose-dark h3 { font-size: 1.1rem; }
    .prose-dark p { margin-bottom: 0.75rem; line-height: 1.6; color: #d0d4d9; }
    .prose-dark ul, .prose-dark ol { margin-left: 1.5rem; margin-bottom: 0.75rem; list-style-type: disc; }
    .prose-dark li { margin-bottom: 0.25rem; }
    .prose-dark code { background: #282a2c; color: #fdd663; padding: 2px 6px; border-radius: 4px; font-family: 'Roboto Mono', monospace; font-size: 0.9em; }
    .prose-dark pre { background: #1e1f20; padding: 1rem; border-radius: 8px; border: 1px solid #333537; overflow-x: auto; margin: 1rem 0; }
    .prose-dark table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
    .prose-dark th, .prose-dark td { border: 1px solid #333537; padding: 8px 12px; text-align: left; }
    .prose-dark th { background: #282a2c; color: #8ab4f8; }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans selection:bg-blue-500 selection:text-white">

  <!-- Top App Navigation (ADK Dev UI Style) -->
  <header class="border-b border-google-border bg-google-card/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/30 text-google-blue">
          <i data-lucide="layers" class="w-5 h-5"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-semibold text-white tracking-tight text-base">Google ADK</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-google-border text-google-textMuted font-mono">Dev UI v1.0</span>
          </div>
          <p class="text-xs text-google-textMuted">Cloud Architecture & Terraform Synthesis</p>
        </div>
      </div>

      <div class="flex items-center space-x-4">
        <div class="hidden md:flex items-center space-x-2 bg-google-surface px-3 py-1.5 rounded-full border border-google-border text-xs">
          <span class="w-2 h-2 rounded-full bg-google-green animate-pulse"></span>
          <span class="text-google-textMuted font-mono">Pipeline:</span>
          <span class="text-google-blue font-mono font-medium">SequentialAgent</span>
        </div>
        <div class="hidden lg:flex items-center space-x-2 bg-google-surface px-3 py-1.5 rounded-full border border-google-border text-xs">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-google-yellow"></i>
          <span class="text-google-textMuted">Model:</span>
          <span class="text-white font-mono">gemini-2.5-pro</span>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Workspace -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col gap-6">

    <!-- Sequential Agent Execution Stepper Bar -->
    <div class="bg-google-card border border-google-border rounded-xl p-4 shadow-sm">
      <div class="text-xs font-semibold uppercase tracking-wider text-google-textMuted mb-3 flex items-center justify-between">
        <span>Sequential Execution Pipeline (4 Sub-Agents)</span>
        <span id="pipelineStatusText" class="text-google-textMuted font-mono font-normal">Status: Ready</span>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <!-- Step 1 -->
        <div id="step-1" class="flex items-center p-3 rounded-lg border border-google-border bg-google-surface/60 transition-all duration-300">
          <div id="step-icon-1" class="w-7 h-7 rounded-full bg-google-card flex items-center justify-center text-xs font-mono text-google-textMuted mr-3 border border-google-border">1</div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-white truncate">Cloud Architect</p>
            <p id="step-status-1" class="text-[11px] text-google-textMuted truncate">High-Level Architecture</p>
          </div>
        </div>

        <!-- Step 2 -->
        <div id="step-2" class="flex items-center p-3 rounded-lg border border-google-border bg-google-surface/60 transition-all duration-300">
          <div id="step-icon-2" class="w-7 h-7 rounded-full bg-google-card flex items-center justify-center text-xs font-mono text-google-textMuted mr-3 border border-google-border">2</div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-white truncate">Network Engineer</p>
            <p id="step-status-2" class="text-[11px] text-google-textMuted truncate">VPC & Routing</p>
          </div>
        </div>

        <!-- Step 3 -->
        <div id="step-3" class="flex items-center p-3 rounded-lg border border-google-border bg-google-surface/60 transition-all duration-300">
          <div id="step-icon-3" class="w-7 h-7 rounded-full bg-google-card flex items-center justify-center text-xs font-mono text-google-textMuted mr-3 border border-google-border">3</div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-white truncate">Security Engineer</p>
            <p id="step-status-3" class="text-[11px] text-google-textMuted truncate">IAM, KMS & Guardrails</p>
          </div>
        </div>

        <!-- Step 4 -->
        <div id="step-4" class="flex items-center p-3 rounded-lg border border-google-border bg-google-surface/60 transition-all duration-300">
          <div id="step-icon-4" class="w-7 h-7 rounded-full bg-google-card flex items-center justify-center text-xs font-mono text-google-textMuted mr-3 border border-google-border">4</div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-white truncate">DevOps Engineer</p>
            <p id="step-status-4" class="text-[11px] text-google-textMuted truncate">Terraform Synthesis</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Grid: Input Form (Left) & Output Workspace (Right) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">

      <!-- Left Panel: Input & PDF Upload -->
      <div class="lg:col-span-4 flex flex-col gap-4">
        <div class="bg-google-card border border-google-border rounded-xl p-5 shadow-sm flex flex-col gap-4">
          <div class="flex items-center justify-between">
            <h2 class="text-sm font-semibold text-white flex items-center gap-2">
              <i data-lucide="file-up" class="w-4 h-4 text-google-blue"></i>
              Case Study Input
            </h2>
          </div>

          <!-- PDF Upload Box -->
          <div id="dropZone" class="border-2 border-dashed border-google-border hover:border-google-blue/50 rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer bg-google-surface/40 transition-colors">
            <input type="file" id="pdfFileInput" accept=".pdf,application/pdf" class="hidden">
            <div class="w-12 h-12 rounded-full bg-google-card flex items-center justify-center mb-3 text-google-blue border border-google-border">
              <i data-lucide="upload-cloud" class="w-6 h-6"></i>
            </div>
            <p class="text-sm font-medium text-white mb-1" id="uploadLabel">Upload Case Study PDF</p>
            <p class="text-xs text-google-textMuted" id="fileDetails">Click or drag & drop PDF file here</p>
          </div>

          <!-- Custom Prompt -->
          <div>
            <label class="block text-xs font-medium text-google-textMuted mb-2">Instructions / Focus Area</label>
            <textarea id="promptInput" rows="3" class="w-full bg-google-surface border border-google-border rounded-lg p-3 text-xs text-white focus:outline-none focus:border-google-blue resize-none font-sans" placeholder="e.g., Analyze this case study for a multi-region deployment with high availability...">Please analyze this case study PDF and generate complete cloud architecture, network topology, security controls, and Terraform IaC.</textarea>
          </div>

          <!-- Run Pipeline Button -->
          <button id="runBtn" onclick="runPipeline()" class="w-full py-2.5 px-4 rounded-lg bg-google-blueDark hover:bg-blue-600 text-white font-medium text-sm flex items-center justify-center space-x-2 transition-all shadow-md hover:shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed">
            <i data-lucide="play" class="w-4 h-4"></i>
            <span>Execute Sequential Pipeline</span>
          </button>
        </div>

        <!-- Session State Info Card -->
        <div class="bg-google-card border border-google-border rounded-xl p-4 text-xs text-google-textMuted">
          <div class="font-semibold text-white mb-2 flex items-center gap-1.5">
            <i data-lucide="database" class="w-3.5 h-3.5 text-google-green"></i>
            ADK Session State
          </div>
          <div class="space-y-1.5 font-mono text-[11px]">
            <div class="flex justify-between"><span class="text-google-textMuted">session_id:</span> <span id="sessIdDisplay" class="text-white">None</span></div>
            <div class="flex justify-between"><span class="text-google-textMuted">state.keys:</span> <span id="stateKeysDisplay" class="text-google-blue">[]</span></div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Multi-Tab Output Viewer -->
      <div class="lg:col-span-8 bg-google-card border border-google-border rounded-xl flex flex-col overflow-hidden shadow-sm">
        
        <!-- Tab Navigation Bar -->
        <div class="border-b border-google-border bg-google-surface/60 px-4 flex items-center justify-between overflow-x-auto">
          <div class="flex space-x-1 py-2">
            <button onclick="switchTab('arch')" id="tab-btn-arch" class="tab-btn px-3 py-1.5 rounded-lg text-xs font-medium transition-all bg-google-card text-google-blue border border-google-border">
              🏗️ Cloud Architecture
            </button>
            <button onclick="switchTab('network')" id="tab-btn-network" class="tab-btn px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-google-textMuted hover:text-white">
              🌐 Network Topology
            </button>
            <button onclick="switchTab('security')" id="tab-btn-security" class="tab-btn px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-google-textMuted hover:text-white">
              🔒 Security & IAM
            </button>
            <button onclick="switchTab('terraform')" id="tab-btn-terraform" class="tab-btn px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-google-textMuted hover:text-white">
              ⚡ Terraform IaC
            </button>
            <button onclick="switchTab('events')" id="tab-btn-events" class="tab-btn px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-google-textMuted hover:text-white">
              📜 Logs / Events
            </button>
          </div>

          <div class="flex items-center space-x-2 py-2">
            <button id="copyBtn" onclick="copyActiveContent()" class="p-1.5 text-google-textMuted hover:text-white hover:bg-google-card rounded-md border border-transparent hover:border-google-border text-xs flex items-center gap-1">
              <i data-lucide="copy" class="w-3.5 h-3.5"></i>
              <span>Copy</span>
            </button>
            <button id="downloadTfBtn" onclick="downloadTerraform()" class="p-1.5 text-google-blue hover:text-white hover:bg-google-card rounded-md border border-transparent hover:border-google-border text-xs flex items-center gap-1 hidden">
              <i data-lucide="download" class="w-3.5 h-3.5"></i>
              <span>Download .tf</span>
            </button>
          </div>
        </div>

        <!-- Tab Content Area -->
        <div class="flex-1 p-6 overflow-y-auto min-h-[480px] max-h-[700px] bg-google-card" id="outputArea">
          
          <!-- Cloud Architecture View -->
          <div id="tab-arch" class="tab-content prose-dark max-w-none">
            <div class="text-center py-16 text-google-textMuted">
              <i data-lucide="cloud" class="w-12 h-12 mx-auto mb-3 opacity-30"></i>
              <p class="text-sm font-medium">No architecture output yet.</p>
              <p class="text-xs mt-1">Upload a case study PDF and click "Execute Sequential Pipeline".</p>
            </div>
          </div>

          <!-- Network Architecture View -->
          <div id="tab-network" class="tab-content prose-dark max-w-none hidden">
            <div class="text-center py-16 text-google-textMuted">
              <i data-lucide="network" class="w-12 h-12 mx-auto mb-3 opacity-30"></i>
              <p class="text-sm font-medium">No network topology output yet.</p>
            </div>
          </div>

          <!-- Security Architecture View -->
          <div id="tab-security" class="tab-content prose-dark max-w-none hidden">
            <div class="text-center py-16 text-google-textMuted">
              <i data-lucide="shield-check" class="w-12 h-12 mx-auto mb-3 opacity-30"></i>
              <p class="text-sm font-medium">No security design output yet.</p>
            </div>
          </div>

          <!-- Terraform Code View -->
          <div id="tab-terraform" class="tab-content hidden">
            <div class="text-center py-16 text-google-textMuted" id="tfPlaceholder">
              <i data-lucide="code-2" class="w-12 h-12 mx-auto mb-3 opacity-30"></i>
              <p class="text-sm font-medium">No Terraform code generated yet.</p>
            </div>
            <pre id="tfPre" class="hidden rounded-lg border border-google-border !bg-google-surface p-4 text-xs font-mono overflow-x-auto"><code id="tfCode" class="language-terraform"></code></pre>
          </div>

          <!-- Logs / Events View -->
          <div id="tab-events" class="tab-content hidden font-mono text-xs space-y-2">
            <div class="text-google-textMuted flex items-center space-x-2">
              <span class="text-google-green">•</span>
              <span>Dev UI Initialized. Ready to accept case study upload.</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  </main>

  <script>
    lucide.createIcons();

    let selectedFile = null;
    let currentTab = 'arch';
    let outputData = {
      arch: '',
      network: '',
      security: '',
      terraform: '',
      events: []
    };

    // File Drag & Drop Handlers
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('pdfFileInput');

    dropZone.onclick = () => fileInput.click();
    dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('border-google-blue'); };
    dropZone.ondragleave = () => { dropZone.classList.remove('border-google-blue'); };
    dropZone.ondrop = (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-google-blue');
      if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    };
    fileInput.onchange = (e) => {
      if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    };

    function handleFileSelect(file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Please select a valid PDF file.');
        return;
      }
      selectedFile = file;
      document.getElementById('uploadLabel').innerText = file.name;
      document.getElementById('fileDetails').innerText = `${(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to process`;
      addLog(`Selected PDF file: ${file.name} (${file.size} bytes)`);
    }

    function addLog(msg, author = 'SYSTEM') {
      const timestamp = new Date().toLocaleTimeString();
      outputData.events.push(`[${timestamp}] [${author}] ${msg}`);
      const eventsContainer = document.getElementById('tab-events');
      const div = document.createElement('div');
      div.className = 'text-google-textMuted flex items-start space-x-2';
      div.innerHTML = `<span class="text-google-blue">[${timestamp}]</span> <span class="text-google-yellow">[${author}]</span> <span>${msg}</span>`;
      eventsContainer.appendChild(div);
      eventsContainer.scrollTop = eventsContainer.scrollHeight;
    }

    function switchTab(tab) {
      currentTab = tab;
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.className = 'tab-btn px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-google-textMuted hover:text-white';
      });
      document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));

      const activeBtn = document.getElementById(`tab-btn-${tab}`);
      const activeContent = document.getElementById(`tab-${tab}`);
      if (activeBtn) activeBtn.className = 'tab-btn px-3 py-1.5 rounded-lg text-xs font-medium transition-all bg-google-card text-google-blue border border-google-border';
      if (activeContent) activeContent.classList.remove('hidden');

      const dlBtn = document.getElementById('downloadTfBtn');
      if (tab === 'terraform' && outputData.terraform) {
        dlBtn.classList.remove('hidden');
      } else {
        dlBtn.classList.add('hidden');
      }
    }

    function setStepState(stepNum, state) {
      const stepEl = document.getElementById(`step-${stepNum}`);
      const iconEl = document.getElementById(`step-icon-1`);
      const statusEl = document.getElementById(`step-status-${stepNum}`);

      if (state === 'running') {
        stepEl.className = 'flex items-center p-3 rounded-lg border border-google-blue bg-blue-950/30 transition-all duration-300';
        statusEl.innerText = '⚡ Processing...';
        statusEl.className = 'text-[11px] text-google-blue font-medium truncate animate-pulse';
      } else if (state === 'done') {
        stepEl.className = 'flex items-center p-3 rounded-lg border border-green-500/40 bg-green-950/20 transition-all duration-300';
        statusEl.innerText = '✓ Completed';
        statusEl.className = 'text-[11px] text-google-green font-medium truncate';
      } else {
        stepEl.className = 'flex items-center p-3 rounded-lg border border-google-border bg-google-surface/60 transition-all duration-300';
        statusEl.className = 'text-[11px] text-google-textMuted truncate';
      }
    }

    async function runPipeline() {
      if (!selectedFile) {
        alert('Please upload a case study PDF first.');
        return;
      }

      const runBtn = document.getElementById('runBtn');
      runBtn.disabled = true;
      runBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Synthesizing Architecture...</span>`;
      lucide.createIcons();

      document.getElementById('pipelineStatusText').innerText = 'Status: Running Sequential Pipeline';
      document.getElementById('pipelineStatusText').className = 'text-google-blue font-mono font-medium animate-pulse';

      // Reset steps
      [1, 2, 3, 4].forEach(i => setStepState(i, 'pending'));
      setStepState(1, 'running');
      addLog('Triggering sequential execution across 4 LlmAgents...', 'RUNNER');

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('prompt', document.getElementById('promptInput').value);

      try {
        const response = await fetch('/api/analyze', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || 'Failed to process case study.');
        }

        const data = await response.json();
        const results = data.results;

        outputData.arch = results.cloud_architecture || '';
        outputData.network = results.network_architecture || '';
        outputData.security = results.security_architecture || '';
        outputData.terraform = results.terraform_code || '';

        // Render Markdown views
        document.getElementById('tab-arch').innerHTML = marked.parse(outputData.arch);
        document.getElementById('tab-network').innerHTML = marked.parse(outputData.network);
        document.getElementById('tab-security').innerHTML = marked.parse(outputData.security);

        // Render Terraform Code view
        if (outputData.terraform) {
          document.getElementById('tfPlaceholder').classList.add('hidden');
          const pre = document.getElementById('tfPre');
          const code = document.getElementById('tfCode');
          code.textContent = outputData.terraform;
          pre.classList.remove('hidden');
          hljs.highlightElement(code);
        }

        [1, 2, 3, 4].forEach(i => setStepState(i, 'done'));

        document.getElementById('sessIdDisplay').innerText = data.session_id.substring(0, 16) + '...';
        document.getElementById('stateKeysDisplay').innerText = '["cloud_architecture", "network_architecture", "security_architecture", "terraform_code"]';
        document.getElementById('pipelineStatusText').innerText = 'Status: Completed Successfully';
        document.getElementById('pipelineStatusText').className = 'text-google-green font-mono font-medium';

        addLog('All 4 agents completed successfully. Terraform code generated.', 'SEQUENTIAL_AGENT');
        switchTab('arch');

      } catch (err) {
        alert(`Error: ${err.message}`);
        addLog(`Error: ${err.message}`, 'ERROR');
        document.getElementById('pipelineStatusText').innerText = 'Status: Failed';
        document.getElementById('pipelineStatusText').className = 'text-google-red font-mono font-medium';
      } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i><span>Execute Sequential Pipeline</span>`;
        lucide.createIcons();
      }
    }

    function copyActiveContent() {
      let content = '';
      if (currentTab === 'arch') content = outputData.arch;
      else if (currentTab === 'network') content = outputData.network;
      else if (currentTab === 'security') content = outputData.security;
      else if (currentTab === 'terraform') content = outputData.terraform;
      else if (currentTab === 'events') content = outputData.events.join('\\n');

      if (!content) return;
      navigator.clipboard.writeText(content).then(() => {
        const copyBtn = document.getElementById('copyBtn');
        copyBtn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-google-green"></i><span class="text-google-green">Copied!</span>`;
        lucide.createIcons();
        setTimeout(() => {
          copyBtn.innerHTML = `<i data-lucide="copy" class="w-3.5 h-3.5"></i><span>Copy</span>`;
          lucide.createIcons();
        }, 2000);
      });
    }

    function downloadTerraform() {
      if (!outputData.terraform) return;
      const blob = new Blob([outputData.terraform], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'main.tf';
      a.click();
      URL.revokeObjectURL(url);
    }
  </script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/dev-ui", response_class=HTMLResponse)
def serve_dev_ui():
    """Serves the Google ADK Dev UI."""
    return HTMLResponse(content=DEV_UI_HTML, status_code=200)

@app.get("/healthz")
def healthz():
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze_case_study(
    file: UploadFile = File(..., description="PDF Case Study document"),
    prompt: str = Form(
        "Please analyze this case study PDF and generate complete cloud architecture, network topology, security controls, and Terraform IaC.",
        description="Optional custom prompt instruction"
    ),
):
    if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF file.")

    logger.info(f"Received case study: {file.filename}")
    pdf_bytes = await file.read()
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    # Create session
    session = await runner.session_service.create_session(
        app_name="cloud_architect_app",
        user_id=user_id,
    )

    # Multi-modal input part with PDF bytes and prompt
    user_content = genai_types.Content(
        role="user",
        parts=[
            genai_types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            genai_types.Part.from_text(text=prompt),
        ],
    )

    logger.info(f"Executing SequentialAgent pipeline for session: {session.id}...")

    # Execute the 4 sequential agents
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=user_content,
    ):
        if event.author:
            logger.info(f"Agent turn completed: {event.author}")

    # Fetch updated session state
    updated_session = await runner.session_service.get_session(
        app_name="cloud_architect_app",
        user_id=user_id,
        session_id=session.id,
    )

    return {
        "status": "success",
        "session_id": session.id,
        "results": {
            "cloud_architecture": updated_session.state.get("cloud_architecture"),
            "network_architecture": updated_session.state.get("network_architecture"),
            "security_architecture": updated_session.state.get("security_architecture"),
            "terraform_code": updated_session.state.get("terraform_code"),
        }
    }
