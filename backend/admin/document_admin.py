from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin/documents",
    tags=["Knowledge Base Administration"]
)

# Temporary in-memory storage
documents = {}
document_versions = {}
audit_logs = []


class ApprovalRequest(BaseModel):
    approved_by: str


class RejectRequest(BaseModel):
    rejected_by: str
    reason: str


class ArchiveRequest(BaseModel):
    archived_by: str


class RestoreRequest(BaseModel):
    version: int
    restored_by: str


class BulkDeleteRequest(BaseModel):
    document_ids: List[int]


def add_audit_log(action: str, document_id: int, user: str):
    audit_logs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "document_id": document_id,
        "performed_by": user
    })


@router.put("/{document_id}/approve")
def approve_document(document_id: int, request: ApprovalRequest):

    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")

    documents[document_id]["status"] = "Approved"

    add_audit_log("APPROVE", document_id, request.approved_by)

    return {
        "message": "Document approved successfully",
        "document": documents[document_id]
    }


@router.put("/{document_id}/reject")
def reject_document(document_id: int, request: RejectRequest):

    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")

    documents[document_id]["status"] = "Rejected"
    documents[document_id]["rejection_reason"] = request.reason

    add_audit_log("REJECT", document_id, request.rejected_by)

    return {
        "message": "Document rejected successfully",
        "document": documents[document_id]
    }


@router.put("/{document_id}/archive")
def archive_document(document_id: int, request: ArchiveRequest):

    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")

    documents[document_id]["status"] = "Archived"

    add_audit_log("ARCHIVE", document_id, request.archived_by)

    return {
        "message": "Document archived successfully",
        "document": documents[document_id]
    }


@router.get("/{document_id}/versions")
def get_version_history(document_id: int):

    return {
        "document_id": document_id,
        "versions": document_versions.get(document_id, [])
    }


@router.put("/{document_id}/restore")
def restore_version(document_id: int, request: RestoreRequest):

    versions = document_versions.get(document_id, [])

    for version in versions:

        if version["version"] == request.version:

            documents[document_id] = version["document"]

            add_audit_log(
                "RESTORE",
                document_id,
                request.restored_by
            )

            return {
                "message": "Version restored successfully",
                "document": version["document"]
            }

    raise HTTPException(
        status_code=404,
        detail="Version not found"
    )


@router.delete("/bulk-delete")
def bulk_delete(request: BulkDeleteRequest):

    deleted = []

    for doc_id in request.document_ids:

        if doc_id in documents:
            del documents[doc_id]
            deleted.append(doc_id)

    add_audit_log(
        "BULK_DELETE",
        0,
        "Administrator"
    )

    return {
        "deleted_documents": deleted
    }


@router.get("/audit-logs")
def get_audit_logs():

    return {
        "count": len(audit_logs),
        "logs": audit_logs
    }