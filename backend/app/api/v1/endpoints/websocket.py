from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.core.websocket_manager import ws_manager
import json

router = APIRouter()

@router.websocket("/ws/driver/{driver_id}")
async def driver_websocket(websocket: WebSocket, driver_id: int):
    """
    WebSocket endpoint for drivers to receive real-time order notifications.
    """
    await ws_manager.connect_driver(websocket, driver_id)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle ping/pong for connection health
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Handle location updates from driver
            elif message.get("type") == "location_update":
                # Could broadcast to order watchers here
                pass
                
    except WebSocketDisconnect:
        ws_manager.disconnect_driver(driver_id)


@router.websocket("/ws/restaurant/{restaurant_id}")
async def restaurant_websocket(websocket: WebSocket, restaurant_id: int):
    """
    WebSocket endpoint for restaurants to receive real-time order notifications.
    """
    await ws_manager.connect_restaurant(websocket, restaurant_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        ws_manager.disconnect_restaurant(websocket, restaurant_id)


@router.websocket("/ws/order/{order_id}")
async def order_tracking_websocket(websocket: WebSocket, order_id: int):
    """
    WebSocket endpoint for customers to track their order in real-time.
    """
    await ws_manager.connect_order_watcher(websocket, order_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        ws_manager.disconnect_order_watcher(websocket, order_id)
