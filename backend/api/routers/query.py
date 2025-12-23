"""
Query API router.

Endpoints for natural language query translation and execution.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from uuid import UUID

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(backend_dir)

from api.dependencies import get_db, get_neo4j, get_llm
from api.models.requests import TranslateQueryRequest, ExecuteQueryRequest
from api.models.responses import JobResponse
from db.models import Project
from services.query_service import QueryService

router = APIRouter()


@router.post("/translate")
async def translate_query(
    request: TranslateQueryRequest,
    db: Session = Depends(get_db),
    neo4j=Depends(get_neo4j),
    llm=Depends(get_llm),
):
    """
    Translate natural language to Cypher query.

    Uses LLM with ontology schema context to generate a valid Cypher query
    from natural language input.

    Returns the generated Cypher query, explanation, and confidence score.
    This is a synchronous operation (no job needed).
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {request.project_id} not found",
        )

    service = QueryService(db, neo4j, llm)

    try:
        translation = service.translate_query(
            request.project_id, request.natural_language
        )
        return translation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/execute", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_query(
    request: ExecuteQueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    neo4j=Depends(get_neo4j),
    llm=Depends(get_llm),
):
    """
    Execute Cypher query against the knowledge graph.

    This is an async operation for complex queries that may take time.

    Returns a job_id for polling status and results.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {request.project_id} not found",
        )

    service = QueryService(db, neo4j, llm)
    job = service.create_query_job(request.project_id, request.cypher_query)

    # Queue background task
    background_tasks.add_task(
        service.run_query, job.id, request.project_id, request.cypher_query
    )

    return job
