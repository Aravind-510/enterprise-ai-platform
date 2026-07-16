from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(
    prefix="/documents",
    tags=["Knowledge Base"]
)

documents_db = {}


class DocumentUpdate(BaseModel):
    title: str
    department: str
    owner: str
    status: str


class SearchRequest(BaseModel):
    department: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None


@router.get("/")
def get_documents(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    sort_by: str = "title"
):

    docs = list(documents_db.values())

    docs.sort(key=lambda x: x.get(sort_by, ""))

    start = (page - 1) * size
    end = start + size

    return {
        "page": page,
        "size": size,
        "total": len(docs),
        "documents": docs[start:end]
    }


@router.get("/{document_id}")
def get_document(document_id: int):

    if document_id not in documents_db:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return documents_db[document_id]


@router.put("/{document_id}")
def update_document(document_id: int, document: DocumentUpdate):

    if document_id not in documents_db:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    documents_db[document_id].update(document.dict())

    return {
        "message": "Document updated successfully",
        "document": documents_db[document_id]
    }


@router.delete("/{document_id}")
def delete_document(document_id: int):

    if document_id not in documents_db:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    del documents_db[document_id]

    return {
        "message": "Document deleted successfully"
    }


@router.post("/search")
def search_documents(search: SearchRequest):

    results = []

    for doc in documents_db.values():

        if search.department and doc["department"] != search.department:
            continue

        if search.owner and doc["owner"] != search.owner:
            continue

        if search.status and doc["status"] != search.status:
            continue

        results.append(doc)

    return {
        "count": len(results),
        "documents": results
    }