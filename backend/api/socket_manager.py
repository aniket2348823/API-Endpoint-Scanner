from typing import List
from fastapi import WebSocket
import json
import logging

class SocketManager:
    def __init__(self):
        # We separate connections so we know who to broadcast to
        self.ui_connections: List[WebSocket] = []
        self.spy_connections: List[WebSocket] = []
        self.logger = logging.getLogger("Antigravity.SocketManager")

    async def connect(self, websocket: WebSocket, client_type: str = "ui"):
        await websocket.accept()
        if client_type == "spy":
            self.spy_connections.append(websocket)
            self.logger.info("Spy Extension Connected.")
            # Notify UIs that Spy is Online
            await self.broadcast_to_ui({
                "type": "SPY_STATUS",
                "payload": {"connected": True}
            })
        else:
            self.ui_connections.append(websocket)
            self.logger.info("UI Client Connected.")
            # Tell the new UI client if Spy is currently connected
            spy_is_online = len(self.spy_connections) > 0
            await websocket.send_text(json.dumps({
                "type": "SPY_STATUS",
                "payload": {"connected": spy_is_online}
            }))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.spy_connections:
            self.spy_connections.remove(websocket)
            self.logger.info("Spy Extension Disconnected.")
            # Notify UIs that Spy is Offline (need to wrap in async loop if called from sync context, 
            # but usually called from endpoint which is async or we rely on main loop)
            # relying on main loop to handle disconnect logic if needed, 
            # but for simplicity we assume sync disconnect here. 
            # NOTE: To broadcast from sync disconnect, we'd need an event loop reference.
            # Ideally disconnect() is called from the async endpoint so we can await.
            pass 
        elif websocket in self.ui_connections:
            self.ui_connections.remove(websocket)
            self.logger.info("UI Client Disconnected.")

    async def broadcast(self, data: dict):
        """Broadcasts to UI clients (default behavior)."""
        await self.broadcast_to_ui(data)

    async def broadcast_to_ui(self, data: dict):
        message = json.dumps(data)
        to_remove = []
        for connection in self.ui_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                self.logger.error(f"Failed to send to UI: {e}")
                to_remove.append(connection)
        
        for dead in to_remove:
            if dead in self.ui_connections:
                self.ui_connections.remove(dead)

manager = SocketManager()
