from fastapi import Request
from fastapi.responses import JSONResponse, Response
from fastapi import status
from pydantic import BaseModel

class ExternalAPIError(Exception):
    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}

class InvalidSymbolError(Exception):
    def __init__(self, symbol: str):
        self.symbol = symbol

class RateLimitError(Exception):
    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict | None = None

async def external_api_error_handler(_: Request, exc: ExternalAPIError) -> Response:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=ErrorResponse(code="EXTERNAL_API_ERROR", message=exc.message, details=exc.details).model_dump(),
    )

async def invalid_symbol_error_handler(_: Request, exc: InvalidSymbolError) -> Response:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(code="INVALID_SYMBOL", message=f"Invalid symbol: {exc.symbol}", details={"symbol": exc.symbol}).model_dump(),
    )

async def rate_limit_error_handler(_: Request, exc: RateLimitError) -> Response:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(code="RATE_LIMIT", message=exc.message).model_dump(),
    )
