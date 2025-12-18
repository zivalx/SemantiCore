"""
Ontology models.

The ontology is a first-class artifact stored as a graph within Neo4j.
It supports versioning, diffs, and tracks rejected alternatives.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Supported data types for properties."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    URI = "uri"
    JSON = "json"


class OntologyProperty(BaseModel):
    """
    A property definition within the ontology.
    """

    property_id: UUID = Field(default_factory=uuid4)
    name: str
    data_type: DataType
    description: str
    is_required: bool = False
    is_unique: bool = False
    default_value: Optional[Any] = None
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    examples: List[Any] = Field(default_factory=list)


class OntologyConstraint(BaseModel):
    """
    A constraint within the ontology.
    """

    constraint_id: UUID = Field(default_factory=uuid4)
    constraint_type: str  # "uniqueness", "existence", "cardinality", "custom"
    description: str
    expression: str  # Cypher or logical expression
    applies_to: str  # class name or relationship type
    severity: str = "error"  # "error", "warning", "info"


class OntologyClass(BaseModel):
    """
    A class (entity type) definition in the ontology.

    This will be stored as a node in Neo4j with label "OntologyClass".
    """

    class_id: UUID = Field(default_factory=uuid4)
    name: str = Field(description="Class name (e.g., 'Person', 'Organization')")
    label: str = Field(description="Human-readable label")
    description: str = Field(description="Plain English description of what this class represents")
    properties: List[OntologyProperty] = Field(default_factory=list)
    parent_classes: List[str] = Field(
        default_factory=list, description="Names of parent classes (inheritance)"
    )
    examples: List[str] = Field(
        default_factory=list, description="Example instances of this class"
    )
    rationale: str = Field(
        default="", description="Why this class exists and what problem it solves"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j storage."""
        data = self.model_dump()
        data["class_id"] = str(data["class_id"])
        data["created_at"] = data["created_at"].isoformat()
        data["updated_at"] = data["updated_at"].isoformat()
        return data


class OntologyRelationType(BaseModel):
    """
    A relationship type definition in the ontology.

    This will be stored as a node in Neo4j with label "OntologyRelationType".
    """

    relation_id: UUID = Field(default_factory=uuid4)
    name: str = Field(description="Relationship type name (e.g., 'WORKS_FOR', 'LOCATED_IN')")
    label: str = Field(description="Human-readable label")
    description: str = Field(description="Plain English description of this relationship")
    source_class: str = Field(description="Name of the source entity class")
    target_class: str = Field(description="Name of the target entity class")
    properties: List[OntologyProperty] = Field(default_factory=list)
    cardinality: str = "many-to-many"
    is_symmetric: bool = False
    inverse_of: Optional[str] = None
    examples: List[str] = Field(
        default_factory=list, description="Example instances of this relationship"
    )
    rationale: str = Field(default="", description="Why this relationship type exists")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j storage."""
        data = self.model_dump()
        data["relation_id"] = str(data["relation_id"])
        data["created_at"] = data["created_at"].isoformat()
        data["updated_at"] = data["updated_at"].isoformat()
        return data


class Ontology(BaseModel):
    """
    Complete ontology definition.
    """

    ontology_id: UUID = Field(default_factory=uuid4)
    name: str
    version: str = "1.0.0"
    description: str
    domain: str = Field(description="Domain this ontology models (e.g., 'healthcare', 'e-commerce')")
    classes: List[OntologyClass] = Field(default_factory=list)
    relation_types: List[OntologyRelationType] = Field(default_factory=list)
    constraints: List[OntologyConstraint] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump()
        data["ontology_id"] = str(data["ontology_id"])
        data["created_at"] = data["created_at"].isoformat()
        data["updated_at"] = data["updated_at"].isoformat()
        return data


class OntologyVersion(BaseModel):
    """
    Represents a specific version of an ontology.
    """

    version_id: UUID = Field(default_factory=uuid4)
    ontology_id: UUID
    version_number: str
    parent_version_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"
    change_summary: str = ""
    is_accepted: bool = False
    acceptance_timestamp: Optional[datetime] = None


class ChangeType(str, Enum):
    """Types of changes in an ontology diff."""

    CLASS_ADDED = "class_added"
    CLASS_REMOVED = "class_removed"
    CLASS_MODIFIED = "class_modified"
    RELATION_ADDED = "relation_added"
    RELATION_REMOVED = "relation_removed"
    RELATION_MODIFIED = "relation_modified"
    PROPERTY_ADDED = "property_added"
    PROPERTY_REMOVED = "property_removed"
    PROPERTY_MODIFIED = "property_modified"


class OntologyChange(BaseModel):
    """A single change in an ontology diff."""

    change_type: ChangeType
    element_name: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    rationale: str = ""


class OntologyDiff(BaseModel):
    """
    Represents differences between two ontology versions.
    """

    from_version: str
    to_version: str
    changes: List[OntologyChange] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def has_breaking_changes(self) -> bool:
        """Check if diff contains breaking changes."""
        breaking_types = {
            ChangeType.CLASS_REMOVED,
            ChangeType.RELATION_REMOVED,
            ChangeType.PROPERTY_REMOVED,
        }
        return any(change.change_type in breaking_types for change in self.changes)
