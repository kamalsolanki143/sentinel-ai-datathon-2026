"""
Sentinel AI - Main FastAPI Application
File: backend/main.py
Purpose: FastAPI entry point. Configures routers, CORS, exception handling,
         logging, and application startup/shutdown events.

Dependencies: fastapi, uvicorn, loguru, backend.api.*, backend.database.*
"""

import sys
from pathlib import Path

# Automatically ensure project root is in sys.path
_file_path = Path(__file__).resolve()
_project_root = _file_path.parent.parent
_backend_dir = _file_path.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config.settings import get_settings
from backend.config.config import APP_METADATA
from backend.config.logging_config import setup_logging
from backend.database.postgres import init_postgres_db, AsyncSessionLocal
from backend.database.neo4j import close_neo4j_driver
from backend.services.pipeline import sync_postgres_to_neo4j

# Load settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager (Startup and Shutdown events).
    """
    # --- Startup ---
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode...")
    
    # Validate database credentials
    settings.validate_database_config()

    # Initialize PostgreSQL Database
    await init_postgres_db()

    # Pre-synchronize Postgres with Neo4j if Neo4j is available
    async with AsyncSessionLocal() as session:
        try:
            await sync_postgres_to_neo4j(session)
            logger.info("Successfully synchronized PostgreSQL records with Neo4j on startup.")
        except Exception as e:
            logger.warning(f"Warning: Neo4j pre-sync skipped on startup: {e} (Verify Neo4j is running)")

    logger.info("Sentinel AI Core Systems initialized successfully.")
    
    yield
    
    # --- Shutdown ---
    logger.info("Shutting down Sentinel AI Core Systems...")
    await close_neo4j_driver()
    logger.info("Shutdown complete.")


def create_app() -> FastAPI:
    """Factory function to create the FastAPI application instance."""
    app = FastAPI(
        title=APP_METADATA["title"],
        description=APP_METADATA["description"],
        version=APP_METADATA["version"],
        contact=APP_METADATA["contact"],
        lifespan=lifespan,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Setup CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Global Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Global exception caught for {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred processing your request.",
                "details": str(exc) if settings.DEBUG else None
            },
        )

    # System Health Check Endpoint
    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, Any]:
        """Simple health check endpoint to verify API is running."""
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION,
        }

    # Register All Subsystem Routers
    from backend.api.auth import router as auth_router
    from backend.api.chat import router as chat_router
    from backend.api.crimes import router as crimes_router
    from backend.api.network import router as network_router
    from backend.api.predictions import router as predictions_router
    from backend.api.recommendations import router as recommendations_router
    from backend.api.reports import router as reports_router
    from backend.api.simulation import router as simulation_router

    # Register authentication routes under both /api/v1 and /api
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(auth_router, prefix="/api")

    # Register feature routes
    app.include_router(chat_router, prefix=settings.API_V1_STR)
    app.include_router(chat_router)

    app.include_router(crimes_router, prefix=settings.API_V1_STR)
    app.include_router(crimes_router)

    app.include_router(network_router, prefix=settings.API_V1_STR)
    app.include_router(network_router)

    app.include_router(predictions_router, prefix=settings.API_V1_STR)
    app.include_router(predictions_router)

    app.include_router(recommendations_router, prefix=settings.API_V1_STR)
    app.include_router(recommendations_router, prefix="/api")

    app.include_router(reports_router, prefix=settings.API_V1_STR)
    app.include_router(reports_router)

    app.include_router(simulation_router, prefix=settings.API_V1_STR)
    app.include_router(simulation_router, prefix="/api")

    return app


# The FastAPI application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Run the server using uvicorn if executed directly
    uvicorn.run(
        "backend.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
