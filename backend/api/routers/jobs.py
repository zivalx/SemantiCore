"""
Jobs API router.

Endpoints for polling async job status.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from api.dependencies import get_db
from api.models.responses import JobResponse
from db.models import Job

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    """
    Get job status by ID.

    Use this endpoint to poll for job completion.
    Job status will be one of: pending, running, completed, failed
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )

    return job


@router.get("/project/{project_id}", response_model=List[JobResponse])
async def list_project_jobs(
    project_id: UUID,
    job_type: str = None,
    job_status: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List jobs for a project.

    Optional filters:
    - job_type: Filter by job type (extraction, ontology_generation, etc.)
    - job_status: Filter by status (pending, running, completed, failed)
    - limit: Max number of results (default 50)
    - offset: Pagination offset (default 0)
    """
    query = db.query(Job).filter(Job.project_id == project_id)

    if job_type:
        query = query.filter(Job.type == job_type)

    if job_status:
        query = query.filter(Job.status == job_status)

    jobs = (
        query.order_by(Job.created_at.desc()).limit(limit).offset(offset).all()
    )

    return jobs
