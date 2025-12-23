"""
Pydantic models for API responses.
"""

from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


class SourceResponse(BaseModel):
    """Source metadata response."""

    id: UUID
    name: str
    type: str
    file_size: Optional[int]
    uploaded_at: datetime
    canonical_record_count: int

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    """Project response."""

    id: UUID
    name: str
    domain: str
    description: Optional[str]
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    sources: list[SourceResponse] = []

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    """Job status response."""

    id: UUID
    project_id: UUID
    type: str
    status: str
    progress: float
    result: Optional[Any]
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PrimitiveResponse(BaseModel):
    """Semantic primitive response."""

    id: UUID
    project_id: UUID
    source_id: UUID
    label: str
    type: str
    evidence: Optional[str]
    confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class OntologyVersionResponse(BaseModel):
    """Ontology version response."""

    id: UUID
    project_id: UUID
    version: str
    neo4j_ontology_id: UUID
    is_accepted: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    message: str = "API is healthy"


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    data: Optional[Any] = None
