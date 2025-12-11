import pytest
from app.core.exceptions import ExternalAPIError
from app.services.exchange import exchange_service

@pytest.mark.asyncio
async def test_external_error_handler(async_client, monkeypatch):
    async def fake_fetch_ticker(symbol: str):
        raise ExternalAPIError("TEST")
    monkeypatch.setattr(exchange_service, "fetch_ticker", fake_fetch_ticker)
    resp = await async_client.get("/api/v1/ticker?symbol=BTC/USDT")
    assert resp.status_code == 502
    data = resp.json()
    assert data["code"] == "EXTERNAL_API_ERROR"
