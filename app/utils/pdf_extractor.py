"""
app/utils/pdf_extractor.py

Extracts text content from PDF files using PyMuPDF (fitz).
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts and returns all text content from a PDF file.

    Args:
        file_path: Absolute path to the PDF file on disk.

    Returns:
        The extracted text, concatenated across all pages, stripped
        of leading/trailing whitespace. Returns an empty string if no
        extractable text is found (e.g. a scanned/image-only PDF) —
        callers are responsible for deciding whether that's an error.

    Raises:
        RuntimeError: if the file cannot be opened/parsed as a PDF.
    """
    try:
        text_parts: list[str] = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")
