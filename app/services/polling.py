import asyncio
from app.core.logging import get_logger

logger = get_logger(__name__)

class PollingService:
    def __init__(self, exchange_service, ws_manager, poll_interval: float = 2.0):
        self.exchange = exchange_service
        self.ws = ws_manager
        self.poll_interval = poll_interval
        self._tasks: dict[str, asyncio.Task] = {}

    def start_stream(self, symbol: str):
        if symbol in self._tasks:
            return
        self._tasks[symbol] = asyncio.create_task(self._poll(symbol))

    async def _poll(self, symbol: str):
        last_price = None
        while True:
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                if ticker.price != last_price:
                    last_price = ticker.price
                    await self.ws.broadcast(symbol, ticker.model_dump())
            except Exception as e:
                logger.error("Polling error for %s: %s", symbol, e)
            await asyncio.sleep(self.poll_interval)
