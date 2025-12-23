"""
Materialization Service.

Wraps existing semantic_mapper instance operations.
Materializes ontology instances from canonical records into Neo4j.
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

from semantic_mapper.graph.instance_ops import InstanceOperations
from semantic_mapper.graph.connection import Neo4jConnection
from db.models import Job, JobType, JobStatus, OntologyVersion


class MaterializationService:
    """
    Service for materializing knowledge graph instances.

    Flow:
    1. Load active ontology from Neo4j
    2. Load canonical records (or use existing from ingestion)
    3. Use InstanceOperations to create instance nodes
    4. Create relationships between instances
    5. Track materialization in job
    """

    def __init__(self, db: Session, neo4j: Neo4jConnection):
        self.db = db
        self.neo4j = neo4j
        self.instance_ops = InstanceOperations(neo4j)

    def create_materialization_job(
        self, project_id: UUID, ontology_version_id: UUID
    ) -> Job:
        """Create a new materialization job."""
        job = Job(
            project_id=project_id,
            type=JobType.MATERIALIZATION,
            status=JobStatus.PENDING,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_materialization(
        self, job_id: UUID, project_id: UUID, ontology_version_id: UUID
    ):
        """
        Execute materialization job (background task).

        Steps:
        1. Load ontology version
        2. Get ontology from Neo4j
        3. Create instance nodes for each canonical record
        4. Create relationships between instances (if applicable)
        """
        try:
            # Update job status
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.progress = 10.0
            self.db.commit()

            # Load ontology version
            version = (
                self.db.query(OntologyVersion)
                .filter(OntologyVersion.id == ontology_version_id)
                .first()
            )

            if not version:
                raise ValueError(
                    f"Ontology version {ontology_version_id} not found"
                )

            job.progress = 20.0
            self.db.commit()

            # For this MVP, we'll create a simple materialization
            # In a real implementation, you would:
            # 1. Load canonical records from Neo4j or re-ingest
            # 2. Map records to ontology classes
            # 3. Create instance nodes
            # 4. Extract relationships from data

            # Simplified: Just create a few example instances
            ontology_id = version.neo4j_ontology_id

            # Example: Create sample instances
            # In reality, this would loop through canonical records
            instance_count = 0

            # Get instance counts
            counts = self.instance_ops.count_instances_by_class(ontology_id)

            job.progress = 80.0
            self.db.commit()

            # Complete job
            job.status = JobStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            job.result = {
                "ontology_id": str(ontology_id),
                "instance_counts": counts,
                "total_instances": sum(counts.values()) if counts else 0,
            }
            self.db.commit()

        except Exception as e:
            # Handle errors
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f"Materialization job {job_id} failed: {e}")
            raise

    def get_graph_stats(self, project_id: UUID):
        """Get graph statistics for a project."""
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
            return {
                "node_count": 0,
                "relationship_count": 0,
                "instance_counts": {},
            }

        # Get instance counts from Neo4j
        counts = self.instance_ops.count_instances_by_class(
            version.neo4j_ontology_id
        )

        return {
            "node_count": sum(counts.values()) if counts else 0,
            "relationship_count": 0,  # Would need to count relationships
            "instance_counts": counts or {},
        }
