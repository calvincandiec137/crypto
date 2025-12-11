import time

class TTLCacheBackend:
    def __init__(self):
        self._store: dict[str, tuple[float, object]] = {}

    async def get(self, key: str):
        entry = self._store.get(key)
        if not entry:
            return None
        expires, value = entry
        if expires < time.time():
            self._store.pop(key, None)
            return None
        return value

    async def set(self, key: str, value, ttl: int):
        expires = time.time() + ttl
        self._store[key] = (expires, value)
