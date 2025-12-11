import asyncio
from collections import defaultdict
from fastapi import WebSocket
from typing import Dict, List


class WebSocketManager:
    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, symbol: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._connections[symbol].append(websocket)

    async def disconnect(self, symbol: str, websocket: WebSocket):
        async with self._lock:
            if websocket in self._connections[symbol]:
                self._connections[symbol].remove(websocket)

    async def broadcast(self, symbol: str, message: dict):
        async with self._lock:
            conns = list(self._connections.get(symbol, []))

        dead = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    if ws in self._connections[symbol]:
                        self._connections[symbol].remove(ws)


ws_manager = WebSocketManager()
