from fastapi import APIRouter, Query
from app.services.exchange import exchange_service
from app.models.responses import TickerResponse, OHLCVResponse
from app.core.config import settings

router = APIRouter()

@router.get("/ticker", response_model=TickerResponse)
async def get_ticker(symbol: str | None = Query(None)):
    return await exchange_service.fetch_ticker(symbol or settings.DEFAULT_SYMBOL)

@router.get("/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv(
    symbol: str = Query(...),
    timeframe: str = Query("1m"),
    limit: int = Query(100, ge=1, le=1000),
):
    return await exchange_service.fetch_ohlcv(symbol, timeframe, limit)
