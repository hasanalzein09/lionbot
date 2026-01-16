from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # driver_id -> WebSocket
        self.driver_connections: Dict[int, WebSocket] = {}
        # restaurant_id -> Set of WebSockets
        self.restaurant_connections: Dict[int, Set[WebSocket]] = {}
        # order_id -> Set of WebSockets (customers tracking their order)
        self.order_watchers: Dict[int, Set[WebSocket]] = {}

    async def connect_driver(self, websocket: WebSocket, driver_id: int):
        await websocket.accept()
        self.driver_connections[driver_id] = websocket

    async def connect_restaurant(self, websocket: WebSocket, restaurant_id: int):
        await websocket.accept()
        if restaurant_id not in self.restaurant_connections:
            self.restaurant_connections[restaurant_id] = set()
        self.restaurant_connections[restaurant_id].add(websocket)

    async def connect_order_watcher(self, websocket: WebSocket, order_id: int):
        await websocket.accept()
        if order_id not in self.order_watchers:
            self.order_watchers[order_id] = set()
        self.order_watchers[order_id].add(websocket)

    def disconnect_driver(self, driver_id: int):
        self.driver_connections.pop(driver_id, None)

    def disconnect_restaurant(self, websocket: WebSocket, restaurant_id: int):
        if restaurant_id in self.restaurant_connections:
            self.restaurant_connections[restaurant_id].discard(websocket)

    def disconnect_order_watcher(self, websocket: WebSocket, order_id: int):
        if order_id in self.order_watchers:
            self.order_watchers[order_id].discard(websocket)

    async def notify_driver(self, driver_id: int, message: dict):
        """Send message to specific driver."""
        if driver_id in self.driver_connections:
            try:
                await self.driver_connections[driver_id].send_json(message)
            except Exception:
                self.disconnect_driver(driver_id)

    async def notify_restaurant(self, restaurant_id: int, message: dict):
        """Send message to all connections of a restaurant."""
        if restaurant_id in self.restaurant_connections:
            dead_connections = set()
            for ws in self.restaurant_connections[restaurant_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_connections.add(ws)
            self.restaurant_connections[restaurant_id] -= dead_connections

    async def broadcast_new_order(self, order_data: dict):
        """Broadcast new order to all online drivers."""
        message = {"type": "new_order", "data": order_data}
        dead_drivers = []
        for driver_id, ws in self.driver_connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                dead_drivers.append(driver_id)
        for driver_id in dead_drivers:
            self.disconnect_driver(driver_id)

    async def notify_order_update(self, order_id: int, status: str, driver_location: dict = None):
        """Notify watchers about order status/location update."""
        if order_id in self.order_watchers:
            message = {
                "type": "order_update",
                "order_id": order_id,
                "status": status,
                "driver_location": driver_location
            }
            dead_watchers = set()
            for ws in self.order_watchers[order_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_watchers.add(ws)
            self.order_watchers[order_id] -= dead_watchers


# Singleton instance
ws_manager = ConnectionManager()
