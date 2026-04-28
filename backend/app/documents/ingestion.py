import os
import uuid
import PyPDF2
import docx
from typing import Optional
from app.config import settings


def save_upload(file_bytes: bytes, original_filename: str) -> tuple[str, str]:
    """Save uploaded file to disk. Returns (saved_path, unique_filename)."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = original_filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(settings.upload_dir, unique_name)
    with open(save_path, "wb") as f:
        f.write(file_bytes)
    return save_path, unique_name


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF file page by page.
    Returns list of {"page": int, "text": str}
    """
    pages = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append({"page": page_num, "text": text})
    return pages


def extract_text_from_docx(file_path: str) -> list[dict]:
    """
    Extract text from a DOCX file paragraph by paragraph.
    Returns list of {"page": int, "text": str} (page estimation).
    """
    doc = docx.Document(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    # DOCX doesn't have real pages, treat entire doc as one block
    return [{"page": 1, "text": full_text}]


def extract_text_from_txt(file_path: str) -> list[dict]:
    """Extract text from a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()
    return [{"page": 1, "text": content}]


def extract_text(file_path: str, file_type: str) -> list[dict]:
    """
    Main dispatcher — extract text based on file type.
    Returns list of {"page": int, "text": str}
    """
    extractors = {
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "doc": extract_text_from_docx,
        "txt": extract_text_from_txt,
    }
    extractor = extractors.get(file_type.lower())
    if not extractor:
        raise ValueError(f"Unsupported file type: {file_type}")
    return extractor(file_path)


ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}
MAX_SIZE_BYTES = settings.max_file_size_mb * 1024 * 1024


def validate_file(filename: str, file_size: int) -> str:
    """Validate file type and size. Returns file extension."""
    if "." not in filename:
        raise ValueError("File has no extension")
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type .{ext} not supported. Allowed: {ALLOWED_EXTENSIONS}")
    if file_size > MAX_SIZE_BYTES:
        raise ValueError(f"File too large. Max size: {settings.max_file_size_mb}MB")
    return ext
