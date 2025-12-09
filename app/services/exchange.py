import ccxt.async_support as ccxt_async
import ccxt
from typing import Any, cast

from app.services.cache import cache, ticker_cache_key, ohlcv_cache_key
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import (
    ExternalAPIError,
    InvalidSymbolError,
    RateLimitError,
)
from app.models.responses import (
    TickerResponse,
    OHLCVResponse,
    OHLCVCandle,
)

logger = get_logger(__name__)


class ExchangeService:
    def __init__(self) -> None:
        self._exchange: ccxt_async.Exchange | None = None

    async def startup(self) -> None:
        exchange_cls = getattr(ccxt_async, settings.exchange_name)
        self._exchange = exchange_cls(
            {
                "enableRateLimit": True,
                "timeout": settings.request_timeout_seconds * 1000,
            }
        )

        exchange = cast(ccxt_async.Exchange, self._exchange)
        await exchange.load_markets()
        logger.info("Exchange initialized: %s", exchange.id)

    async def shutdown(self) -> None:
        if self._exchange is not None:
            await self._exchange.close()

    async def fetch_ticker(self, symbol: str) -> TickerResponse:
        if self._exchange is None:
            raise ExternalAPIError("Exchange not initialized")

        exchange = cast(ccxt_async.Exchange, self._exchange)
        cache_key = ticker_cache_key(exchange.id, symbol)

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            ticker: dict[str, Any] = await exchange.fetch_ticker(symbol)
        except ccxt.BadSymbol:
            raise InvalidSymbolError(symbol)
        except ccxt.RateLimitExceeded:
            raise RateLimitError()
        except Exception as exc:
            logger.exception("Ticker fetch failed")
            raise ExternalAPIError("Failed to fetch ticker", {"symbol": symbol}) from exc

        response = TickerResponse(
            symbol=ticker["symbol"],
            price=float(ticker["last"]),
            bid=float(ticker["bid"]) if ticker.get("bid") is not None else None,
            ask=float(ticker["ask"]) if ticker.get("ask") is not None else None,
            volume=float(ticker["baseVolume"])
            if ticker.get("baseVolume") is not None
            else None,
            timestamp=int(ticker["timestamp"]),
        )

        cache.set(cache_key, response, settings.ticker_ttl_seconds)
        return response

    async def fetch_ohlcv(
        self, symbol: str, timeframe: str, limit: int
    ) -> OHLCVResponse:
        if self._exchange is None:
            raise ExternalAPIError("Exchange not initialized")

        exchange = cast(ccxt_async.Exchange, self._exchange)
        cache_key = ohlcv_cache_key(exchange.id, symbol, timeframe, limit)

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            raw = await exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit,
            )
        except ccxt.BadSymbol:
            raise InvalidSymbolError(symbol)
        except ccxt.RateLimitExceeded:
            raise RateLimitError()
        except Exception as exc:
            logger.exception("OHLCV fetch failed")
            raise ExternalAPIError("Failed to fetch OHLCV", {"symbol": symbol}) from exc

        candles = [
            OHLCVCandle(
                timestamp=int(c[0]),
                open=float(c[1]),
                high=float(c[2]),
                low=float(c[3]),
                close=float(c[4]),
                volume=float(c[5]),
            )
            for c in raw
        ]

        response = OHLCVResponse(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
        )

        cache.set(cache_key, response, settings.ohlcv_ttl_seconds)
        return response
exchange_service = ExchangeService()