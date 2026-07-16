from fastapi import APIRouter, Request
from backend.audit.logger import audit_log

router = APIRouter()

@router.post("/login")
def login(request: Request):

    # Login logic here

    audit_log(
        user_id=1,
        endpoint="/login",
        action="User Login",
        status="Success",
        ip=request.client.host
    )

    return {
        "message": "Login Successful"
    }