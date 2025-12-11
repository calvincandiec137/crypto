import json
import redis.asyncio as redis
from typing import Any

class RedisCacheBackend:
    def __init__(self, url: str):
        self.client = redis.from_url(url)

    async def get(self, key: str) -> Any | None:
        raw = await self.client.get(key)
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode()
        return json.loads(raw)

    async def set(self, key: str, value, ttl: int):
        if hasattr(value, "model_dump"):
            payload = value.model_dump()
        else:
            payload = value
        await self.client.set(key, json.dumps(payload), ex=ttl)

    async def flushdb(self):
        await self.client.flushdb()
