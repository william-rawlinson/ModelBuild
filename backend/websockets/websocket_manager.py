import asyncio
import json
from typing import Any

from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connection = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        print("WS connection open")
        self.active_connection = websocket

    def disconnect(self):
        print("WS disconnected")
        self.active_connection = None

    async def send_message(self, message_type: str, payload: Any, process_name: str = "default",
                           process_complete=False):
        """
        Send a structured JSON message to the active connection.
        Example message:
        {
            "type": "upload_progress",
            "process": "model_upload",
            "payload": {
                "progress": 45,
                "status": "parsing sheet..."
            }
        }
        """
        if self.active_connection:
            message = {
                "type": message_type,
                "process_name": process_name,
                "payload": payload,
                "process_complete": process_complete,
            }
            await self.active_connection.send_text(json.dumps(message))
            await asyncio.sleep(0)


# Create a single global manager instance
manager = ConnectionManager()
