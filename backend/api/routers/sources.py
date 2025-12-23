"""
Sources API router.

Endpoints for file upload and source management.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from uuid import UUID
import shutil
import os
import hashlib

import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from api.dependencies import get_db
from api.models.responses import SourceResponse, MessageResponse
from db.models import Source, Project, SourceType
from config import settings

router = APIRouter()


def compute_checksum(file_path: str) -> str:
    """Compute SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_source_type(filename: str) -> SourceType:
    """Determine source type from filename extension."""
    ext = filename.lower().split(".")[-1]
    mapping = {
        "json": SourceType.JSON,
        "jsonl": SourceType.JSON,
        "csv": SourceType.CSV,
        "txt": SourceType.TEXT,
        "md": SourceType.TEXT,
        "pdf": SourceType.PDF,
        "docx": SourceType.DOCX,
    }
    return mapping.get(ext, SourceType.TEXT)


@router.post("/upload", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_source(
    project_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a data source file.

    Saves file to storage and creates Source record.
    File is stored at: {UPLOAD_DIR}/{project_id}/{filename}
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size} bytes) exceeds maximum allowed ({settings.MAX_UPLOAD_SIZE} bytes)",
        )

    # Create project-specific directory
    project_upload_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
    os.makedirs(project_upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(project_upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Compute checksum
    checksum = compute_checksum(file_path)

    # Determine source type
    source_type = get_source_type(file.filename)

    # Create source record
    source = Source(
        project_id=project_id,
        name=file.filename,
        type=source_type,
        file_path=file_path,
        file_size=file_size,
        checksum=checksum,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: UUID, db: Session = Depends(get_db)):
    """Get source metadata by ID."""
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID {source_id} not found",
        )

    return source


@router.get("/project/{project_id}", response_model=list[SourceResponse])
async def list_project_sources(project_id: UUID, db: Session = Depends(get_db)):
    """List all sources for a project."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    sources = db.query(Source).filter(Source.project_id == project_id).all()
    return sources


@router.delete("/{source_id}", response_model=MessageResponse)
async def delete_source(source_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a source and its file.

    Removes both the database record and the file from storage.
    """
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID {source_id} not found",
        )

    # Delete file from storage
    if os.path.exists(source.file_path):
        try:
            os.remove(source.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {source.file_path}: {e}")

    source_name = source.name
    db.delete(source)
    db.commit()

    return MessageResponse(
        message=f"Source '{source_name}' deleted successfully",
        data={"source_id": str(source_id)},
    )
