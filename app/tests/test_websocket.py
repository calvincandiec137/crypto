import pytest
from app.main import app
from fastapi.testclient import TestClient
from app.models.responses import TickerResponse
from app.services.exchange import exchange_service

@pytest.mark.asyncio
async def test_websocket_ticker_stream(monkeypatch):
    async def fake_fetch_ticker(symbol: str):
        return TickerResponse(symbol=symbol, price=500.0, bid=499.0, ask=501.0, volume=1.0, timestamp=999)
    monkeypatch.setattr(exchange_service, "fetch_ticker", fake_fetch_ticker)

    client = TestClient(app)

    with client.websocket_connect("/api/v1/ws/ticker?symbol=BTC/USDT") as ws:
        msg = ws.receive_json()
        assert msg["symbol"] == "BTC/USDT"
        assert msg["price"] == 500.0
