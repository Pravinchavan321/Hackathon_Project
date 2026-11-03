"""AgentShield AI — Main FastAPI Application Entrypoint.
A Policy-Governed Framework for Secure and Autonomous AI Agent Execution.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import get_settings
from backend.app.database.mongodb import mongo_manager
from backend.app.database.indexes import ensure_indexes
from backend.app.services.auth_service import seed_admin_user
from backend.app.api.auth_routes import router as auth_router
from backend.app.api.approval_routes import router as approval_router
from backend.app.api.task_routes import router as task_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown hooks."""
    # Startup
    connected = mongo_manager.connect()
    if connected:
        db = mongo_manager.get_db()
        ensure_indexes(db)
        seed_admin_user(db)
    yield
    # Shutdown
    mongo_manager.disconnect()


app = FastAPI(
    title="AgentShield AI API",
    description="A Policy-Governed Framework for Secure and Autonomous AI Agent Execution",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount versioned API routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(approval_router, prefix="/api/v1/approvals")
app.include_router(task_router, prefix="/api/v1/tasks")


@app.get("/health", tags=["System"])
async def health_check():
    """System health and readiness probe."""
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "database_connected": mongo_manager.is_healthy(),
        "llm_provider": settings.LLM_PROVIDER,
        "storage_mode": settings.STORAGE_MODE,
        "version": "1.0.0"
    }


@app.get("/", tags=["System"])
async def root():
    """API root displaying identity and operational status."""
    return {
        "name": "AgentShield AI",
        "tagline": "Autonomous Intelligence. Governed Execution. Trusted Outcomes.",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }
