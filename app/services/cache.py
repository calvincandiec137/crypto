import time
from typing import Any


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None

        exp, value = item
        if exp < time.time():
            self._store.pop(key, None)
            return None

        return value


cache = TTLCache()


def ticker_cache_key(exchange: str, symbol: str) -> str:
    return f"ticker:{exchange}:{symbol}"


def ohlcv_cache_key(exchange: str, symbol: str, timeframe: str, limit: int) -> str:
    return f"ohlcv:{exchange}:{symbol}:{timeframe}:{limit}"
