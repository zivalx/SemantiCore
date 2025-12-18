"""
Ontology graph operations.

The ontology itself is stored as a graph within Neo4j:
- Ontology nodes represent ontology versions
- OntologyClass nodes represent entity classes
- OntologyRelationType nodes represent relationship types
- Relationships connect these elements
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .connection import Neo4jConnection
from ..models.ontology import (
    Ontology,
    OntologyClass,
    OntologyRelationType,
    OntologyVersion,
    OntologyDiff,
    OntologyChange,
    ChangeType,
)


class OntologyOperations:
    """Operations for managing ontology in Neo4j."""

    def __init__(self, connection: Neo4jConnection):
        self.conn = connection

    def initialize_schema(self):
        """
        Initialize the ontology schema in Neo4j.

        Creates constraints and indexes for ontology nodes.
        """
        # Create constraints
        constraints = [
            "CREATE CONSTRAINT ontology_id IF NOT EXISTS FOR (o:Ontology) REQUIRE o.ontology_id IS UNIQUE",
            "CREATE CONSTRAINT class_id IF NOT EXISTS FOR (c:OntologyClass) REQUIRE c.class_id IS UNIQUE",
            "CREATE CONSTRAINT relation_id IF NOT EXISTS FOR (r:OntologyRelationType) REQUIRE r.relation_id IS UNIQUE",
            "CREATE CONSTRAINT version_id IF NOT EXISTS FOR (v:OntologyVersion) REQUIRE v.version_id IS UNIQUE",
        ]

        for constraint in constraints:
            try:
                self.conn.execute_write(constraint)
            except Exception as e:
                # Constraint might already exist
                pass

        # Create indexes for common queries
        indexes = [
            "CREATE INDEX ontology_name IF NOT EXISTS FOR (o:Ontology) ON (o.name)",
            "CREATE INDEX class_name IF NOT EXISTS FOR (c:OntologyClass) ON (c.name)",
            "CREATE INDEX relation_name IF NOT EXISTS FOR (r:OntologyRelationType) ON (r.name)",
        ]

        for index in indexes:
            try:
                self.conn.execute_write(index)
            except Exception:
                pass

    def create_ontology(self, ontology: Ontology) -> UUID:
        """
        Create a new ontology in the graph.

        Args:
            ontology: Ontology model

        Returns:
            UUID of created ontology
        """
        # Create ontology node
        query = """
        CREATE (o:Ontology {
            ontology_id: $ontology_id,
            name: $name,
            version: $version,
            description: $description,
            domain: $domain,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        RETURN o.ontology_id as ontology_id
        """

        params = {
            "ontology_id": str(ontology.ontology_id),
            "name": ontology.name,
            "version": ontology.version,
            "description": ontology.description,
            "domain": ontology.domain,
            "created_at": ontology.created_at.isoformat(),
            "updated_at": ontology.updated_at.isoformat(),
        }

        result = self.conn.execute_write(query, params)

        # Create version node
        version = OntologyVersion(
            ontology_id=ontology.ontology_id,
            version_number=ontology.version,
            created_at=ontology.created_at,
            is_accepted=False,
        )
        self._create_version(version)

        # Create classes
        for cls in ontology.classes:
            self.create_class(ontology.ontology_id, cls)

        # Create relation types
        for rel in ontology.relation_types:
            self.create_relation_type(ontology.ontology_id, rel)

        return ontology.ontology_id

    def create_class(self, ontology_id: UUID, cls: OntologyClass) -> UUID:
        """
        Create an ontology class node.

        Args:
            ontology_id: ID of parent ontology
            cls: OntologyClass model

        Returns:
            UUID of created class
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        CREATE (c:OntologyClass {
            class_id: $class_id,
            name: $name,
            label: $label,
            description: $description,
            properties: $properties,
            parent_classes: $parent_classes,
            examples: $examples,
            rationale: $rationale,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (o)-[:DEFINES]->(c)
        RETURN c.class_id as class_id
        """

        params = {
            "ontology_id": str(ontology_id),
            "class_id": str(cls.class_id),
            "name": cls.name,
            "label": cls.label,
            "description": cls.description,
            "properties": [p.model_dump() for p in cls.properties],
            "parent_classes": cls.parent_classes,
            "examples": cls.examples,
            "rationale": cls.rationale,
            "created_at": cls.created_at.isoformat(),
            "updated_at": cls.updated_at.isoformat(),
        }

        result = self.conn.execute_write(query, params)
        return UUID(result[0]["class_id"])

    def create_relation_type(
        self, ontology_id: UUID, relation: OntologyRelationType
    ) -> UUID:
        """
        Create an ontology relation type node.

        Args:
            ontology_id: ID of parent ontology
            relation: OntologyRelationType model

        Returns:
            UUID of created relation type
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (source:OntologyClass {name: $source_class})
        WHERE (o)-[:DEFINES]->(source)
        MATCH (target:OntologyClass {name: $target_class})
        WHERE (o)-[:DEFINES]->(target)
        CREATE (r:OntologyRelationType {
            relation_id: $relation_id,
            name: $name,
            label: $label,
            description: $description,
            source_class: $source_class,
            target_class: $target_class,
            properties: $properties,
            cardinality: $cardinality,
            is_symmetric: $is_symmetric,
            inverse_of: $inverse_of,
            examples: $examples,
            rationale: $rationale,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        CREATE (o)-[:DEFINES]->(r)
        CREATE (source)-[:CAN_RELATE_VIA]->(r)-[:TARGETS]->(target)
        RETURN r.relation_id as relation_id
        """

        params = {
            "ontology_id": str(ontology_id),
            "relation_id": str(relation.relation_id),
            "name": relation.name,
            "label": relation.label,
            "description": relation.description,
            "source_class": relation.source_class,
            "target_class": relation.target_class,
            "properties": [p.model_dump() for p in relation.properties],
            "cardinality": relation.cardinality,
            "is_symmetric": relation.is_symmetric,
            "inverse_of": relation.inverse_of,
            "examples": relation.examples,
            "rationale": relation.rationale,
            "created_at": relation.created_at.isoformat(),
            "updated_at": relation.updated_at.isoformat(),
        }

        result = self.conn.execute_write(query, params)
        return UUID(result[0]["relation_id"])

    def get_ontology(self, ontology_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve an ontology by ID.

        Args:
            ontology_id: Ontology UUID

        Returns:
            Ontology data as dictionary, or None if not found
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        OPTIONAL MATCH (o)-[:DEFINES]->(c:OntologyClass)
        OPTIONAL MATCH (o)-[:DEFINES]->(r:OntologyRelationType)
        RETURN o, collect(DISTINCT c) as classes, collect(DISTINCT r) as relations
        """

        result = self.conn.execute_read(query, {"ontology_id": str(ontology_id)})
        if not result:
            return None

        return result[0]

    def list_ontologies(self) -> List[Dict[str, Any]]:
        """
        List all ontologies.

        Returns:
            List of ontology summaries
        """
        query = """
        MATCH (o:Ontology)
        OPTIONAL MATCH (o)-[:DEFINES]->(c:OntologyClass)
        OPTIONAL MATCH (o)-[:DEFINES]->(r:OntologyRelationType)
        RETURN o, count(DISTINCT c) as class_count, count(DISTINCT r) as relation_count
        ORDER BY o.created_at DESC
        """

        return self.conn.execute_read(query)

    def _create_version(self, version: OntologyVersion):
        """Create a version node."""
        query = """
        CREATE (v:OntologyVersion {
            version_id: $version_id,
            ontology_id: $ontology_id,
            version_number: $version_number,
            parent_version_id: $parent_version_id,
            created_at: datetime($created_at),
            created_by: $created_by,
            change_summary: $change_summary,
            is_accepted: $is_accepted,
            acceptance_timestamp: $acceptance_timestamp
        })
        """

        params = {
            "version_id": str(version.version_id),
            "ontology_id": str(version.ontology_id),
            "version_number": version.version_number,
            "parent_version_id": str(version.parent_version_id) if version.parent_version_id else None,
            "created_at": version.created_at.isoformat(),
            "created_by": version.created_by,
            "change_summary": version.change_summary,
            "is_accepted": version.is_accepted,
            "acceptance_timestamp": version.acceptance_timestamp.isoformat() if version.acceptance_timestamp else None,
        }

        self.conn.execute_write(query, params)

    def accept_ontology(self, ontology_id: UUID, version: str):
        """Mark an ontology version as accepted."""
        query = """
        MATCH (v:OntologyVersion {ontology_id: $ontology_id, version_number: $version})
        SET v.is_accepted = true, v.acceptance_timestamp = datetime()
        """

        self.conn.execute_write(query, {
            "ontology_id": str(ontology_id),
            "version": version,
        })
