import ccxt.async_support as ccxt_async
import ccxt
from typing import Any, cast

from app.services.cache import cache, ticker_cache_key, ohlcv_cache_key
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalAPIError, InvalidSymbolError, RateLimitError
from app.models.responses import TickerResponse, OHLCVResponse, OHLCVCandle

logger = get_logger(__name__)


class ExchangeService:
    def __init__(self):
        self._exchange: ccxt_async.Exchange | None = None

    async def startup(self):
        cls = getattr(ccxt_async, settings.exchange_name)
        self._exchange = cls(
            {"enableRateLimit": True, "timeout": settings.request_timeout_seconds * 1000}
        )
        exchange = cast(ccxt_async.Exchange, self._exchange)
        await exchange.load_markets()
        logger.info("Exchange initialized: %s", exchange.id)

    async def shutdown(self):
        if self._exchange:
            await self._exchange.close()

    async def fetch_ticker(self, symbol: str) -> TickerResponse:
        ex = cast(ccxt_async.Exchange, self._exchange)
        key = ticker_cache_key(ex.id, symbol)

        if cached := cache.get(key):
            return cached

        try:
            data: dict[str, Any] = await ex.fetch_ticker(symbol)
        except ccxt.BadSymbol:
            raise InvalidSymbolError(symbol)
        except ccxt.RateLimitExceeded:
            raise RateLimitError()
        except Exception as e:
            raise ExternalAPIError("Ticker fetch failed", {"symbol": symbol}) from e

        resp = TickerResponse(
            symbol=data["symbol"],
            price=float(data["last"]),
            bid=data.get("bid"),
            ask=data.get("ask"),
            volume=data.get("baseVolume"),
            timestamp=int(data["timestamp"]),
        )

        cache.set(key, resp, settings.ticker_ttl_seconds)
        return resp

    async def fetch_ohlcv(self, symbol: str, tf: str, limit: int) -> OHLCVResponse:
        ex = cast(ccxt_async.Exchange, self._exchange)
        key = ohlcv_cache_key(ex.id, symbol, tf, limit)

        if cached := cache.get(key):
            return cached

        try:
            raw = await ex.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
        except ccxt.BadSymbol:
            raise InvalidSymbolError(symbol)
        except ccxt.RateLimitExceeded:
            raise RateLimitError()
        except Exception as e:
            raise ExternalAPIError("OHLCV fetch failed", {"symbol": symbol}) from e

        candles = [
            OHLCVCandle(
                timestamp=c[0],
                open=c[1],
                high=c[2],
                low=c[3],
                close=c[4],
                volume=c[5],
            )
            for c in raw
        ]

        resp = OHLCVResponse(symbol=symbol, timeframe=tf, candles=candles)
        cache.set(key, resp, settings.ohlcv_ttl_seconds)
        return resp


exchange_service = ExchangeService()
