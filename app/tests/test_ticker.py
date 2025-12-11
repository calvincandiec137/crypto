import pytest
from app.models.responses import TickerResponse
from app.services.exchange import exchange_service

@pytest.mark.asyncio
async def test_get_ticker_success(async_client, monkeypatch):
    async def fake_fetch_ticker(symbol: str):
        return TickerResponse(symbol=symbol, price=100.0, bid=99.0, ask=101.0, volume=1.0, timestamp=123)
    monkeypatch.setattr(exchange_service, "fetch_ticker", fake_fetch_ticker)
    resp = await async_client.get("/api/v1/ticker?symbol=BTC/USDT")
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC/USDT"
    assert data["price"] == 100.0

@pytest.mark.asyncio
async def test_get_ticker_invalid_symbol(async_client, monkeypatch):
    from app.core.exceptions import InvalidSymbolError
    async def fake_fetch_ticker(symbol: str):
        raise InvalidSymbolError(symbol)
    monkeypatch.setattr(exchange_service, "fetch_ticker", fake_fetch_ticker)
    resp = await async_client.get("/api/v1/ticker?symbol=FAKE/PAIR")
    assert resp.status_code == 400
    data = resp.json()
    assert data["code"] == "INVALID_SYMBOL"
