"""
Ontology API router.

Endpoints for ontology generation and management.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from api.dependencies import get_db, get_neo4j, get_llm
from api.models.requests import GenerateOntologyRequest, AcceptOntologyVersionRequest
from api.models.responses import JobResponse, OntologyVersionResponse, MessageResponse
from db.models import Project
from services.ontology_service import OntologyService

router = APIRouter()


@router.post("/generate", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_ontology(
    request: GenerateOntologyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    neo4j=Depends(get_neo4j),
    llm=Depends(get_llm),
):
    """
    Generate formal ontology from primitives and domain description.

    This is an async operation that:
    1. Loads extracted primitives
    2. Uses LLM (via OntologyProposer) to generate formal OWL-style ontology
    3. Stores ontology in Neo4j
    4. Creates OntologyVersion record in PostgreSQL

    Returns a job_id for polling status.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {request.project_id} not found",
        )

    # Create ontology service and job
    service = OntologyService(db, neo4j, llm)
    job = service.create_ontology_job(request.project_id)

    # Queue background task
    background_tasks.add_task(
        service.run_ontology_generation,
        job.id,
        request.project_id,
        request.domain_description,
    )

    return job


@router.get("/{project_id}/versions", response_model=List[OntologyVersionResponse])
async def list_ontology_versions(
    project_id: UUID,
    db: Session = Depends(get_db),
    neo4j=Depends(get_neo4j),
    llm=Depends(get_llm),
):
    """
    List all ontology versions for a project.

    Returns versions ordered by creation date (newest first).
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    service = OntologyService(db, neo4j, llm)
    versions = service.list_versions(project_id)

    return versions


@router.get("/{project_id}/active")
async def get_active_ontology(
    project_id: UUID,
    db: Session = Depends(get_db),
    neo4j=Depends(get_neo4j),
    llm=Depends(get_llm),
):
    """
    Get the active ontology for a project.

    Returns the ontology version marked as active, along with the
    full ontology structure from Neo4j (classes, relations, properties).
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    service = OntologyService(db, neo4j, llm)
    result = service.get_active_ontology(project_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active ontology found for project {project_id}",
        )

    # Convert ontology to dict for JSON response
    ontology = result["ontology"]
    version = result["version"]

    return {
        "version": {
            "id": str(version.id),
            "project_id": str(version.project_id),
            "version": version.version,
            "neo4j_ontology_id": str(version.neo4j_ontology_id),
            "is_accepted": version.is_accepted,
            "is_active": version.is_active,
            "created_at": version.created_at.isoformat(),
        },
        "ontology": {
            "id": str(ontology.id),
            "name": ontology.name,
            "version": ontology.version,
            "description": ontology.description,
            "classes": [
                {
                    "name": cls.name,
                    "description": cls.description,
                    "properties": [
                        {
                            "name": prop.name,
                            "data_type": prop.data_type,
                            "is_required": prop.is_required,
                            "description": prop.description,
                        }
                        for prop in cls.properties
                    ],
                }
                for cls in ontology.classes
            ],
            "relation_types": [
                {
                    "name": rel.name,
                    "source_class": rel.source_class,
                    "target_class": rel.target_class,
                    "description": rel.description,
                    "cardinality": rel.cardinality.value,
                    "is_symmetric": rel.is_symmetric,
                }
                for rel in ontology.relation_types
            ],
        },
    }


@router.post("/{version_id}/accept", response_model=OntologyVersionResponse)
async def accept_ontology_version(
    version_id: UUID,
    db: Session = Depends(get_db),
    neo4j=Depends(get_neo4j),
    llm=Depends(get_llm),
):
    """
    Accept and activate an ontology version.

    Marks the specified version as accepted and active.
    Deactivates any previously active versions for the project.
    Updates project status to 'building' (ready for materialization).
    """
    service = OntologyService(db, neo4j, llm)

    try:
        version = service.accept_version(version_id)
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
