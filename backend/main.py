from fastapi import FastAPI

from backend.authentication.routes import router as auth_router
from backend.users.routes import router as users_router
from backend.roles.routes import router as roles_router
from backend.permissions.routes import router as permissions_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(permissions_router)