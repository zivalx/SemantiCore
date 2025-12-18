"""
Query operations.

Handles execution of queries against the instance graph.
Supports both Cypher queries and natural language queries (translated to Cypher).
"""

from typing import Any, Dict, List
from uuid import UUID

from .connection import Neo4jConnection


class QueryOperations:
    """Operations for querying the instance graph."""

    def __init__(self, connection: Neo4jConnection):
        self.conn = connection

    def execute_cypher(
        self, query: str, parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query results
        """
        return self.conn.execute_read(query, parameters)

    def get_ontology_schema_context(self, ontology_id: UUID) -> Dict[str, Any]:
        """
        Get schema context for query translation.

        Returns information about classes, relationships, and properties
        that can be used by LLM to translate natural language to Cypher.

        Args:
            ontology_id: ID of the ontology

        Returns:
            Schema context dictionary
        """
        # Get classes
        class_query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (o)-[:DEFINES]->(c:OntologyClass)
        RETURN c.name as name, c.label as label, c.description as description, c.properties as properties
        """

        classes = self.conn.execute_read(class_query, {"ontology_id": str(ontology_id)})

        # Get relationships
        rel_query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (o)-[:DEFINES]->(r:OntologyRelationType)
        RETURN r.name as name, r.label as label, r.description as description,
               r.source_class as source_class, r.target_class as target_class,
               r.properties as properties
        """

        relationships = self.conn.execute_read(rel_query, {"ontology_id": str(ontology_id)})

        return {
            "ontology_id": str(ontology_id),
            "classes": classes,
            "relationships": relationships,
        }

    def validate_query(self, query: str) -> tuple[bool, str]:
        """
        Validate a Cypher query without executing it.

        Args:
            query: Cypher query string

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Use EXPLAIN to validate without executing
            explain_query = f"EXPLAIN {query}"
            self.conn.execute_read(explain_query)
            return True, ""
        except Exception as e:
            return False, str(e)

    def get_sample_instances(
        self, ontology_id: UUID, class_name: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get sample instances for a class (useful for query building).

        Args:
            ontology_id: ID of the ontology
            class_name: Name of the class
            limit: Number of samples

        Returns:
            Sample instances
        """
        query = """
        MATCH (o:Ontology {ontology_id: $ontology_id})
        MATCH (c:OntologyClass {name: $class_name})
        WHERE (o)-[:DEFINES]->(c)
        MATCH (i:Instance)-[:INSTANCE_OF]->(c)
        RETURN i
        LIMIT $limit
        """

        params = {
            "ontology_id": str(ontology_id),
            "class_name": class_name,
            "limit": limit,
        }

        return self.conn.execute_read(query, params)

    def explain_query(self, query: str) -> Dict[str, Any]:
        """
        Get query execution plan.

        Args:
            query: Cypher query string

        Returns:
            Query plan information
        """
        explain_query = f"EXPLAIN {query}"
        return self.conn.execute_read(explain_query)
