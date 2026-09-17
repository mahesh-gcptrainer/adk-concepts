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

"""Tools for the Infrastructure Designer Multi-Agent System."""

import os

import pypdf


def _resolve_file_path(file_path: str) -> str | None:
    """Resolves a file path across current directory, project root, and samples folder."""
    cleaned = file_path.strip().strip("'\"")
    candidates = [
        cleaned,
        os.path.abspath(cleaned),
        os.path.join(os.getcwd(), cleaned),
        os.path.join(os.path.dirname(__file__), "..", cleaned),
        os.path.join(
            os.path.dirname(__file__), "..", "samples", os.path.basename(cleaned)
        ),
        os.path.join(os.getcwd(), "samples", os.path.basename(cleaned)),
    ]
    for candidate in candidates:
        if os.path.exists(candidate) and os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return None


def read_pdf_document(file_path: str, max_pages: int | None = None) -> str:
    """Extracts and formats text content from a local PDF specification file.

    Use this tool to read requirement documents, architecture briefs, or compliance guides
    provided as PDF files.

    Args:
        file_path: Path to the local PDF file (e.g., 'samples/ecommerce_requirements.pdf').
        max_pages: Optional maximum number of pages to read from the start of the document.

    Returns:
        Structured string containing document metadata and extracted text per page.
    """
    resolved_path = _resolve_file_path(file_path)
    if not resolved_path:
        return f"Error: PDF file '{file_path}' not found on the filesystem."

    try:
        reader = pypdf.PdfReader(resolved_path)
        total_pages = len(reader.pages)
        if total_pages == 0:
            return f"Warning: The PDF file '{resolved_path}' is empty."

        pages_to_read = (
            min(total_pages, max_pages) if max_pages and max_pages > 0 else total_pages
        )
        extracted_content = [
            f"=== Document: {os.path.basename(resolved_path)} (Total Pages: {total_pages}) ==="
        ]

        for idx in range(pages_to_read):
            page = reader.pages[idx]
            page_text = page.extract_text() or ""
            extracted_content.append(
                f"--- Page {idx + 1} of {total_pages} ---\n{page_text.strip()}"
            )

        if pages_to_read < total_pages:
            extracted_content.append(
                f"Note: Truncated after {pages_to_read} pages (out of {total_pages} total)."
            )

        return "\n\n".join(extracted_content)
    except Exception as exc:
        return f"Error extracting content from PDF '{file_path}': {exc!s}"
