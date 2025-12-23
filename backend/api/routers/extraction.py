"""
Extraction API router.

Endpoints for semantic primitive extraction.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from api.dependencies import get_db, get_llm
from api.models.responses import JobResponse, PrimitiveResponse, MessageResponse
from db.models import Project
from services.extraction_service import ExtractionService

router = APIRouter()


@router.post("/extract", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def extract_primitives(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    llm=Depends(get_llm),
):
    """
    Extract semantic primitives from project sources.

    This is an async operation that:
    1. Ingests all source files to canonical records
    2. Analyzes data patterns
    3. Uses LLM to extract entities, attributes, and relations
    4. Stores primitives in database

    Returns a job_id for polling status.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    # Create extraction service and job
    service = ExtractionService(db, llm)
    job = service.create_extraction_job(project_id)

    # Queue background task
    background_tasks.add_task(service.run_extraction, job.id, project_id)

    return job


@router.get("/primitives/{project_id}", response_model=List[PrimitiveResponse])
async def get_primitives(project_id: UUID, db: Session = Depends(get_db), llm=Depends(get_llm)):
    """
    Get extracted primitives for a project.

    Returns all semantic primitives (entities, attributes, relations)
    that have been extracted from the project's sources.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    service = ExtractionService(db, llm)
    primitives = service.get_primitives(project_id)

    return primitives
