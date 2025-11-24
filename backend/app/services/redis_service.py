import redis.asyncio as redis
from app.core.config import settings
import json

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(f"redis://{settings.REDIS_HOST}:6379", decode_responses=True)

    async def set_user_state(self, phone_number: str, state: str, data: dict = None):
        key = f"user:{phone_number}"
        value = {"state": state, "data": data or {}}
        await self.redis.set(key, json.dumps(value), ex=3600) # Expire in 1 hour

    async def get_user_state(self, phone_number: str):
        key = f"user:{phone_number}"
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def update_user_data(self, phone_number: str, new_data: dict):
        current = await self.get_user_state(phone_number)
        if current:
            current["data"].update(new_data)
            await self.set_user_state(phone_number, current["state"], current["data"])

    # Cart Management
    async def add_to_cart(self, phone_number: str, item: dict):
        key = f"cart:{phone_number}"
        cart = await self.redis.get(key)
        if cart:
            cart_items = json.loads(cart)
        else:
            cart_items = []
        
        cart_items.append(item)
        await self.redis.set(key, json.dumps(cart_items), ex=3600*24) # 24 hours

    async def get_cart(self, phone_number: str):
        key = f"cart:{phone_number}"
        cart = await self.redis.get(key)
        return json.loads(cart) if cart else []

    async def clear_cart(self, phone_number: str):
        key = f"cart:{phone_number}"
        await self.redis.delete(key)

redis_service = RedisService()
