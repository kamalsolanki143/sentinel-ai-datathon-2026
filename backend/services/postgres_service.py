"""
Sentinel AI - PostgreSQL Database Service
===========================================
File: backend/services/postgres_service.py
Purpose: Async SQLAlchemy setup for connecting to PostgreSQL.
         Provides session management and database connection pooling.

Dependencies: sqlalchemy, asyncpg, loguru
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from backend.config.settings import get_settings
from backend.database.models import Base

settings = get_settings()


class PostgresService:
    """Service managing PostgreSQL connections via async SQLAlchemy."""

    def __init__(self) -> None:
        """Initialize the async engine and session maker."""
        self.engine: AsyncEngine | None = None
        self.async_session_maker: async_sessionmaker[AsyncSession] | None = None
        
    def setup(self) -> None:
        """Configure the engine and connection pool."""
        logger.info(f"Setting up PostgreSQL engine for {settings.POSTGRES_DB}")
        
        # Avoid creating multiple engines if already setup
        if self.engine is not None:
            return
            
        try:
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
            )
            
            self.async_session_maker = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info("PostgreSQL engine initialized successfully")
        except Exception as exc:
            logger.error(f"Failed to initialize PostgreSQL engine: {str(exc)}")
            raise

    async def close(self) -> None:
        """Close the database engine."""
        if self.engine is not None:
            logger.info("Closing PostgreSQL engine")
            await self.engine.dispose()
            self.engine = None
            self.async_session_maker = None

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional scope around a series of operations."""
        if self.async_session_maker is None:
            self.setup()
            
        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Transaction rollback due to error: {str(exc)}")
            raise
        finally:
            await session.close()

    async def check_health(self) -> bool:
        """Check database connectivity."""
        if self.engine is None:
            self.setup()
            
        try:
            from sqlalchemy import text
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            logger.error(f"Database health check failed: {str(exc)}")
            return False


# Global service instance
postgres_db = PostgresService()

# FastAPI dependency for getting DB sessions
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for FastAPI routers."""
    async with postgres_db.get_session() as session:
        yield session
