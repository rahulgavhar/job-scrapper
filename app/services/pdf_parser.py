import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from io import BytesIO

from PyPDF2 import PdfReader
from app.core.config import settings

# Directory to save uploaded resumes (for local storage)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_resume(file: UploadFile) -> Tuple[str, str]:
    """
    Save the uploaded resume file to either Supabase or local disk.

    Returns:
        Tuple of (file_path, storage_url)
        - For Supabase: (supabase_path, public_url)
        - For local: (local_file_path, local_file_path)
    """
    ext = Path(file.filename).suffix
    if ext.lower() != ".pdf":
        raise ValueError("Only PDF files are allowed")

    # Check if Supabase storage is enabled
    if settings.USE_SUPABASE_STORAGE:
        from app.services.supabase_storage import supabase_storage

        if supabase_storage:
            # Upload to Supabase
            file_path, public_url = await supabase_storage.upload_file(file)
            return file_path, public_url
        else:
            # Fallback to local storage if Supabase is not initialized
            print("Warning: Supabase storage not initialized, falling back to local storage")

    # Local storage fallback
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Use async file operations for better performance
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    local_path = str(file_path)
    return local_path, local_path


def _extract_text_from_bytes(file_content: bytes) -> str:
    """
    Extract text from PDF bytes (synchronous).

    Args:
        file_content: PDF file content as bytes

    Returns:
        Extracted text content
    """
    text = ""
    try:
        pdf_file = BytesIO(file_content)
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF bytes: {e}")

    return text.strip()


def _extract_text_from_local_file(file_path: str) -> str:
    """
    Extract text from a local PDF file (synchronous).

    Args:
        file_path: Path to local PDF file

    Returns:
        Extracted text content
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF file: {e}")

    return text.strip()


async def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file (async).
    Supports both local files and Supabase storage.

    Args:
        file_path: Path to PDF file (local path or Supabase path)

    Returns:
        The text content as a string.
    """
    try:
        # Check if this is a Supabase path
        if settings.USE_SUPABASE_STORAGE and file_path.startswith("uploads/"):
            from app.services.supabase_storage import supabase_storage

            if supabase_storage:
                # Download from Supabase and process in memory
                file_content = await supabase_storage.download_file(file_path)

                # Extract text from bytes (synchronous operation)
                text = _extract_text_from_bytes(file_content)
                return text

        # Local file processing (synchronous)
        text = _extract_text_from_local_file(file_path)
        return text

    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


