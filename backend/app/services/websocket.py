from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """ Accepts an incoming connection request and stores the session socket. """
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📡 New dashboard terminal connected. Active sessions: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """ Removes a disconnected session socket safely from the registry pool. """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"🔌 Terminal disconnected. Remaining active sessions: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """ Sends a direct message payload exclusively to one target websocket client. """
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """
        Broadcasts telemetry event frames or critical security alerts 
        simultaneously to every connected dashboard user interface.
        """
        payload = json.dumps(message, default=str)  
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                pass

manager = ConnectionManager()