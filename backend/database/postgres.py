from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.config.settings import get_settings
from backend.database.models import Base

settings = get_settings()


def get_engine():
    """Get or create the async SQLAlchemy engine dynamically."""
    settings.validate_database_config()
    db_url = settings.DATABASE_URL
    return create_async_engine(
        db_url,
        echo=False,
        future=True,
        pool_pre_ping=True
    )


# Engine and session factory
engine = get_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency to get session on requests
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Initialize database schemas (called during application startup)
async def init_db() -> None:
    """Validate configuration, verify connectivity, and initialize schemas."""
    settings.validate_database_config()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL database connection verified and schemas initialized.")
    except Exception as exc:
        exc_str = str(exc)
        if "InvalidPasswordError" in exc_str or "password authentication failed" in exc_str:
            err_msg = (
                f"\n{'='*75}\n"
                f"POSTGRESQL AUTHENTICATION FAILED: Password authentication failed for user '{settings.POSTGRES_USER}'.\n\n"
                f"Details: {exc_str}\n\n"
                f"Please update your '.env' file with the correct POSTGRES_USER and POSTGRES_PASSWORD.\n"
                f"{'='*75}\n"
            )
            logger.error(err_msg)
            raise RuntimeError(err_msg) from exc
        else:
            logger.error(f"PostgreSQL initialization failed: {exc_str}")
            raise


# Compatibility alias for main.py startup invocation
init_postgres_db = init_db
