"""
Semantic primitive models.

These represent candidate semantic elements extracted from data:
- Entities
- Attributes
- Relationships
- Evidence and confidence
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ConfidenceScore(BaseModel):
    """
    Represents confidence in a semantic assertion.

    Confidence is NOT a black box - it must be explainable.
    """

    score: float = Field(ge=0.0, le=1.0, description="Confidence value between 0 and 1")
    reasoning: str = Field(description="Human-readable explanation for this confidence")
    factors: Dict[str, float] = Field(
        default_factory=dict, description="Individual factors contributing to confidence"
    )

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0 and 1")
        return v


class SemanticEvidence(BaseModel):
    """
    Evidence linking a semantic assertion to source data.

    Every semantic decision must be traceable back to source data.
    """

    evidence_id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    record_id: UUID
    field_path: Optional[str] = None  # JSONPath or column name
    evidence_text: str
    evidence_type: str  # "direct", "inferred", "contextual"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EntityCandidate(BaseModel):
    """
    A candidate entity extracted from data.

    This is a PROPOSAL, not a fact.
    """

    candidate_id: UUID = Field(default_factory=uuid4)
    entity_type: str = Field(description="Proposed entity class name")
    entity_label: str = Field(description="Human-readable label for this specific entity")
    properties: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[SemanticEvidence] = Field(
        default_factory=list, description="Evidence supporting this entity"
    )
    confidence: ConfidenceScore
    alternatives: List[str] = Field(
        default_factory=list, description="Alternative entity types to consider"
    )
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = self.model_dump()
        data["candidate_id"] = str(data["candidate_id"])
        data["extracted_at"] = data["extracted_at"].isoformat()
        return data


class AttributeCandidate(BaseModel):
    """
    A candidate attribute for an entity or relationship.
    """

    candidate_id: UUID = Field(default_factory=uuid4)
    attribute_name: str
    attribute_type: str  # "string", "number", "boolean", "date", "uri", etc.
    entity_candidate_id: Optional[UUID] = None
    sample_values: List[Any] = Field(default_factory=list)
    evidence: List[SemanticEvidence] = Field(default_factory=list)
    confidence: ConfidenceScore
    is_required: bool = False
    is_unique: bool = False
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class RelationshipCandidate(BaseModel):
    """
    A candidate relationship between entities.
    """

    candidate_id: UUID = Field(default_factory=uuid4)
    relation_type: str = Field(description="Proposed relationship type name")
    source_entity_type: str
    target_entity_type: str
    source_entity_id: Optional[UUID] = None  # If linking to specific entity candidates
    target_entity_id: Optional[UUID] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[SemanticEvidence] = Field(default_factory=list)
    confidence: ConfidenceScore
    cardinality: str = "many-to-many"  # "one-to-one", "one-to-many", "many-to-one", "many-to-many"
    alternatives: List[str] = Field(
        default_factory=list, description="Alternative relationship types to consider"
    )
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = self.model_dump()
        data["candidate_id"] = str(data["candidate_id"])
        data["extracted_at"] = data["extracted_at"].isoformat()
        return data
