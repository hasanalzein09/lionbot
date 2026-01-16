import httpx
from app.core.config import settings
from app.core.constants import (
    CART_EXPIRY_SECONDS, CONVERSATION_EXPIRY_SECONDS,
    USER_STATE_EXPIRY_SECONDS, PENDING_REVIEW_EXPIRY_SECONDS,
    ANALYTICS_RETENTION_SECONDS, AI_MAX_CONVERSATION_MESSAGES
)
import json
from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def json_dumps(obj):
    """JSON dumps with Decimal support"""
    return json.dumps(obj, cls=DecimalEncoder)

# Maximum size for in-memory fallback store (LRU eviction)
MAX_MEMORY_STORE_SIZE = 10000


class LRUCache(OrderedDict):
    """Simple LRU cache implementation for memory fallback"""

    def __init__(self, max_size: int = MAX_MEMORY_STORE_SIZE):
        super().__init__()
        self.max_size = max_size

    def get(self, key, default=None):
        if key in self:
            self.move_to_end(key)
            return self[key]
        return default

    def set(self, key, value):
        if key in self:
            self.move_to_end(key)
        self[key] = value
        while len(self) > self.max_size:
            oldest = next(iter(self))
            del self[oldest]
            logger.debug(f"LRU evicted key: {oldest[:20]}...")


class RedisService:
    """
    Redis Service using Upstash REST API.
    Compatible with serverless environments like Cloud Run.
    Falls back to LRU in-memory storage if Upstash not configured.
    """

    def __init__(self):
        self.base_url = settings.UPSTASH_REDIS_REST_URL
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        # Fallback to LRU in-memory storage with eviction
        self._memory_store = LRUCache(MAX_MEMORY_STORE_SIZE)
        self._client: Optional[httpx.AsyncClient] = None
        self._using_fallback = not (self.base_url and self.token)
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create singleton httpx client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def close(self):
        """Close the httpx client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _execute(self, *args) -> Any:
        """Execute Redis command via Upstash REST API"""
        if not self.base_url or not self.token:
            # Fallback to memory storage
            return await self._memory_fallback(*args)
        
        try:
            client = self._get_client()
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json=list(args)
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result")
        except Exception as e:
            logger.error(f"Upstash Redis error: {e}")
            # Fallback to memory
            return await self._memory_fallback(*args)
    
    async def _memory_fallback(self, *args) -> Any:
        """In-memory fallback when Redis is unavailable (with LRU eviction)"""
        if not args:
            return None

        command = args[0].upper()

        if command == "SET":
            key = args[1]
            value = args[2]
            self._memory_store.set(key, value)
            return "OK"
        elif command == "GET":
            key = args[1]
            return self._memory_store.get(key)
        elif command == "DEL":
            key = args[1]
            if key in self._memory_store:
                del self._memory_store[key]
            return 1
        elif command == "PUBLISH":
            # Just log for memory mode
            return 0
        elif command == "HINCRBY":
            # Hash increment
            key = args[1]
            field = args[2]
            increment = int(args[3])
            hash_data = self._memory_store.get(key) or {}
            if isinstance(hash_data, str):
                hash_data = json.loads(hash_data)
            hash_data[field] = hash_data.get(field, 0) + increment
            self._memory_store.set(key, json_dumps(hash_data))
            return hash_data[field]
        elif command == "HGETALL":
            key = args[1]
            hash_data = self._memory_store.get(key)
            if hash_data and isinstance(hash_data, str):
                return json.loads(hash_data)
            return hash_data or {}
        elif command == "SADD":
            key = args[1]
            value = args[2]
            set_data = self._memory_store.get(key) or set()
            if isinstance(set_data, str):
                set_data = set(json.loads(set_data))
            set_data.add(value)
            self._memory_store.set(key, json_dumps(list(set_data)))
            return 1
        elif command == "SCARD":
            key = args[1]
            set_data = self._memory_store.get(key)
            if set_data and isinstance(set_data, str):
                return len(json.loads(set_data))
            return 0
        elif command == "EXPIRE":
            # Ignore expiry in memory mode (items auto-evict via LRU)
            return 1
        elif command == "PING":
            return "PONG"

        return None

    # ==================== User State Management ====================
    async def set_user_state(self, phone_number: str, state: str, data: dict = None):
        key = f"user:{phone_number}"
        value = {"state": state, "data": data or {}}
        await self._execute("SET", key, json_dumps(value), "EX", USER_STATE_EXPIRY_SECONDS)

    async def get_user_state(self, phone_number: str) -> Optional[Dict]:
        key = f"user:{phone_number}"
        value = await self._execute("GET", key)
        if value:
            return json.loads(value)
        return None

    async def update_user_data(self, phone_number: str, new_data: dict):
        current = await self.get_user_state(phone_number)
        if current:
            current["data"].update(new_data)
            await self.set_user_state(phone_number, current["state"], current["data"])

    async def reset_user_state(self, phone_number: str):
        """Reset user to initial state"""
        key = f"user:{phone_number}"
        await self._execute("DEL", key)

    # ==================== Cart Management ====================
    async def add_to_cart(self, phone_number: str, item: dict):
        """Add item to cart or update quantity if exists"""
        key = f"cart:{phone_number}"
        cart_items = await self.get_cart(phone_number)
        
        # Check if item already exists in cart
        existing_index = None
        for i, cart_item in enumerate(cart_items):
            if cart_item.get("menu_item_id") == item.get("menu_item_id"):
                existing_index = i
                break
        
        if existing_index is not None:
            # Update quantity
            cart_items[existing_index]["quantity"] += item.get("quantity", 1)
        else:
            # Add new item
            cart_items.append(item)
        
        await self._execute("SET", key, json_dumps(cart_items), "EX", CART_EXPIRY_SECONDS)

    async def get_cart(self, phone_number: str) -> List[Dict]:
        key = f"cart:{phone_number}"
        cart = await self._execute("GET", key)
        return json.loads(cart) if cart else []

    async def update_cart_item_quantity(self, phone_number: str, menu_item_id: int, quantity: int) -> bool:
        """Update quantity of specific item in cart"""
        cart_items = await self.get_cart(phone_number)
        
        for item in cart_items:
            if item.get("menu_item_id") == menu_item_id:
                if quantity <= 0:
                    cart_items.remove(item)
                else:
                    item["quantity"] = quantity
                
                key = f"cart:{phone_number}"
                await self._execute("SET", key, json_dumps(cart_items), "EX", CART_EXPIRY_SECONDS)
                return True
        
        return False

    async def remove_from_cart(self, phone_number: str, menu_item_id: int) -> bool:
        """Remove specific item from cart"""
        cart_items = await self.get_cart(phone_number)
        
        original_length = len(cart_items)
        cart_items = [item for item in cart_items if item.get("menu_item_id") != menu_item_id]
        
        if len(cart_items) < original_length:
            key = f"cart:{phone_number}"
            await self._execute("SET", key, json_dumps(cart_items), "EX", CART_EXPIRY_SECONDS)
            return True
        
        return False

    async def get_cart_total(self, phone_number: str) -> float:
        """Calculate cart total"""
        cart_items = await self.get_cart(phone_number)
        return sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)

    async def get_cart_count(self, phone_number: str) -> int:
        """Get total number of items in cart"""
        cart_items = await self.get_cart(phone_number)
        return sum(item.get("quantity", 1) for item in cart_items)

    async def clear_cart(self, phone_number: str):
        key = f"cart:{phone_number}"
        await self._execute("DEL", key)

    # ==================== Pub/Sub for Real-time Updates ====================
    async def publish_order_update(self, order_id: int, data: dict):
        """Publish order update for real-time notifications"""
        channel = f"order:{order_id}"
        await self._execute("PUBLISH", channel, json_dumps(data))

    async def publish_restaurant_notification(self, restaurant_id: int, data: dict):
        """Publish notification to restaurant"""
        channel = f"restaurant:{restaurant_id}:orders"
        await self._execute("PUBLISH", channel, json_dumps(data))

    async def publish_driver_notification(self, driver_id: int, data: dict):
        """Publish notification to driver"""
        channel = f"driver:{driver_id}:deliveries"
        await self._execute("PUBLISH", channel, json_dumps(data))

    # ==================== Conversation Memory ====================
    async def save_conversation_message(self, phone_number: str, role: str, content: str, context: dict = None):
        """Save a message to conversation history"""
        key = f"conv:{phone_number}"
        conv = await self._execute("GET", key)

        if conv:
            conv = json.loads(conv)
        else:
            conv = {"messages": [], "context": {}}

        # Add new message
        conv["messages"].append({
            "role": role,
            "content": content[:500],  # Limit message length
            "timestamp": str(datetime.now())
        })

        # Keep only last N messages
        conv["messages"] = conv["messages"][-AI_MAX_CONVERSATION_MESSAGES:]

        # Update context if provided
        if context:
            conv["context"].update(context)

        # Save with 30 min expiry
        await self._execute("SET", key, json_dumps(conv), "EX", CONVERSATION_EXPIRY_SECONDS)

    async def get_conversation(self, phone_number: str) -> Optional[Dict]:
        """Get conversation history"""
        key = f"conv:{phone_number}"
        conv = await self._execute("GET", key)
        if conv:
            return json.loads(conv)
        return {"messages": [], "context": {}}

    async def update_conversation_context(self, phone_number: str, context: dict):
        """Update conversation context without adding a message"""
        key = f"conv:{phone_number}"
        conv = await self._execute("GET", key)

        if conv:
            conv = json.loads(conv)
        else:
            conv = {"messages": [], "context": {}}

        conv["context"].update(context)
        await self._execute("SET", key, json_dumps(conv), "EX", CONVERSATION_EXPIRY_SECONDS)

    async def clear_conversation(self, phone_number: str):
        """Clear conversation history"""
        key = f"conv:{phone_number}"
        await self._execute("DEL", key)

    # ==================== Pending Reviews ====================
    async def set_pending_review(self, phone_number: str, order_id: int, restaurant_name: str):
        """Set a pending review request"""
        key = f"pending_review:{phone_number}"
        data = {"order_id": order_id, "restaurant_name": restaurant_name}
        await self._execute("SET", key, json_dumps(data), "EX", PENDING_REVIEW_EXPIRY_SECONDS)

    async def get_pending_review(self, phone_number: str) -> Optional[Dict]:
        """Get pending review if exists"""
        key = f"pending_review:{phone_number}"
        data = await self._execute("GET", key)
        if data:
            return json.loads(data)
        return None

    async def clear_pending_review(self, phone_number: str):
        """Clear pending review"""
        key = f"pending_review:{phone_number}"
        await self._execute("DEL", key)

    # ==================== Rate Limiting ====================
    async def check_rate_limit(self, phone_number: str, action: str = "ai", limit: int = 10, window: int = 60) -> bool:
        """
        Check if user is within rate limit.
        Returns True if allowed, False if rate limited.
        Default: 10 AI calls per 60 seconds.
        """
        key = f"ratelimit:{action}:{phone_number}"
        count = await self._execute("GET", key)

        if count is None:
            # First request - set counter
            await self._execute("SET", key, "1", "EX", window)
            return True

        count = int(count)
        if count >= limit:
            return False

        # Increment counter
        await self._execute("SET", key, str(count + 1), "KEEPTTL")
        return True

    async def get_rate_limit_remaining(self, phone_number: str, action: str = "ai", limit: int = 10) -> int:
        """Get remaining calls before rate limit"""
        key = f"ratelimit:{action}:{phone_number}"
        count = await self._execute("GET", key)
        if count is None:
            return limit
        return max(0, limit - int(count))

    # ==================== Analytics ====================
    async def track_ai_usage(self, phone_number: str, intent: str, success: bool):
        """Track AI usage for analytics"""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # Track daily intent counts
        key = f"analytics:intent:{today}"
        await self._execute("HINCRBY", key, intent, 1)
        await self._execute("EXPIRE", key, ANALYTICS_RETENTION_SECONDS)  # Keep for 7 days

        # Track success rate
        status = "success" if success else "error"
        key = f"analytics:status:{today}"
        await self._execute("HINCRBY", key, status, 1)
        await self._execute("EXPIRE", key, ANALYTICS_RETENTION_SECONDS)

        # Track user activity
        key = f"analytics:users:{today}"
        await self._execute("SADD", key, phone_number)
        await self._execute("EXPIRE", key, ANALYTICS_RETENTION_SECONDS)

    async def get_daily_analytics(self, date: str = None) -> Dict:
        """Get analytics for a specific date"""
        from datetime import datetime
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        # Get intent distribution
        intents_key = f"analytics:intent:{date}"
        intents = await self._execute("HGETALL", intents_key)

        # Get status counts
        status_key = f"analytics:status:{date}"
        status = await self._execute("HGETALL", status_key)

        # Get unique users count
        users_key = f"analytics:users:{date}"
        users_count = await self._execute("SCARD", users_key)

        return {
            "date": date,
            "intents": intents or {},
            "status": status or {},
            "unique_users": users_count or 0
        }


redis_service = RedisService()
