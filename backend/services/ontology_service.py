"""
Ontology Service.

Wraps existing semantic_mapper ontology generation and storage logic.
Generates formal ontologies from primitives and domain descriptions.
"""

from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime
import sys
import os

# Add paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
sys.path.append(os.path.join(backend_dir, "..", "src"))

from semantic_mapper.llm.base import BaseLLMProvider
from semantic_mapper.llm.ontology_proposer import OntologyProposer
from semantic_mapper.graph.ontology_ops import OntologyOperations
from semantic_mapper.graph.connection import Neo4jConnection
from semantic_mapper.models.ontology import Ontology
from db.models import (
    Job,
    JobType,
    JobStatus,
    Primitive,
    OntologyVersion,
    Project,
    Source,
)


class OntologyService:
    """
    Service for ontology generation and management.

    Flow:
    1. Load primitives and source data
    2. Use OntologyProposer to generate formal ontology
    3. Store ontology in Neo4j via OntologyOperations
    4. Create OntologyVersion record in PostgreSQL
    """

    def __init__(self, db: Session, neo4j: Neo4jConnection, llm: BaseLLMProvider):
        self.db = db
        self.neo4j = neo4j
        self.llm = llm
        self.ontology_proposer = OntologyProposer(llm)
        self.ontology_ops = OntologyOperations(neo4j)

    def create_ontology_job(self, project_id: UUID) -> Job:
        """Create a new ontology generation job."""
        job = Job(
            project_id=project_id,
            type=JobType.ONTOLOGY_GENERATION,
            status=JobStatus.PENDING,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_ontology_generation(
        self, job_id: UUID, project_id: UUID, domain_description: str
    ):
        """
        Execute ontology generation job (background task).

        Steps:
        1. Load primitives and source data
        2. Use existing OntologyProposer to generate ontology
        3. Store ontology in Neo4j
        4. Create OntologyVersion record in PostgreSQL
        """
        try:
            # Update job status
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.progress = 10.0
            self.db.commit()

            # Load primitives
            primitives = (
                self.db.query(Primitive).filter(Primitive.project_id == project_id).all()
            )

            # Load sources for data samples
            sources = (
                self.db.query(Source).filter(Source.project_id == project_id).all()
            )
            source_ids = [str(source.id) for source in sources]

            job.progress = 20.0
            self.db.commit()

            # Prepare data samples (simplified - would normally load canonical records)
            # For now, use primitives as evidence
            data_samples = [
                {"type": p.type, "label": p.label, "evidence": p.evidence}
                for p in primitives
            ]

            job.progress = 30.0
            self.db.commit()

            # Generate ontology proposal using existing OntologyProposer
            proposal = self.ontology_proposer.propose_ontology(
                domain_description=domain_description,
                data_samples=data_samples,
                source_ids=source_ids,
                iteration=1,
            )

            job.progress = 60.0
            self.db.commit()

            # Convert proposal to Ontology model
            ontology = self._proposal_to_ontology(proposal, project_id)

            # Store ontology in Neo4j
            self.ontology_ops.create_ontology(ontology)

            job.progress = 80.0
            self.db.commit()

            # Create OntologyVersion record in PostgreSQL
            project = self.db.query(Project).filter(Project.id == project_id).first()
            version_number = f"{project.version}.0.0"

            ontology_version = OntologyVersion(
                project_id=project_id,
                version=version_number,
                neo4j_ontology_id=ontology.id,
                is_accepted=False,
                is_active=False,
                generation_job_id=job_id,
            )

            self.db.add(ontology_version)

            # Complete job
            job.status = JobStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            job.result = {
                "ontology_version_id": str(ontology_version.id),
                "neo4j_ontology_id": str(ontology.id),
                "class_count": len(ontology.classes),
                "relation_count": len(ontology.relation_types),
            }
            self.db.commit()

        except Exception as e:
            # Handle errors
            job = self.db.query(Job).filter(Job.id == job_id).first()
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            print(f"Ontology generation job {job_id} failed: {e}")
            raise

    def _proposal_to_ontology(self, proposal, project_id: UUID) -> Ontology:
        """Convert OntologyProposal to Ontology model."""
        from semantic_mapper.models.ontology import (
            Ontology,
            OntologyClass,
            OntologyRelationType,
            OntologyProperty,
        )

        # Create ontology ID
        ontology_id = uuid4()

        # Convert class proposals to OntologyClass
        classes = []
        for class_prop in proposal.classes:
            properties = [
                OntologyProperty(
                    name=prop.name,
                    data_type=prop.data_type,
                    is_required=prop.is_required,
                    description=prop.description or "",
                )
                for prop in class_prop.properties
            ]

            ont_class = OntologyClass(
                name=class_prop.name,
                description=class_prop.description,
                properties=properties,
                constraints=[],
            )
            classes.append(ont_class)

        # Convert relation proposals to OntologyRelationType
        relation_types = []
        for rel_prop in proposal.relations:
            from semantic_mapper.models.ontology import RelationCardinality

            relation_type = OntologyRelationType(
                name=rel_prop.name,
                source_class=rel_prop.source_class,
                target_class=rel_prop.target_class,
                description=rel_prop.description,
                cardinality=RelationCardinality.MANY_TO_MANY,  # Default
                is_symmetric=rel_prop.is_symmetric,
            )
            relation_types.append(relation_type)

        # Create Ontology
        ontology = Ontology(
            id=ontology_id,
            name=f"Ontology for project {project_id}",
            description=proposal.reasoning,
            version="1.0.0",
            classes=classes,
            relation_types=relation_types,
        )

        return ontology

    def accept_version(self, version_id: UUID) -> OntologyVersion:
        """
        Accept and activate an ontology version.

        Marks the version as accepted and active.
        Deactivates any previously active versions for the project.
        """
        version = (
            self.db.query(OntologyVersion).filter(OntologyVersion.id == version_id).first()
        )

        if not version:
            raise ValueError(f"Ontology version {version_id} not found")

        # Deactivate all other versions for this project
        self.db.query(OntologyVersion).filter(
            OntologyVersion.project_id == version.project_id,
            OntologyVersion.id != version_id,
        ).update({"is_active": False})

        # Activate and accept this version
        version.is_accepted = True
        version.is_active = True

        # Update project status
        project = (
            self.db.query(Project).filter(Project.id == version.project_id).first()
        )
        project.status = "building"  # Ready for materialization

        self.db.commit()
        self.db.refresh(version)

        return version

    def get_active_ontology(self, project_id: UUID):
        """Get the active ontology for a project."""
        version = (
            self.db.query(OntologyVersion)
            .filter(
                OntologyVersion.project_id == project_id,
                OntologyVersion.is_active == True,
            )
            .first()
        )

        if not version:
            return None

        # Load ontology from Neo4j
        ontology = self.ontology_ops.get_ontology(version.neo4j_ontology_id)
        return {"version": version, "ontology": ontology}

    def list_versions(self, project_id: UUID):
        """List all ontology versions for a project."""
        versions = (
            self.db.query(OntologyVersion)
            .filter(OntologyVersion.project_id == project_id)
            .order_by(OntologyVersion.created_at.desc())
            .all()
        )
        return versions
