"""
Pydantic models for API requests.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class CreateProjectRequest(BaseModel):
    """Request to create a new project."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    domain: str = Field(..., min_length=1, max_length=255, description="Domain context")
    description: str = Field(..., min_length=1, description="Domain description/framing")


class UpdateProjectRequest(BaseModel):
    """Request to update a project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ExtractPrimitivesRequest(BaseModel):
    """Request to extract semantic primitives."""

    project_id: UUID
    source_ids: Optional[list[UUID]] = None  # If None, extract from all sources


class GenerateOntologyRequest(BaseModel):
    """Request to generate ontology."""

    project_id: UUID
    domain_description: str
    primitive_ids: Optional[list[UUID]] = None  # If None, use all primitives


class AcceptOntologyVersionRequest(BaseModel):
    """Request to accept an ontology version."""

    version_id: UUID


class MaterializeGraphRequest(BaseModel):
    """Request to materialize graph."""

    project_id: UUID
    ontology_version_id: UUID


class TranslateQueryRequest(BaseModel):
    """Request to translate natural language to Cypher."""

    project_id: UUID
    natural_language: str = Field(..., min_length=1)


class ExecuteQueryRequest(BaseModel):
    """Request to execute Cypher query."""

    project_id: UUID
    cypher_query: str = Field(..., min_length=1)
