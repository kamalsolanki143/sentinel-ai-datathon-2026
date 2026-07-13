"""
Sentinel AI - Neo4j Graph Database Service
============================================
File: backend/services/neo4j_service.py
Purpose: Wrapper service for interacting with the Neo4j Knowledge Graph.
         Manages connection pooling and executes Cypher queries.

Dependencies: neo4j, loguru
"""

from typing import Any
from loguru import logger
from neo4j import AsyncGraphDatabase, AsyncDriver

from backend.config.settings import get_settings

settings = get_settings()


class Neo4jService:
    """Service managing Neo4j connections and queries."""

    def __init__(self) -> None:
        """Initialize connection parameters."""
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.driver: AsyncDriver | None = None

    async def connect(self) -> None:
        """Establish connection to Neo4j database."""
        if self.driver is not None:
            return
            
        logger.info(f"Connecting to Neo4j at {self.uri}")
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            # Verify connectivity
            await self.driver.verify_connectivity()
            logger.info("Neo4j connection established successfully")
        except Exception as exc:
            logger.error(f"Failed to connect to Neo4j: {str(exc)}")
            self.driver = None
            raise

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver is not None:
            logger.info("Closing Neo4j connection")
            await self.driver.close()
            self.driver = None

    async def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute a Cypher query and return results as a list of dictionaries.
        
        Args:
            query: The Cypher query to execute.
            parameters: Dictionary of parameters for the query.
            
        Returns:
            List of dictionaries representing the records.
        """
        if self.driver is None:
            await self.connect()
            
        params = parameters or {}
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                records = await result.data()
                return records
        except Exception as exc:
            logger.error(f"Error executing Cypher query: {str(exc)}\nQuery: {query}")
            raise

    async def check_health(self) -> bool:
        """Check Neo4j database connectivity."""
        if self.driver is None:
            try:
                await self.connect()
            except Exception:
                return False
                
        try:
            await self.driver.verify_connectivity()
            return True
        except Exception as exc:
            logger.error(f"Neo4j health check failed: {str(exc)}")
            return False


# Global service instance
neo4j_db = Neo4jService()
