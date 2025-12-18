"""
Semantic extraction module.

Extracts semantic candidates (entities, attributes, relationships) from canonical records.
This is a lightweight module - the heavy lifting is done by the LLM in ontology proposal.
"""

from .extractor import SemanticExtractor

__all__ = ["SemanticExtractor"]
