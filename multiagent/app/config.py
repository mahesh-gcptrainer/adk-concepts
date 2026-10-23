"""Configuration settings for the Multi-Agent Cloud Infrastructure System."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Default LLM Model for agents
DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.5-flash")

# GCP Project and Region
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "project-247cb656-8ea6-47ef-a6f")
GCP_REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Ensure Vertex AI flag is active if project is present and no GEMINI_API_KEY
if not os.getenv("GEMINI_API_KEY") and GCP_PROJECT:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", GCP_REGION)
