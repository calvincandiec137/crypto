import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    exchange_name: str = os.getenv("EXCHANGE_NAME", "binance")
    default_symbol: str = os.getenv("DEFAULT_SYMBOL", "BTC/USDT")

    ticker_ttl_seconds: int = int(os.getenv("TICKER_TTL_SECONDS", "5"))
    ohlcv_ttl_seconds: int = int(os.getenv("OHLCV_TTL_SECONDS", "60"))

    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
