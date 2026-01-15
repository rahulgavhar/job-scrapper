from fastapi import UploadFile
from app.services.pdf_parser import save_resume


async def save_pdf(file: UploadFile) -> str:
    """
    Saves uploaded PDF and returns file path.
    Delegates to pdf_parser service.
    """
    return await save_resume(file)

