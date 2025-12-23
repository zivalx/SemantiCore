"""
Materialization API router.

Endpoints for knowledge graph materialization.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from uuid import UUID

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from api.dependencies import get_db, get_neo4j
from api.models.requests import MaterializeGraphRequest
from api.models.responses import JobResponse
from db.models import Project
from services.materialization_service import MaterializationService

router = APIRouter()


@router.post("/materialize", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def materialize_graph(
    request: MaterializeGraphRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    neo4j=Depends(get_neo4j),
):
    """
    Materialize instance graph from canonical records.

    This is an async operation that:
    1. Loads the active ontology
    2. Loads canonical records
    3. Creates instance nodes in Neo4j
    4. Creates relationships between instances

    Returns a job_id for polling status.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {request.project_id} not found",
        )

    # Create materialization service and job
    service = MaterializationService(db, neo4j)
    job = service.create_materialization_job(
        request.project_id, request.ontology_version_id
    )

    # Queue background task
    background_tasks.add_task(
        service.run_materialization,
        job.id,
        request.project_id,
        request.ontology_version_id,
    )

    return job


@router.get("/stats/{project_id}")
async def get_graph_stats(
    project_id: UUID, db: Session = Depends(get_db), neo4j=Depends(get_neo4j)
):
    """
    Get graph statistics for a project.

    Returns node counts, relationship counts, and instance counts by class.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    service = MaterializationService(db, neo4j)
    stats = service.get_graph_stats(project_id)

    return stats
