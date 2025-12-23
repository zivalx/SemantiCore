"""
Query Service.

Wraps existing semantic_mapper query translation and execution logic.
Translates natural language to Cypher and executes queries against Neo4j.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import sys
import os

# Add paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
sys.path.append(os.path.join(backend_dir, "..", "src"))

from semantic_mapper.llm.base import BaseLLMProvider
from semantic_mapper.llm.query_translator import QueryTranslator
from semantic_mapper.graph.query_ops import QueryOperations
from semantic_mapper.graph.connection import Neo4jConnection
from db.models import Job, JobType, JobStatus, OntologyVersion


class QueryService:
    """
    Service for query translation and execution.

    Flow:
    1. Translate natural language to Cypher using QueryTranslator
    2. Execute Cypher query against Neo4j
    3. Return structured results
    """

    def __init__(self, db: Session, neo4j: Neo4jConnection, llm: BaseLLMProvider):
        self.db = db
        self.neo4j = neo4j
        self.llm = llm
        self.query_translator = QueryTranslator(llm)
        self.query_ops = QueryOperations(neo4j)

    def translate_query(self, project_id: UUID, natural_language: str):
        """
        Translate natural language to Cypher query.

        Uses existing QueryTranslator with ontology schema context.
        """
        # Load active ontology
        version = (
            self.db.query(OntologyVersion)
            .filter(
                OntologyVersion.project_id == project_id,
                OntologyVersion.is_active == True,
            )
            .first()
        )

        if not version:
            raise ValueError(f"No active ontology found for project {project_id}")

        # Get ontology schema context
        schema = self.query_ops.get_ontology_schema_context(
            version.neo4j_ontology_id
        )

        # Get sample instances for context
        sample_instances = {}
        for class_name in schema.get("classes", []):
            samples = self.query_ops.get_sample_instances(
                version.neo4j_ontology_id, class_name, limit=3
            )
            sample_instances[class_name] = samples

        # Translate using existing QueryTranslator
        translation = self.query_translator.translate(
            natural_language_query=natural_language,
            ontology_schema=schema,
            sample_instances=sample_instances,
        )

        return {
            "natural_language": natural_language,
            "cypher_query": translation.cypher_query,
            "explanation": translation.explanation,
            "confidence": translation.confidence,
            "warnings": translation.warnings or [],
        }

    def create_query_job(self, project_id: UUID, cypher_query: str) -> Job:
        """Create a new query execution job."""
        job = Job(
            project_id=project_id,
            type=JobType.QUERY,
            status=JobStatus.PENDING,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_query(self, job_id: UUID, project_id: UUID, cypher_query: str):
        """
        Execute Cypher query (background task).

        Steps:
        1. Validate query
        2. Execute against Neo4j
        3. Return results
        """
        try:
            # Update job status
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.progress = 20.0
            self.db.commit()

            # Validate query
            is_valid = self.query_ops.validate_query(cypher_query)

            if not is_valid:
                raise ValueError(f"Invalid Cypher query: {cypher_query}")

            job.progress = 40.0
            self.db.commit()

            # Execute query
            results = self.query_ops.execute_cypher(cypher_query, {})

            job.progress = 80.0
            self.db.commit()

            # Complete job
            job.status = JobStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            job.result = {
                "cypher_query": cypher_query,
                "result_count": len(results),
                "results": results[:100],  # Limit to first 100 results
            }
            self.db.commit()

        except Exception as e:
            # Handle errors
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f"Query job {job_id} failed: {e}")
            raise
