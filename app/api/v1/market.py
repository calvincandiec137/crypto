from fastapi import APIRouter, Depends
from app.models.requests import TickerRequest, OHLCVRequest
from app.models.responses import TickerResponse, OHLCVResponse
from app.services.exchange import exchange_service
from app.core.config import settings

router = APIRouter()


def get_exchange_service():
    return exchange_service


@router.get("/ticker", response_model=TickerResponse)
async def get_ticker(
    symbol: str | None = None, service=Depends(get_exchange_service)
) -> TickerResponse:
    sym = symbol or settings.default_symbol
    return await service.fetch_ticker(sym)


@router.get("/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv(
    symbol: str,
    timeframe: str = "1m",
    limit: int = 100,
    service=Depends(get_exchange_service),
) -> OHLCVResponse:
    request = OHLCVRequest(symbol=symbol, timeframe=timeframe, limit=limit)
    return await service.fetch_ohlcv(
        request.symbol, request.timeframe, request.limit
    )
