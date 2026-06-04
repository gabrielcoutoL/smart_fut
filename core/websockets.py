from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, match_id: int):
        await websocket.accept()

        if match_id not in self.active_connections:
            self.active_connections[match_id] = []

        self.active_connections[match_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, match_id: int):
        if match_id in self.active_connections:
            self.active_connections[match_id].remove(websocket)

        if not self.active_connections[match_id]:
            self.active_connections.pop(match_id)

    async def broadcast(self, message: dict, match_id: int):

        connections = self.active_connections.get(match_id, [])

        for websocket in connections:
            await websocket.send_json(message)
