"""
Sentinel AI - Main FastAPI Application
=========================================
File: backend/main.py
Purpose: FastAPI entry point. Configures routers, CORS, exception handling,
         logging, and application startup/shutdown events.

Dependencies: fastapi, uvicorn, loguru
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config.settings import get_settings
from backend.config.config import APP_METADATA
from backend.config.logging_config import setup_logging

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
    
    # Connect to databases (Neo4j, Postgres, etc.)
    # Example: await neo4j_service.connect()
    # Example: await postgres_service.connect()
    
    logger.info("Sentinel AI Core Systems initialized successfully.")
    
    yield
    
    # --- Shutdown ---
    logger.info("Shutting down Sentinel AI Core Systems...")
    # Close database connections
    # Example: await neo4j_service.close()
    # Example: await postgres_service.close()
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

    # Health Check Endpoint
    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, Any]:
        """Simple health check endpoint to verify API is running."""
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION
        }

    # Register Routers (To be implemented in API package)
    # from backend.api.chat import router as chat_router
    # app.include_router(chat_router, prefix=settings.API_V1_STR)

    return app

# The FastAPI application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Run the server using uvicorn if executed directly
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
