import pytest
from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app
from app.services.exchange import exchange_service
from app.models.responses import TickerResponse
from app.core.exceptions import InvalidSymbolError


@pytest.mark.asyncio
async def test_get_ticker_success(monkeypatch):
    async def fake_fetch_ticker(symbol: str):
        return TickerResponse(
            symbol=symbol,
            price=100.0,
            bid=99.5,
            ask=100.5,
            volume=123.0,
            timestamp=1234567890,
        )

    monkeypatch.setattr(exchange_service, "fetch_ticker", fake_fetch_ticker)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/ticker?symbol=BTC/USDT")

    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC/USDT"
    assert data["price"] == 100.0


@pytest.mark.asyncio
async def test_get_ticker_invalid_symbol(monkeypatch):
    async def fake_fetch_ticker(symbol: str):
        raise InvalidSymbolError(symbol)

    monkeypatch.setattr(exchange_service, "fetch_ticker", fake_fetch_ticker)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/ticker?symbol=BAD/PAIR")

    assert resp.status_code == 400
    data = resp.json()
    assert data["code"] == "INVALID_SYMBOL"
