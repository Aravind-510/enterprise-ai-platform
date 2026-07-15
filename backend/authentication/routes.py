from fastapi import APIRouter
from .schemas import LoginRequest
from .jwt_handler import create_access_token

router = APIRouter()


@router.post("/login")
def login(request: LoginRequest):

    token = create_access_token(
        {"sub": request.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout():

    return {
        "message": "Logged out successfully"
    }


@router.post("/refresh-token")
def refresh():

    return {
        "message": "Refresh Token Endpoint"
    }