import ccxt.async_support as ccxt_async
import ccxt
from typing import Any, cast
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalAPIError, InvalidSymbolError, RateLimitError
from app.models.responses import TickerResponse, OHLCVResponse, OHLCVCandle

from app.services.local_cache import TTLCacheBackend
from app.services.redis_backend import RedisCacheBackend

logger = get_logger(__name__)

# select cache backend (module-level so tests can import exchange_service)
_cache_backend = None
if settings.REDIS_URL:
    try:
        _cache_backend = RedisCacheBackend(settings.REDIS_URL)
    except Exception:
        _cache_backend = TTLCacheBackend()
else:
    _cache_backend = TTLCacheBackend()


class ExchangeService:
    def __init__(self, cache_backend):
        self.cache = cache_backend
        self._exchange: ccxt_async.Exchange | None = None

    async def startup(self):
        cls = getattr(ccxt_async, settings.EXCHANGE_NAME)
        self._exchange = cls({"enableRateLimit": True, "timeout": settings.REQUEST_TIMEOUT_SECONDS * 1000})
        await self._exchange.load_markets()
        logger.info("Exchange initialized: %s", getattr(self._exchange, "id", settings.EXCHANGE_NAME))

    async def shutdown(self):
        if self._exchange:
            await self._exchange.close()

    async def fetch_ticker(self, symbol: str) -> TickerResponse:
        ex = cast(ccxt_async.Exchange, self._exchange)
        if ex is None:
            raise ExternalAPIError("Exchange not initialized")
        key = f"ticker:{ex.id}:{symbol}"
        cached = await self.cache.get(key)
        if cached:
            return TickerResponse(**cached) if isinstance(cached, dict) else cached

        try:
            raw: dict[str, Any] = await ex.fetch_ticker(symbol)
        except ccxt.BadSymbol:
            raise InvalidSymbolError(symbol)
        except ccxt.RateLimitExceeded:
            raise RateLimitError()
        except Exception as e:
            raise ExternalAPIError("Ticker fetch failed", {"symbol": symbol}) from e

        resp = TickerResponse(
            symbol=raw.get("symbol", symbol),
            price=float(raw.get("last")),
            bid=raw.get("bid"),
            ask=raw.get("ask"),
            volume=raw.get("baseVolume"),
            timestamp=int(raw.get("timestamp")),
        )
        await self.cache.set(key, resp.model_dump(), settings.TICKER_TTL_SECONDS)
        return resp

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> OHLCVResponse:
        ex = cast(ccxt_async.Exchange, self._exchange)
        if ex is None:
            raise ExternalAPIError("Exchange not initialized")
        key = f"ohlcv:{ex.id}:{symbol}:{timeframe}:{limit}"
        cached = await self.cache.get(key)
        if cached:
            return OHLCVResponse(**cached) if isinstance(cached, dict) else cached

        try:
            raw = await ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        except ccxt.BadSymbol:
            raise InvalidSymbolError(symbol)
        except ccxt.RateLimitExceeded:
            raise RateLimitError()
        except Exception as e:
            raise ExternalAPIError("OHLCV fetch failed", {"symbol": symbol}) from e

        candles = [
            OHLCVCandle(timestamp=c[0], open=c[1], high=c[2], low=c[3], close=c[4], volume=c[5])
            for c in raw
        ]
        resp = OHLCVResponse(symbol=symbol, timeframe=timeframe, candles=candles)
        await self.cache.set(key, resp.model_dump(), settings.OHLCV_TTL_SECONDS)
        return resp

# module-level instance exported for routes/tests
exchange_service = ExchangeService(_cache_backend)
