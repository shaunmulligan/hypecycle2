from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    """websocket connection manager"""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def list(self):
        """List the active ws connections"""
        return self.active_connections