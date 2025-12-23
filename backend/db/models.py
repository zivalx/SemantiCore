"""
SQLAlchemy ORM models for PostgreSQL database.

Defines tables for:
- Projects
- Sources (uploaded files)
- Jobs (async operations)
- Primitives (extracted semantic primitives)
- OntologyVersions (ontology proposals and versions)
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Float,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4
import enum

from .connection import Base


# Enums
class ProjectStatus(str, enum.Enum):
    """Project lifecycle status."""

    DRAFT = "draft"
    BUILDING = "building"
    COMPLETE = "complete"


class SourceType(str, enum.Enum):
    """Supported source file types."""

    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"


class JobType(str, enum.Enum):
    """Types of async jobs."""

    INGESTION = "ingestion"
    EXTRACTION = "extraction"
    ONTOLOGY_GENERATION = "ontology_generation"
    MATERIALIZATION = "materialization"
    QUERY = "query"


class JobStatus(str, enum.Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PrimitiveType(str, enum.Enum):
    """Semantic primitive types."""

    ENTITY = "entity"
    ATTRIBUTE = "attribute"
    RELATION = "relation"


# ORM Models


class Project(Base):
    """
    Project model.

    A project represents a complete semantic mapping workflow,
    including data sources, ontology, and materialized graph.
    """

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    sources = relationship(
        "Source", back_populates="project", cascade="all, delete-orphan"
    )
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")
    primitives = relationship(
        "Primitive", back_populates="project", cascade="all, delete-orphan"
    )
    ontology_versions = relationship(
        "OntologyVersion", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status={self.status})>"


class Source(Base):
    """
    Data source model.

    Represents an uploaded file that has been ingested into canonical records.
    """

    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # File metadata
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(SourceType), nullable=False)
    file_path = Column(String(512), nullable=False)  # Path in storage
    file_size = Column(BigInteger)  # Size in bytes
    checksum = Column(String(64))  # SHA256 checksum

    # Ingestion tracking
    canonical_record_count = Column(Integer, default=0)
    ingestion_job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    # Timestamps
    uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="sources")
    primitives = relationship("Primitive", back_populates="source")

    __table_args__ = (Index("idx_sources_project", "project_id"),)

    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', type={self.type})>"


class Job(Base):
    """
    Async job model.

    Tracks background operations like extraction, ontology generation,
    materialization, and query execution.
    """

    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # Job metadata
    type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    progress = Column(Float, default=0.0)  # 0-100

    # Results and errors
    result = Column(JSONB, nullable=True)  # Structured result data
    error = Column(Text, nullable=True)  # Error message if failed

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="jobs")

    __table_args__ = (
        Index("idx_jobs_project", "project_id"),
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_type", "type"),
    )

    def __repr__(self):
        return f"<Job(id={self.id}, type={self.type}, status={self.status})>"


class Primitive(Base):
    """
    Semantic primitive model.

    Represents extracted entities, attributes, or relations from source data.
    """

    __tablename__ = "primitives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )

    # Primitive metadata
    label = Column(String(255), nullable=False)
    type = Column(SQLEnum(PrimitiveType), nullable=False)
    evidence = Column(Text)  # Source quote or reference
    confidence = Column(Float)  # 0-1 confidence score

    # Tracking
    extraction_job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="primitives")
    source = relationship("Source", back_populates="primitives")

    __table_args__ = (
        Index("idx_primitives_project", "project_id"),
        Index("idx_primitives_source", "source_id"),
        Index("idx_primitives_type", "type"),
    )

    def __repr__(self):
        return f"<Primitive(id={self.id}, label='{self.label}', type={self.type})>"


class OntologyVersion(Base):
    """
    Ontology version model.

    Tracks proposed and accepted ontologies for a project.
    Links to Neo4j ontology nodes.
    """

    __tablename__ = "ontology_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # Version metadata
    version = Column(String(50), nullable=False)  # e.g., "1.0.0"
    neo4j_ontology_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # Reference to Neo4j Ontology node

    # Status flags
    is_accepted = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)

    # Tracking
    generation_job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="ontology_versions")

    __table_args__ = (
        Index("idx_ontology_project", "project_id"),
        Index("idx_ontology_active", "is_active"),
    )

    def __repr__(self):
        return f"<OntologyVersion(id={self.id}, version='{self.version}', active={self.is_active})>"
