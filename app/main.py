from fastapi import FastAPI

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

configure_logging()

app = FastAPI(title="Crypto MCP Server", version="0.1.0")
app.include_router(api_router)

app.add_exception_handler(ExternalAPIError, external_api_error_handler)
app.add_exception_handler(InvalidSymbolError, invalid_symbol_error_handler)
app.add_exception_handler(RateLimitError, rate_limit_error_handler)


@app.on_event("startup")
async def startup() -> None:
    await exchange_service.startup()


@app.on_event("shutdown")
async def shutdown() -> None:
    await exchange_service.shutdown()
