"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import generation, auth, payment, user

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    generation.router,
    prefix="/generation",
    tags=["generation"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    payment.router,
    prefix="/payment",
    tags=["payment"]
)

api_router.include_router(
    user.router,
    prefix="/user",
    tags=["user"]
)
