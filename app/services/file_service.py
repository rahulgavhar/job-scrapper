from typing import Tuple
from fastapi import UploadFile
from app.services.pdf_parser import save_resume


async def save_pdf(file: UploadFile) -> Tuple[str, str]:
    """
    Saves uploaded PDF and returns file path and storage URL.
    Delegates to pdf_parser service.

    Returns:
        Tuple of (file_path, storage_url)
        - For Supabase: (supabase_path, public_url)
        - For local: (local_file_path, local_file_path)
    """
    return await save_resume(file)

