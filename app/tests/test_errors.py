import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import APIRouter

from app.main import app
from app.core.exceptions import ExternalAPIError

router = APIRouter()


@router.get("/test/error")
async def error_route():
    raise ExternalAPIError("Boom", {"detail": "test"})


app.include_router(router)


@pytest.mark.asyncio
async def test_external_error_handler():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/test/error")

    assert resp.status_code == 502
    data = resp.json()
    assert data["code"] == "EXTERNAL_API_ERROR"
    assert data["message"] == "Boom"
