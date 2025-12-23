"""
Projects API router.

Endpoints for project CRUD operations.
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
from api.models.requests import CreateProjectRequest, UpdateProjectRequest
from api.models.responses import ProjectResponse, MessageResponse
from db.models import Project, ProjectStatus

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest, db: Session = Depends(get_db)
):
    """
    Create a new project.

    Creates a project in DRAFT status with version 1.
    """
    project = Project(
        name=request.name,
        domain=request.domain,
        description=request.description,
        status=ProjectStatus.DRAFT,
        version=1,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    """
    List all projects.

    Returns projects with their associated sources.
    """
    projects = db.query(Project).order_by(Project.updated_at.desc()).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific project by ID.

    Includes sources, but not jobs or primitives (use dedicated endpoints for those).
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID, request: UpdateProjectRequest, db: Session = Depends(get_db)
):
    """
    Update a project's metadata.

    Can update name, domain, and/or description.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    # Update fields if provided
    if request.name is not None:
        project.name = request.name
    if request.domain is not None:
        project.domain = request.domain
    if request.description is not None:
        project.description = request.description

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a project.

    Cascades to delete all sources, jobs, primitives, and ontology versions.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    project_name = project.name
    db.delete(project)
    db.commit()

    return MessageResponse(
        message=f"Project '{project_name}' deleted successfully",
        data={"project_id": str(project_id)},
    )
