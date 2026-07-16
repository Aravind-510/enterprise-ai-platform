import os
import shutil
import hashlib
from pathlib import Path

import filetype
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/documents", tags=["Knowledge Base"])

# Storage folder
UPLOAD_DIR = Path("storage/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md"
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown"
}

# Maximum file size (20 MB)
MAX_FILE_SIZE = 20 * 1024 * 1024


def calculate_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File exceeds maximum size."
        )

    detected = filetype.guess(content)

    if detected:

        if detected.mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid MIME type."
            )

    file_hash = calculate_hash(content)

    # Duplicate detection
    for existing in UPLOAD_DIR.iterdir():

        if existing.is_file():

            with open(existing, "rb") as f:
                existing_hash = calculate_hash(f.read())

            if existing_hash == file_hash:
                raise HTTPException(
                    status_code=409,
                    detail="Duplicate document."
                )

    save_path = UPLOAD_DIR / file.filename

    with open(save_path, "wb") as buffer:
        buffer.write(content)

    return {
        "message": "Document uploaded successfully",
        "filename": file.filename,
        "location": str(save_path),
        "size": len(content)
    }