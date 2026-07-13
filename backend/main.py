"""
Sentinel AI - Main FastAPI Application
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
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from backend.config import settings
from backend.database.postgres import init_db, AsyncSessionLocal, get_db
from backend.database.models import Officer, OfficerRole
from backend.database.neo4j import neo4j_service
from backend.auth.auth_handler import hash_password, verify_password, create_access_token
from backend.services.pipeline import sync_postgres_to_neo4j

# Import routers
from backend.api import crimes, network, predictions, chat, reports

# Define lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables
    await init_db()
    
    # Pre-synchronize Postgres with Neo4j if Neo4j is available
    async with AsyncSessionLocal() as session:
        try:
            await sync_postgres_to_neo4j(session)
            print("Successfully synchronized PostgreSQL records with Neo4j on startup.")
        except Exception as e:
            print(f"Warning: Neo4j pre-sync skipped on startup: {e} (Verify Neo4j is running)")
            
    yield
    
    # Shutdown: Close Neo4j driver connection pool
    await neo4j_service.close()
    print("Neo4j driver connection pool closed successfully.")

app = FastAPI(
    title="Sentinel AI - Crime Intelligence Operating System API",
    description="Backend API serving crime analytics, digital twin, relationship graphs, and predictive models",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL EXCEPTION HANDLERS ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    # Return 500 error detailing internal cause
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred.", "error": str(exc)}
    )

# --- AUTH ROUTER ---

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])

class OfficerRegisterRequest(uvicorn.Config if False else Any): # dummy helper
    pass

# We can define Pydantic schema for register
from pydantic import BaseModel

class RegisterInput(BaseModel):
    name: str
    badge_number: str
    rank: str
    department: str
    password: str
    role: str = "officer" # officer, admin, analyst

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_officer(payload: RegisterInput, db: AsyncSession = Depends(get_db)):
    """Register a new law enforcement officer"""
    # Check if badge number is unique
    existing_q = select(Officer).where(Officer.badge_number == payload.badge_number)
    res = await db.execute(existing_q)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Officer with this badge number is already registered."
        )
        
    # Determine officer role
    role_val = OfficerRole.officer
    if payload.role == "admin":
        role_val = OfficerRole.admin
    elif payload.role == "analyst":
        role_val = OfficerRole.analyst
        
    hashed = hash_password(payload.password)
    new_officer = Officer(
        name=payload.name,
        badge_number=payload.badge_number,
        rank=payload.rank,
        department=payload.department,
        hashed_password=hashed,
        role=role_val
    )
    db.add(new_officer)
    await db.commit()
    await db.refresh(new_officer)
    
    return {
        "id": new_officer.id,
        "name": new_officer.name,
        "badge_number": new_officer.badge_number,
        "role": new_officer.role.value
    }

@auth_router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate officer credentials and return JWT bearer token. (Username maps to badge number)"""
    query = select(Officer).where(Officer.badge_number == form_data.username)
    result = await db.execute(query)
    officer = result.scalar_one_or_none()
    if not officer or not verify_password(form_data.password, officer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid badge number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate token payload
    token_data = {
        "sub": str(officer.id),
        "name": officer.name,
        "badge_number": officer.badge_number,
        "role": officer.role.value
    }
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "officer": {
            "name": officer.name,
            "badge_number": officer.badge_number,
            "role": officer.role.value
        }
    }

# Include routers
app.include_router(auth_router)
app.include_router(crimes.router)
app.include_router(network.router)
app.include_router(predictions.router)
app.include_router(chat.router)
app.include_router(reports.router)

# --- BASE ROUTES ---

@app.get("/health", tags=["system"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
