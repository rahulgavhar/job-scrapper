import uuid
from pathlib import Path
from fastapi import UploadFile

from PyPDF2 import PdfReader

# Directory to save uploaded resumes
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_resume(file: UploadFile) -> str:
    """
    Save the uploaded resume file to disk with a unique name.

    Returns:
        The path of the saved file.
    """
    ext = Path(file.filename).suffix
    if ext.lower() != ".pdf":
        raise ValueError("Only PDF files are allowed")

    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Use async file operations for better performance
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return str(file_path)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Returns:
        The text content as a string.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    return text.strip()

