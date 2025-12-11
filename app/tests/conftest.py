import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from app.main import app
from app.services.exchange import exchange_service
from app.services.redis_backend import RedisCacheBackend

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
async def clear_redis():
    try:
        cache = exchange_service.cache
        if isinstance(cache, RedisCacheBackend):
            await cache.flushdb()
    except Exception:
        pass
    yield
