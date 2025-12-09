from pydantic import BaseModel, Field


class TickerRequest(BaseModel):
    symbol: str | None = Field(default=None, description="Trading pair symbol")


class OHLCVRequest(BaseModel):
    symbol: str
    timeframe: str = Field(default="1m")
    limit: int = Field(default=100, ge=1, le=1000)
