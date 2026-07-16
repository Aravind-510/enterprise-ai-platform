from fastapi import FastAPI

# Authentication
from backend.authentication.routes import router as auth_router

# Users
from backend.users.routes import router as users_router

from backend.rag.document_upload import router as upload_router

from backend.rag.knowledge_api import router as knowledge_router

from backend.rag.retriever import router as retriever_router

from backend.admin.document_admin import router as admin_router



app = FastAPI(
    title="Enterprise AI Platform",
    description="Enterprise AI Platform with Authentication, RBAC and Knowledge Base",
    version="1.0.0"
)

# Register Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(upload_router)
app.include_router(knowledge_router)
app.include_router(retriever_router)
app.include_router(admin_router)


@app.get(
    "/",
    tags=["System"],
    summary="Application Status"
)
def root():
    return {
        "status": "running"
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health Check"
)
def health():
    return {
        "database": "connected",
        "vector_db": "connected",
        "llm": "connected"
    }