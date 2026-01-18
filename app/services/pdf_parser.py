from typing import Tuple
from pathlib import Path
from fastapi import UploadFile, HTTPException
from io import BytesIO

from PyPDF2 import PdfReader


async def save_resume(file: UploadFile) -> Tuple[str, str]:
    """
    Save the uploaded resume file to Supabase Storage.

    Returns:
        Tuple of (file_path, storage_url)
        - (supabase_path, public_url)
    """
    ext = Path(file.filename).suffix
    if ext.lower() != ".pdf":
        raise ValueError("Only PDF files are allowed")

    # Upload to Supabase Storage
    from app.services.supabase_storage import supabase_storage

    if not supabase_storage:
        raise HTTPException(status_code=500, detail="Supabase storage not initialized")

    # Upload to Supabase
    file_path, public_url = await supabase_storage.upload_file(file)
    return file_path, public_url


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


async def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file stored in Supabase.

    Args:
        file_path: Path to PDF file in Supabase storage

    Returns:
        The text content as a string.
    """
    try:
        from app.services.supabase_storage import supabase_storage

        if not supabase_storage:
            raise RuntimeError("Supabase storage not initialized")

        # Download from Supabase and process in memory
        file_content = await supabase_storage.download_file(file_path)

        # Extract text from bytes (synchronous operation)
        text = _extract_text_from_bytes(file_content)
        return text

    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


