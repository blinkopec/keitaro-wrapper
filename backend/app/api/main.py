from fastapi import APIRouter

from app.api.routes import campaigns, health, offers

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(campaigns.router)
api_router.include_router(offers.router)
