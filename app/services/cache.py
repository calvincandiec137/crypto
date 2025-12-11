import time
from typing import Any


class TTLCache:
    def __init__(self):
        self._store: dict[str, tuple[float, Any]] = {}

    async def set(self, key: str, value: Any, ttl: int):
        self._store[key] = (time.time() + ttl, value)

    async def get(self, key: str):
        entry = self._store.get(key)
        if not entry:
            return None

        expires, value = entry
        if expires < time.time():
            self._store.pop(key, None)
            return None
        return value


def ticker_cache_key(exchange: str, symbol: str) -> str:
    return f"ticker:{exchange}:{symbol}"


def ohlcv_cache_key(exchange: str, symbol: str, tf: str, limit: int) -> str:
    return f"ohlcv:{exchange}:{symbol}:{tf}:{limit}"
