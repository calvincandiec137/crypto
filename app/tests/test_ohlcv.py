import pytest
from app.models.responses import OHLCVResponse, OHLCVCandle
from app.services.exchange import exchange_service

@pytest.mark.asyncio
async def test_get_ohlcv_success(async_client, monkeypatch):
    async def fake_fetch_ohlcv(symbol: str, timeframe: str, limit: int):
        return OHLCVResponse(symbol=symbol, timeframe=timeframe, candles=[OHLCVCandle(timestamp=1, open=1, high=2, low=0.5, close=1.5, volume=10)])
    monkeypatch.setattr(exchange_service, "fetch_ohlcv", fake_fetch_ohlcv)
    resp = await async_client.get("/api/v1/ohlcv?symbol=BTC/USDT&timeframe=1m&limit=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC/USDT"
    assert len(data["candles"]) == 1
