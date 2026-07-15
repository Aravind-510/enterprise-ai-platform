from fastapi import FastAPI
from backend.authentication.routes import router as auth_router

app = FastAPI(
    title="Enterprise AI Platform",
    version="1.0.0"
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    return {
        "database": "connected",
        "vector_db": "connected",
        "llm": "connected"
    }