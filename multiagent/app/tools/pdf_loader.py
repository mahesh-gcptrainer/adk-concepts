"""PDF processing tools and utilities for case study ingestion."""

import os
from io import BytesIO
from typing import Optional
from pypdf import PdfReader
from google.genai import types


def extract_pdf_text(pdf_path: str) -> dict:
    """Extracts text content and page metadata from a PDF file.

    Args:
        pdf_path: Absolute or relative filesystem path to the PDF document.

    Returns:
        dict with status, page_count, and extracted_text.
    """
    if not os.path.exists(pdf_path):
        return {
            "status": "error",
            "error": f"PDF file not found at path: {pdf_path}",
            "extracted_text": "",
        }

    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        pages_content = []

        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            pages_content.append(f"--- Page {idx + 1} ---\n{page_text}")

        full_text = "\n\n".join(pages_content)
        return {
            "status": "success",
            "file_path": pdf_path,
            "page_count": total_pages,
            "extracted_text": full_text,
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": f"Failed to extract PDF text: {str(exc)}",
            "extracted_text": "",
        }


def load_pdf_as_adk_content(
    pdf_path: str,
    prompt_text: Optional[str] = None
) -> types.Content:
    """Loads a PDF file as a native multimodal Gemini Part for ADK execution.

    Args:
        pdf_path: Path to the case study PDF file.
        prompt_text: Optional instructional prompt to accompany the PDF.

    Returns:
        google.genai.types.Content object containing the PDF Part and text prompt.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Case study PDF not found at: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")

    default_prompt = (
        "Attached is the case study PDF document. Please analyze the requirements "
        "and execute the end-to-end cloud infrastructure design and Terraform implementation."
    )
    instruction = prompt_text or default_prompt
    text_part = types.Part.from_text(text=instruction)

    return types.Content(parts=[pdf_part, text_part])
