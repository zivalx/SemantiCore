"""
Ontology proposal models.

These represent LLM-generated proposals for ontology elements.
LLMs propose — humans decide.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .ontology import OntologyClass, OntologyRelationType
from .primitives import ConfidenceScore


class AlternativeInterpretation(BaseModel):
    """
    An alternative way to model something in the ontology.

    Represents uncertainty and multiple valid approaches.
    """

    interpretation_id: UUID = Field(default_factory=uuid4)
    description: str
    rationale: str
    tradeoffs: Dict[str, str] = Field(
        default_factory=dict, description="Pros and cons of this interpretation"
    )
    confidence: ConfidenceScore


class ClassProposal(BaseModel):
    """
    A proposed ontology class from the LLM.
    """

    proposal_id: UUID = Field(default_factory=uuid4)
    proposed_class: OntologyClass
    plain_english_explanation: str = Field(
        description="Simple explanation of what this class represents and why it's needed"
    )
    confidence: ConfidenceScore
    open_questions: List[str] = Field(
        default_factory=list, description="Unresolved questions about this class"
    )
    alternatives: List[AlternativeInterpretation] = Field(
        default_factory=list, description="Alternative ways to model this"
    )
    source_evidence_ids: List[UUID] = Field(
        default_factory=list, description="IDs of evidence supporting this proposal"
    )
    proposed_at: datetime = Field(default_factory=datetime.utcnow)


class RelationProposal(BaseModel):
    """
    A proposed relationship type from the LLM.
    """

    proposal_id: UUID = Field(default_factory=uuid4)
    proposed_relation: OntologyRelationType
    plain_english_explanation: str = Field(
        description="Simple explanation of what this relationship means and why it's needed"
    )
    confidence: ConfidenceScore
    open_questions: List[str] = Field(
        default_factory=list, description="Unresolved questions about this relationship"
    )
    alternatives: List[AlternativeInterpretation] = Field(
        default_factory=list, description="Alternative ways to model this relationship"
    )
    source_evidence_ids: List[UUID] = Field(
        default_factory=list, description="IDs of evidence supporting this proposal"
    )
    proposed_at: datetime = Field(default_factory=datetime.utcnow)


class OntologyProposal(BaseModel):
    """
    A complete ontology proposal from the LLM.

    This is what gets presented to the human for review.
    """

    proposal_id: UUID = Field(default_factory=uuid4)
    ontology_name: str
    domain_description: str
    version: str = "1.0.0"
    class_proposals: List[ClassProposal] = Field(default_factory=list)
    relation_proposals: List[RelationProposal] = Field(default_factory=list)
    overall_explanation: str = Field(
        description="High-level explanation of the entire ontology structure"
    )
    modeling_decisions: Dict[str, str] = Field(
        default_factory=dict,
        description="Key modeling decisions made and their justifications",
    )
    open_questions: List[str] = Field(
        default_factory=list, description="Questions that need human input"
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Assumptions made during proposal generation"
    )
    confidence: ConfidenceScore
    proposed_at: datetime = Field(default_factory=datetime.utcnow)
    based_on_source_ids: List[UUID] = Field(
        default_factory=list, description="Data sources used for this proposal"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump()
        data["proposal_id"] = str(data["proposal_id"])
        data["proposed_at"] = data["proposed_at"].isoformat()
        return data
