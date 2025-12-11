from fastapi import FastAPI, WebSocket
from app.api.router import api_router
from app.core.logging import configure_logging
from app.core.exceptions import (
    ExternalAPIError,
    InvalidSymbolError,
    RateLimitError,
    external_api_error_handler,
    invalid_symbol_error_handler,
    rate_limit_error_handler,
)
from app.services.exchange import exchange_service
from app.services.websocket_manager import ws_manager  
from app.services.polling import PollingService

from app.core.config import settings

configure_logging()

app = FastAPI(title="Crypto MCP Server")
app.include_router(api_router)

# register exception handlers
app.add_exception_handler(ExternalAPIError, external_api_error_handler)
app.add_exception_handler(InvalidSymbolError, invalid_symbol_error_handler)
app.add_exception_handler(RateLimitError, rate_limit_error_handler)

# create polling service instance here (uses module-level exchange_service & ws_manager)
polling_service = PollingService(exchange_service, ws_manager, poll_interval=2.0)

@app.on_event("startup")
async def startup():
    await exchange_service.startup()

@app.on_event("shutdown")
async def shutdown():
    await exchange_service.shutdown()

@app.websocket("/api/v1/ws/ticker")
async def ws_ticker(websocket: WebSocket, symbol: str):
    await ws_manager.connect(symbol, websocket)

    # send one immediate ticker so TestClient receives something
    ticker = await exchange_service.fetch_ticker(symbol)
    await websocket.send_json(ticker.model_dump())

    polling_service.start_stream(symbol)

    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        await ws_manager.disconnect(symbol, websocket)
