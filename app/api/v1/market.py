from fastapi import APIRouter, Depends, Query
from app.services.exchange import exchange_service
from app.models.responses import TickerResponse, OHLCVResponse
from app.core.config import settings

router = APIRouter()


def get_exchange_service():
    return exchange_service


@router.get("/ticker", response_model=TickerResponse)
async def get_ticker(
    symbol: str | None = Query(None),
    service=Depends(get_exchange_service),
):
    return await service.fetch_ticker(symbol or settings.default_symbol)


@router.get("/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv(
    symbol: str = Query(...),
    timeframe: str = Query("1m"),
    limit: int = Query(100, ge=1, le=1000),
    service=Depends(get_exchange_service),
):
    return await service.fetch_ohlcv(symbol, timeframe, limit)
