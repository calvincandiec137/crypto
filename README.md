# Crypto MCP Server

A high-performance, async market-data server delivering real-time and historical cryptocurrency data through REST and WebSocket APIs.

Built with FastAPI, CCXT, Redis, and a background polling engine.

**Context:** This server exposes a deterministic REST API designed to be easily consumed by LLM Agents (via Model Context Protocol tools) or standard frontend clients.

https://github.com/user-attachments/assets/0ef7e8d9-002f-4bcd-9c44-9aa8e89fb27e


## Features

### Market Data
- Real-time ticker (REST)
- Real-time ticker (WebSocket streaming)
- Historical OHLCV (candlesticks)
- Exchange data normalized into stable JSON responses

### Infrastructure
- Redis caching backend (primary)
- In-memory TTL cache (fallback)
- Background polling service for continuous price updates
- Multi-client WebSocket broadcasting
- CCXT async integration (Binance Spot)

### Engineering
- Modular service architecture
- Deterministic error model
- Async test suite (pytest + httpx)
- Clean separation of API, services, and integration layers

## Design Decisions & Architecture

### Why this Architecture?

**Redis as "Hot Cache" (Decoupling):** LLM Agents often retry or spam requests. By decoupling the data fetching (Polling Service) from the data serving (API), we ensure that 1,000 API requests only result in 1 request to the Binance Exchange. This prevents rate-limit bans.

**WebSockets for Efficiency:** Instead of an agent polling an endpoint every second to check for price movement, the WebSocket pushes updates only when data changes. This reduces network overhead and latency.

**AsyncIO + CCXT:** Crypto markets move in milliseconds. Using `ccxt.async_support` ensures non-blocking I/O, allowing the server to handle concurrent WebSocket clients while simultaneously polling the exchange without thread locking.

### System Architecture Diagram

```
                                  ┌──────────────────────────┐
                                  │        Clients           │
                                  │   REST / WebSocket       │
                                  └────────────┬─────────────┘
                                               │
                                  ┌────────────▼────────────┐
                                  │        FastAPI          │
                                  │ (Routers + Lifespan)    │
                                  └────────────┬────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
         ┌──────────▼─────────┐    ┌───────────▼───────────┐    ┌─────────▼─────────┐
         │ REST API Layer     │    │ WebSocket Layer       │    │ PollingService    │
         │ /api/v1/...        │    │ /ws/ticker            │    │ (Background loop) │
         └──────────┬─────────┘    └───────────┬───────────┘    └─────────┬─────────┘
                    │                          │                          │
                    └──────────────────────────┼──────────────────────────┘
                                               │
                                   ┌───────────▼───────────┐
                                   │    ExchangeService    │
                                   │ (Normalization+Cache) │
                                   └───────────┬───────────┘
                                               │
                     ┌─────────────────────────┼───────────────────┐
                     │                         │                   │
        ┌────────────▼──────────┐   ┌──────────▼─────────┐   ┌─────▼─────────────┐
        │ RedisCacheBackend     │   │ TTLCache (fallback)│   │ CCXT (Binance)    │
        └───────────────────────┘   └────────────────────┘   └───────────────────┘
```

### Component Responsibilities

| Component | Role |
|-----------|------|
| API Layer | HTTP/WS endpoints, validation, schemas |
| ExchangeService | Fetches, normalizes, and caches market data |
| PollingService | Background tasks that fetch ticker updates |
| WebSocketManager | Manages active WS clients + broadcasts updates |
| RedisCacheBackend | Primary shared cache for fast responses |
| CCXT (Binance) | Actual market data retrieval |

## Endpoints

### 1. Real-Time Ticker (REST)

```http
GET /api/v1/ticker?symbol=BTC/USDT
```

**Response (Deterministic):**

```json
{
  "symbol": "BTC/USDT",
  "price": 90012.42,
  "bid": 90012.41,
  "ask": 90012.42,
  "volume": 21000.12,
  "timestamp": 1765338616002
}
```

### 2. Historical OHLCV

```http
GET /api/v1/ohlcv?symbol=BTC/USDT&timeframe=1m&limit=100
```

### 3. Real-Time Ticker (WebSocket)

```
ws://127.0.0.1:8000/api/v1/ws/ticker?symbol=BTC/USDT
```

## Redis Caching

Redis stores the latest ticker and OHLCV snapshots.

**Production Note:** In development, `keys *` is fine. In production, we use `SCAN` to avoid blocking the Redis thread.

```bash
# Check keys (Safe way)
redis-cli --scan --pattern "*ticker*"

# Check TTL
redis-cli ttl ticker:binance:BTC/USDT
```

## Installation & Setup

### 1. Clone repo

```bash
git clone https://github.com/calvincandiec137/crypto
cd crypto
```

### 2. Virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Redis

```bash
# Docker example
docker run --name redis -p 6379:6379 -d redis
```

### 5. Run server

```bash
uvicorn app.main:app --reload
```

## Configuration

Configure via `.env` file (see `.env.example`):

```env
REDIS_URL=redis://localhost:6379
EXCHANGE_NAME=binance
DEFAULT_SYMBOL=BTC/USDT
TICKER_TTL_SECONDS=5
POLLING_INTERVAL_SECONDS=2.0
```

## Testing

Run the full async test suite:

```bash
pytest
```

## Future Improvements

- **Redis Pub/Sub:** Currently using polling for WS updates; moving to Redis Pub/Sub would allow horizontal scaling of WebSocket servers.
- **Metrics:** Add Prometheus `/metrics` to track exchange latency and cache hit rates.
- **Rate Limiting:** Implement token bucket limits on the API side using Redis.
