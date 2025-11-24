from fastapi import APIRouter
from app.api.v1.endpoints import webhook, login, restaurants, menus, orders

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
api_router.include_router(menus.router, prefix="/menus", tags=["menus"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(webhook.router, tags=["whatsapp"])
