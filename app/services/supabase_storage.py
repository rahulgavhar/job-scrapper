"""
Supabase Storage Service for handling resume uploads to cloud storage.
"""

import uuid
from typing import Optional, Tuple
from pathlib import Path
from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from app.core.config import settings


class SupabaseStorageService:
    """Service for managing file uploads to Supabase Storage."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Optional[Client] = None
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET

        if settings.USE_SUPABASE_STORAGE:
            if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                raise ValueError("Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")

            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
                self._ensure_bucket_exists()
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Supabase client: {e}")

    def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists. Create if it doesn't."""
        try:
            # Try to list files in bucket to verify it exists
            self.client.storage.from_(self.bucket_name).list()
        except Exception as e:
            # If bucket doesn't exist, it will raise an error
            # Note: Creating buckets via API might require service role key
            print(f"Warning: Could not verify bucket '{self.bucket_name}': {e}")
            print(f"Please ensure the bucket '{self.bucket_name}' exists in your Supabase project.")

    async def upload_file(self, file: UploadFile) -> Tuple[str, str]:
        """
        Upload a file to Supabase Storage.

        Args:
            file: The uploaded file

        Returns:
            Tuple of (file_path, public_url)

        Raises:
            HTTPException: If upload fails
        """
        if not self.client:
            raise HTTPException(status_code=500, detail="Supabase storage not initialized")

        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        try:
            # Generate unique filename
            ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{ext}"
            file_path = f"uploads/{unique_filename}"

            # Read file content
            file_content = await file.read()

            # Upload to Supabase Storage with explicit content type
            # file_options with "content-type" is required to override mime type detection
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "application/pdf"}
            )

            # Check if upload was successful
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Upload failed: {response.error}")

            # Generate public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)

            return file_path, public_url

        except Exception as e:
            error_msg = str(e)

            # Check for RLS policy violation
            if "row-level security policy" in error_msg.lower() or "unauthorized" in error_msg.lower():
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "Supabase Storage permission denied. Please configure your bucket:\n"
                        "1. Go to Supabase Dashboard -> Storage -> Your Bucket\n"
                        "2. Click 'Policies' tab\n"
                        "3. Create a policy for INSERT with: 'Allow all' or 'true' for now\n"
                        "4. Create a policy for SELECT with: 'Allow all' or 'true'\n"
                        "OR make the bucket public in Configuration tab.\n"
                        f"Original error: {error_msg}"
                    )
                )

            raise HTTPException(status_code=500, detail=f"Failed to upload to Supabase: {error_msg}")

    async def download_file(self, file_path: str) -> bytes:
        """
        Download a file from Supabase Storage.

        Args:
            file_path: Path to the file in storage

        Returns:
            File content as bytes

        Raises:
            HTTPException: If download fails
        """
        if not self.client:
            raise HTTPException(status_code=500, detail="Supabase storage not initialized")

        try:
            response = self.client.storage.from_(self.bucket_name).download(file_path)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to download from Supabase: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage.

        Args:
            file_path: Path to the file in storage

        Returns:
            True if deletion was successful

        Raises:
            HTTPException: If deletion fails
        """
        if not self.client:
            raise HTTPException(status_code=500, detail="Supabase storage not initialized")

        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete from Supabase: {str(e)}")

    def get_public_url(self, file_path: str) -> str:
        """
        Get the public URL for a file.

        Args:
            file_path: Path to the file in storage

        Returns:
            Public URL string
        """
        if not self.client:
            raise HTTPException(status_code=500, detail="Supabase storage not initialized")

        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)


# Create a singleton instance
supabase_storage = SupabaseStorageService() if settings.USE_SUPABASE_STORAGE else None

