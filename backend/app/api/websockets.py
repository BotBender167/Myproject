from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected to WS! Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict | str):
        """Broadcast a message to all connected clients."""
        if isinstance(message, dict):
            text_data = json.dumps(message)
        else:
            text_data = message

        print(f"Broadcasting to {len(self.active_connections)} client(s): {text_data[:120]}...")

        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(text_data)
            except Exception as e:
                print(f"WS send failed: {e}")
                dead.append(connection)

        for conn in dead:
            self.disconnect(conn)

# Singleton — imported by both main.py and endpoints.py
manager = ConnectionManager()
