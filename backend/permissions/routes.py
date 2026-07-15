from fastapi import APIRouter

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)

@router.get("/")
def permissions():
    return [
        {
            "module": "HR",
            "permission": "Read"
        },
        {
            "module": "Payroll",
            "permission": "Admin"
        }
    ]