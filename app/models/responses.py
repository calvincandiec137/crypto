from pydantic import BaseModel
from typing import List

class TickerResponse(BaseModel):
    symbol: str
    price: float
    bid: float | None
    ask: float | None
    volume: float | None
    timestamp: int

class OHLCVCandle(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class OHLCVResponse(BaseModel):
    symbol: str
    timeframe: str
    candles: List[OHLCVCandle]
