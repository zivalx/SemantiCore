"""Neo4j connection management."""

import os
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Driver, Session


class Neo4jConnection:
    """
    Manages connection to Neo4j database.

    This is a thin wrapper around the Neo4j driver that provides
    a consistent interface for database operations.
    """

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j connection.

        Args:
            uri: Neo4j URI (default: from NEO4J_URI env var)
            user: Neo4j username (default: from NEO4J_USER env var)
            password: Neo4j password (default: from NEO4J_PASSWORD env var)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")

        self._driver: Optional[Driver] = None

    def connect(self) -> Driver:
        """Establish connection to Neo4j."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
        return self._driver

    def close(self):
        """Close connection to Neo4j."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def verify_connectivity(self) -> bool:
        """
        Verify connection to Neo4j.

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            driver = self.connect()
            driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False

    def execute_query(
        self,
        query: str,
        parameters: Dict[str, Any] = None,
        database: str = "neo4j"
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name

        Returns:
            List of result records as dictionaries
        """
        driver = self.connect()
        with driver.session(database=database) as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def execute_write(
        self,
        query: str,
        parameters: Dict[str, Any] = None,
        database: str = "neo4j"
    ) -> List[Dict[str, Any]]:
        """
        Execute a write query in a transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name

        Returns:
            List of result records as dictionaries
        """
        driver = self.connect()

        def _execute_write_tx(tx):
            result = tx.run(query, parameters or {})
            return [dict(record) for record in result]

        with driver.session(database=database) as session:
            return session.execute_write(_execute_write_tx)

    def execute_read(
        self,
        query: str,
        parameters: Dict[str, Any] = None,
        database: str = "neo4j"
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query in a transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name

        Returns:
            List of result records as dictionaries
        """
        driver = self.connect()

        def _execute_read_tx(tx):
            result = tx.run(query, parameters or {})
            return [dict(record) for record in result]

        with driver.session(database=database) as session:
            return session.execute_read(_execute_read_tx)

    def clear_database(self, database: str = "neo4j"):
        """
        Clear all nodes and relationships from the database.

        WARNING: This is destructive!
        """
        query = "MATCH (n) DETACH DELETE n"
        self.execute_write(query, database=database)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
