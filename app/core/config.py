from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    EXCHANGE_NAME: str = "binance"
    DEFAULT_SYMBOL: str = "BTC/USDT"

    TICKER_TTL_SECONDS: int = 5
    OHLCV_TTL_SECONDS: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 10

    REDIS_URL: str | None = None
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
