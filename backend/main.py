from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "database": "connected",
        "vector_db": "connected",
        "llm": "connected"
    }