"""
FastAPI main application.

Entry point for the Semantic Mapper REST API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sys
import os
from contextlib import asynccontextmanager

# Add paths for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from config import settings
from db.connection import init_db
from api.models.responses import HealthResponse, MessageResponse

# Import routers
from api.routers import projects, sources, jobs, extraction, ontology, materialization, query


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("🚀 Starting Semantic Mapper API...")
    print(f"📊 Database URL: {settings.database_url}")
    print(f"🧠 LLM Provider: {settings.LLM_PROVIDER}")

    # Initialize database
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

    yield

    # Shutdown
    print("👋 Shutting down Semantic Mapper API...")


# Create FastAPI app
app = FastAPI(
    title="Semantic Mapper API",
    description="REST API for semantic ontology mapping and knowledge graph construction",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for uploaded files if needed)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            }
        },
    )


# Root endpoint
@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint with API information."""
    return MessageResponse(
        message="Semantic Mapper API v2.0",
        data={
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/api/health",
        },
    )


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring and Docker health checks."""
    return HealthResponse(status="healthy")


# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(extraction.router, prefix="/api/extraction", tags=["extraction"])
app.include_router(ontology.router, prefix="/api/ontology", tags=["ontology"])
app.include_router(materialization.router, prefix="/api/materialization", tags=["materialization"])
app.include_router(query.router, prefix="/api/query", tags=["query"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
