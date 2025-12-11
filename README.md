
# Crypto MCP Server

A high-performance, async market-data server delivering **real-time** and **historical** cryptocurrency data through REST and WebSocket APIs.  
Built with **FastAPI**, **CCXT**, **Redis**, and a background polling engine.

Designed with LLM-friendly, deterministic schemas and clean service architecture.

---

# Features

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
- MCP-style deterministic request/response formats

---

# Architecture Overview

## High-Level Flow

```

REST Request → FastAPI → ExchangeService → Cache → CCXT → Exchange
WebSocket Client → WS Manager → PollingService → ExchangeService → Cache

```

## Component Responsibilities

| Component | Role |
|----------|------|
| **API Layer** | HTTP/WS endpoints, validation, schemas |
| **ExchangeService** | Fetches, normalizes, and caches market data |
| **PollingService** | Background tasks that fetch ticker updates |
| **WebSocketManager** | Manages active WS clients + broadcasts updates |
| **RedisCacheBackend** | Primary shared cache for fast responses |
| **TTLCache** | Fallback in-memory cache for environments without Redis |
| **CCXT (Binance)** | Actual market data retrieval |

---

# System Architecture Diagram (ASCII)

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


---

# Endpoints

## 1. Real-Time Ticker (REST)

```
GET /api/v1/ticker?symbol=BTC/USDT
```

Example:

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

---

## 2. Historical OHLCV

```
GET /api/v1/ohlcv?symbol=BTC/USDT&timeframe=1m&limit=100
```

Example:

```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1m",
  "candles": [
    {
      "timestamp": 1765338600000,
      "open": 92516.86,
      "high": 92516.86,
      "low": 92440.75,
      "close": 92440.76,
      "volume": 1.80
    }
  ]
}
```

---

## 3. Real-Time Ticker (WebSocket)

```
ws://127.0.0.1:8000/api/v1/ws/ticker?symbol=BTC/USDT
```

Receives updates every time the background polling detects a price change.

Example message:

```json
{"symbol": "BTC/USDT", "price": 89932.32, "timestamp": 1765426653009}
```

---

# Redis Caching

Redis stores:

* Latest ticker snapshot
* Latest OHLCV snapshot

Benefits:

* Fast REST responses
* Reduced CCXT rate usage
* Shared state across workers
* Smooth WebSocket fanout

Check Redis keys:

```
redis-cli keys "*ticker*"
redis-cli ttl ticker:binance:BTC/USDT
```

---

# Installation & Setup

## 1. Clone repo

```
git clone https://github.com/calvincandiec137/crypto
cd crypto
```

## 2. Virtual environment

```
python -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```
pip install -r requirements.txt
```

## 4. Start Redis

Docker:

```
systemctl start redis
export REDIS_URL="redis://localhost:PORT"
```

## 5. Run server

```
uvicorn app.main:app --reload
```

---

# Configuration

`.env` file is optional but supported:

```env
REDIS_URL=redis://localhost:PORT
EXCHANGE_NAME=binance
DEFAULT_SYMBOL=BTC/USDT
TICKER_TTL_SECONDS=5
OHLCV_TTL_SECONDS=60
REQUEST_TIMEOUT_SECONDS=10
```

---

# Testing

```
pytest
```

Covers:

* Ticker endpoint
* OHLCV endpoint
* Error handling layer

WebSocket & Redis tests can be added.

---

# Manual Testing

REST:

```
curl "http://127.0.0.1:8000/api/v1/ticker?symbol=BTC/USDT"
```

WebSocket:

```
websocat "ws://127.0.0.1:8000/api/v1/ws/ticker?symbol=BTC/USDT"
```

Redis:

```
redis-cli keys "*"
redis-cli monitor
```

---

# MCP Compatibility

* Stateless
* Deterministic schemas
* Ideal for LLM integration
* Predictable, structured outputs

---

# Future Improvements

* Redis Pub/Sub fanout
* Multi-exchange routing
* WebSocket OHLCV streaming
* Rate limiting using Redis
* Horizontal scaling with worker coordination
* Prometheus `/metrics` endpoint

---

