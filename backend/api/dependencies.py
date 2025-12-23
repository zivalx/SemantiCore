"""
Shared dependencies for FastAPI routes.

Provides dependency injection for:
- Database sessions
- Neo4j connections
- LLM providers
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator
import sys
import os

# Add paths for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
sys.path.append(os.path.join(backend_dir, "..", "src"))

from db.connection import get_db as _get_db
from semantic_mapper.graph.connection import Neo4jConnection
from semantic_mapper.llm.factory import LLMFactory
from config import settings

# Re-export database dependency
get_db = _get_db


def get_neo4j() -> Generator[Neo4jConnection, None, None]:
    """
    Dependency to get Neo4j connection.

    Usage:
        @router.get("/")
        def endpoint(neo4j: Neo4jConnection = Depends(get_neo4j)):
            ...
    """
    connection = Neo4jConnection(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD,
    )
    try:
        connection.connect()
        yield connection
    finally:
        connection.close()


def get_llm():
    """
    Dependency to get LLM provider.

    Usage:
        @router.post("/generate")
        def endpoint(llm = Depends(get_llm)):
            ...
    """
    if settings.LLM_PROVIDER == "anthropic":
        return LLMFactory.create_anthropic(
            api_key=settings.ANTHROPIC_API_KEY, model=settings.ANTHROPIC_MODEL
        )
    elif settings.LLM_PROVIDER == "openai":
        return LLMFactory.create_openai(
            api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
