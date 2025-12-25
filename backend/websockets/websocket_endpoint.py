import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.websockets.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for upload progress notifications.
    Frontend connects to: ws://127.0.0.1:8000/ws
    """
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # just keep the socket alive
    except WebSocketDisconnect:
        manager.disconnect()
