from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status
from pydantic import BaseModel


class ExternalAPIError(Exception):
    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}


class InvalidSymbolError(Exception):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol


class RateLimitError(Exception):
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        self.message = message


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict | None = None


async def external_api_error_handler(
    request: Request, exc: ExternalAPIError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=ErrorResponse(
            code="EXTERNAL_API_ERROR",
            message=exc.message,
            details=exc.details,
        ).model_dump(),
    )


async def invalid_symbol_error_handler(
    request: Request, exc: InvalidSymbolError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            code="INVALID_SYMBOL",
            message=f"Invalid symbol: {exc.symbol}",
            details={"symbol": exc.symbol},
        ).model_dump(),
    )


async def rate_limit_error_handler(
    request: Request, exc: RateLimitError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            code="RATE_LIMIT",
            message=exc.message,
            details=None,
        ).model_dump(),
    )
