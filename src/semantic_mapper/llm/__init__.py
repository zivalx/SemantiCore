"""
LLM integration module.

Handles interactions with LLM APIs for:
- Ontology proposal generation
- Query translation
- Semantic extraction

All LLM outputs must be structured JSON - no black box reasoning.
"""

from .base import BaseLLMProvider
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider
from .factory import LLMFactory
from .ontology_proposer import OntologyProposer
from .query_translator import QueryTranslator

__all__ = [
    "BaseLLMProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "LLMFactory",
    "OntologyProposer",
    "QueryTranslator",
]
