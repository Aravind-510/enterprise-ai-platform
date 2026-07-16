from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.rag.embedding_service import embedding_service
from backend.rag.vector_store import vector_store

router = APIRouter(
    prefix="",
    tags=["Semantic Retrieval"]
)


class RetrieveRequest(BaseModel):
    query: str
    department: str
    top_k: int = 5
    metadata_filter: Optional[dict] = None


@router.post("/retrieve")
def retrieve_documents(request: RetrieveRequest):

    # Generate query embedding
    embedding = embedding_service.generate_embedding(
        request.query
    )["embedding"]

    # Search ChromaDB
    if request.metadata_filter:

        results = vector_store.search_with_filter(
            department=request.department,
            embedding=embedding,
            metadata_filter=request.metadata_filter,
            top_k=request.top_k
        )

    else:

        results = vector_store.search(
            department=request.department,
            embedding=embedding,
            top_k=request.top_k
        )

    response = []

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i in range(len(ids)):

        similarity = round(1 - distances[i], 4)

        response.append({

            "id": ids[i],

            "document": docs[i],

            "metadata": metas[i],

            "similarity_score": similarity

        })

    return {

        "query": request.query,

        "total_results": len(response),

        "documents": response

    }