"""
Instance graph operations.

Handles materialization of instance data according to an accepted ontology.
Instance nodes are linked to their ontology class definitions.
"""

from typing import Any, Dict, List
from uuid import UUID

from .connection import Neo4jConnection


class InstanceOperations:
    """Operations for managing instance data in Neo4j."""

    def __init__(self, connection: Neo4jConnection):
        self.conn = connection

    def materialize_entity(
        self,
        ontology_id: UUID,
        class_name: str,
        properties: Dict[str, Any],
        source_record_id: UUID = None,
    ) -> str:
        """
        Materialize an entity instance.

        Args:
            ontology_id: ID of the ontology this instance belongs to
            class_name: Name of the ontology class
            properties: Entity properties
            source_record_id: ID of source canonical record

        Returns:
            ID of created instance node
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (c:OntologyClass {name: $class_name})
        WHERE (o)-[:DEFINES]->(c)
        CREATE (i {properties})
        SET i:Instance
        SET i += {class_type: $class_name}
        SET i += {ontology_id: $ontology_id}
        SET i += {source_record_id: $source_record_id}
        CREATE (i)-[:INSTANCE_OF]->(c)
        RETURN elementId(i) as instance_id
        """

        params = {
            "ontology_id": str(ontology_id),
            "class_name": class_name,
            "properties": properties,
            "source_record_id": str(source_record_id) if source_record_id else None,
        }

        result = self.conn.execute_write(query, params)
        return result[0]["instance_id"]

    def materialize_relationship(
        self,
        ontology_id: UUID,
        relation_type: str,
        source_instance_id: str,
        target_instance_id: str,
        properties: Dict[str, Any] = None,
    ) -> str:
        """
        Materialize a relationship instance.

        Args:
            ontology_id: ID of the ontology
            relation_type: Name of the relation type
            source_instance_id: Element ID of source instance
            target_instance_id: Element ID of target instance
            properties: Relationship properties

        Returns:
            Element ID of created relationship
        """
        # Note: We use CALL {} because we need to work with elementId
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (rt:OntologyRelationType {name: $relation_type})
        WHERE (o)-[:DEFINES]->(rt)
        CALL {
            WITH $source_id as source_id, $target_id as target_id
            MATCH (source:Instance)
            WHERE elementId(source) = source_id
            MATCH (target:Instance)
            WHERE elementId(target) = target_id
            CREATE (source)-[r:RELATED {type: $relation_type}]->(target)
            SET r += $properties
            RETURN elementId(r) as rel_id
        }
        RETURN rel_id
        """

        params = {
            "ontology_id": str(ontology_id),
            "relation_type": relation_type,
            "source_id": source_instance_id,
            "target_id": target_instance_id,
            "properties": properties or {},
        }

        result = self.conn.execute_write(query, params)
        return result[0]["rel_id"]

    def get_instances_by_class(
        self, ontology_id: UUID, class_name: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve instances of a specific class.

        Args:
            ontology_id: ID of the ontology
            class_name: Name of the class
            limit: Maximum number of instances to return

        Returns:
            List of instance data
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (c:OntologyClass {name: $class_name})
        WHERE (o)-[:DEFINES]->(c)
        MATCH (i:Instance)-[:INSTANCE_OF]->(c)
        RETURN i, elementId(i) as instance_id
        LIMIT $limit
        """

        params = {
            "ontology_id": str(ontology_id),
            "class_name": class_name,
            "limit": limit,
        }

        return self.conn.execute_read(query, params)

    def get_instance_graph(
        self, ontology_id: UUID, max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Retrieve the instance graph for visualization.

        Args:
            ontology_id: ID of the ontology
            max_depth: Maximum relationship depth to traverse

        Returns:
            Graph data with nodes and relationships
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (i:Instance {ontology_id: $ontology_id})
        OPTIONAL MATCH path = (i)-[r:RELATED*1..$max_depth]-(other:Instance)
        WHERE other.ontology_id = $ontology_id
        RETURN i, r, other
        LIMIT 1000
        """

        params = {
            "ontology_id": str(ontology_id),
            "max_depth": max_depth,
        }

        return self.conn.execute_read(query, params)

    def count_instances_by_class(self, ontology_id: UUID) -> Dict[str, int]:
        """
        Count instances for each class in the ontology.

        Args:
            ontology_id: ID of the ontology

        Returns:
            Dictionary mapping class names to instance counts
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (c:OntologyClass)<-[:INSTANCE_OF]-(i:Instance)
        WHERE (o)-[:DEFINES]->(c)
        RETURN c.name as class_name, count(i) as instance_count
        """

        params = {"ontology_id": str(ontology_id)}
        results = self.conn.execute_read(query, params)

        return {r["class_name"]: r["instance_count"] for r in results}

    def clear_instances(self, ontology_id: UUID):
        """
        Clear all instance data for an ontology.

        Args:
            ontology_id: ID of the ontology
        """
        query = """
        MATCH (i:Instance {ontology_id: $ontology_id})
        DETACH DELETE i
        """

        self.conn.execute_write(query, {"ontology_id": str(ontology_id)})
