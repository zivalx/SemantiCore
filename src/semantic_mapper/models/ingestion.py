"""
Data ingestion models.

These models represent the canonical intermediate format for all ingested data,
regardless of source type.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Supported data source types."""

    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"


class ProvenanceMetadata(BaseModel):
    """Tracks the origin and lineage of data."""

    source_id: UUID = Field(default_factory=uuid4)
    source_type: SourceType
    source_name: str
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = self.model_dump()
        data["source_id"] = str(data["source_id"])
        data["ingested_at"] = data["ingested_at"].isoformat()
        return data


class CanonicalRecord(BaseModel):
    """
    A single record extracted from a data source.
    This is the normalized intermediate representation.
    """

    record_id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    record_index: int
    raw_content: Dict[str, Any]
    structured_fields: Dict[str, Any] = Field(default_factory=dict)
    text_content: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = self.model_dump()
        data["record_id"] = str(data["record_id"])
        data["source_id"] = str(data["source_id"])
        data["extracted_at"] = data["extracted_at"].isoformat()
        return data


class IngestionResult(BaseModel):
    """Result of ingesting a data source."""

    provenance: ProvenanceMetadata
    records: List[CanonicalRecord]
    record_count: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @property
    def success(self) -> bool:
        """Whether ingestion was successful."""
        return len(self.errors) == 0 and self.record_count > 0


class DataSource(BaseModel):
    """Represents a data source that has been ingested."""

    source_id: UUID
    source_type: SourceType
    source_name: str
    description: Optional[str] = None
    ingested_at: datetime
    record_count: int
    status: str = "active"  # active, archived, deleted
