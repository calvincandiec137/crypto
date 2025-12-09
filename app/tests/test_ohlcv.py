import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.exchange import exchange_service
from app.models.responses import OHLCVResponse, OHLCVCandle


@pytest.mark.asyncio
async def test_get_ohlcv_success(monkeypatch):
    async def fake_fetch_ohlcv(symbol: str, timeframe: str, limit: int):
        return OHLCVResponse(
            symbol=symbol,
            timeframe=timeframe,
            candles=[
                OHLCVCandle(
                    timestamp=1234567890,
                    open=1.0,
                    high=2.0,
                    low=0.5,
                    close=1.5,
                    volume=10.0,
                )
            ],
        )

    monkeypatch.setattr(exchange_service, "fetch_ohlcv", fake_fetch_ohlcv)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/ohlcv?symbol=BTC/USDT&timeframe=1m&limit=1"
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC/USDT"
    assert len(data["candles"]) == 1
