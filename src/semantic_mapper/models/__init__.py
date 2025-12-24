"""
Core data models for SemantiCore.

These models define the semantic primitives and ontology structures
that form the foundation of the system.
"""

from .primitives import (
    EntityCandidate,
    AttributeCandidate,
    RelationshipCandidate,
    SemanticEvidence,
    ConfidenceScore,
)
from .ontology import (
    OntologyClass,
    OntologyRelationType,
    OntologyProperty,
    OntologyConstraint,
    Ontology,
    OntologyVersion,
    OntologyDiff,
)
from .ingestion import (
    SourceType,
    DataSource,
    CanonicalRecord,
    IngestionResult,
    ProvenanceMetadata,
)
from .proposal import (
    OntologyProposal,
    ClassProposal,
    RelationProposal,
    AlternativeInterpretation,
)
from .feedback import (
    FeedbackAction,
    FeedbackItem,
    FeedbackSession,
)

__all__ = [
    # Primitives
    "EntityCandidate",
    "AttributeCandidate",
    "RelationshipCandidate",
    "SemanticEvidence",
    "ConfidenceScore",
    # Ontology
    "OntologyClass",
    "OntologyRelationType",
    "OntologyProperty",
    "OntologyConstraint",
    "Ontology",
    "OntologyVersion",
    "OntologyDiff",
    # Ingestion
    "SourceType",
    "DataSource",
    "CanonicalRecord",
    "IngestionResult",
    "ProvenanceMetadata",
    # Proposal
    "OntologyProposal",
    "ClassProposal",
    "RelationProposal",
    "AlternativeInterpretation",
    # Feedback
    "FeedbackAction",
    "FeedbackItem",
    "FeedbackSession",
]
