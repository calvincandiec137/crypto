
# Crypto MCP Server

An async, Python-based MCP-style server that provides real-time and historical
cryptocurrency market data using live exchange APIs via CCXT.

The service exposes clean, deterministic HTTP endpoints suitable for LLM tools,
automation, and programmatic consumption.

---

## Overview

This project implements a lightweight market data server that fetches:

- **Real-time ticker prices**
- **Historical OHLCV (candlestick) data**

from major cryptocurrency exchanges (currently **Binance Spot**) using the
CCXT library.

The server is built with **FastAPI**, follows clean service separation, includes
error handling, caching, and is fully covered by async tests.

---

## Key Features

- Async FastAPI server
- CCXT-based exchange abstraction
- Real-time ticker endpoint
- Historical OHLCV endpoint
- In-memory TTL caching
- Unified error handling
- Deterministic JSON responses
- OpenAPI / Swagger documentation
- Fully tested using pytest + httpx
- MCP-friendly API design

---

## Architecture (High Level)

```

Client
↓
FastAPI Router (/api/v1)
↓
Exchange Service Layer
↓
CCXT (Binance)

```

### Core Layers

- **API Layer**  
  Handles request validation, response schemas, and routing.

- **Service Layer**  
  Contains exchange logic, caching, and exception mapping.

- **Integration Layer**  
  Uses CCXT to fetch data from Binance in async mode.

- **Cache Layer**  
  In-memory TTL cache to avoid excessive API calls.

---

## Endpoints

### 1. Get Ticker (Real-Time Price)

```

GET /api/v1/ticker
GET /api/v1/ticker?symbol=BTC/USDT

````

**Response**
```json
{
  "symbol": "BTC/USDT",
  "price": 92455.91,
  "bid": 92455.9,
  "ask": 92455.91,
  "volume": 20914.49,
  "timestamp": 1765338685013
}
````

* Uses CCXT `fetch_ticker`
* `price` corresponds to **last traded price**
* Cached for a short TTL

---

### 2. Get OHLCV (Historical Candles)

```
GET /api/v1/ohlcv?symbol=BTC/USDT&timeframe=1m&limit=5
```

**Response**

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
      "volume": 1.80049
    }
  ]
}
```

* Uses CCXT `fetch_ohlcv`
* Fully validated query parameters
* Returns structured candle objects
* Cached using exchange + symbol + timeframe + limit

---

## Error Handling

All errors are normalized into deterministic JSON responses.

### Invalid Symbol

```json
{
  "code": "INVALID_SYMBOL",
  "message": "Invalid symbol: FAKE/PAIR",
  "details": {
    "symbol": "FAKE/PAIR"
  }
}
```

### Rate Limit

```json
{
  "code": "RATE_LIMIT",
  "message": "Rate limit exceeded"
}
```

### External API Failure

```json
{
  "code": "EXTERNAL_API_ERROR",
  "message": "Ticker fetch failed"
}
```

Invalid query values (e.g. `limit > 1000`) return FastAPI’s built-in **422 validation errors**.

---

## Supported Symbols

Any **Binance Spot** pair supported by CCXT can be queried.

Examples:

```
BTC/USDT
ETH/USDT
SOL/USDT
BNB/USDT
XRP/USDT
ADA/USDT
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd crypto
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn app.main:app
```

Server will start at:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## Environment Configuration (Optional)

Create a `.env` file if customization is needed.

```env
EXCHANGE_NAME=binance
DEFAULT_SYMBOL=BTC/USDT
TICKER_TTL_SECONDS=5
OHLCV_TTL_SECONDS=60
REQUEST_TIMEOUT_SECONDS=10
LOG_LEVEL=INFO
```

Defaults are provided if `.env` is absent.

---

## Testing

### Run all tests

```bash
pytest
```

Test coverage includes:

* Successful ticker fetch
* Successful OHLCV fetch
* Invalid symbol handling
* Unified error response behavior

Async tests use **httpx ASGITransport** and fully mock the exchange service where required.

---

## Manual Validation

The implementation was manually validated by:

* Calling endpoints via `curl`
* Comparing prices against:

  * Binance web UI
  * Binance REST API
  * CCXT direct calls
* Verifying cache behavior via logs
* Confirming correct HTTP status codes for error scenarios

---

## MCP Alignment

This server follows MCP-style principles:

* Stateless HTTP endpoints
* Deterministic JSON responses
* Strict input/output schemas
* Tool-call friendly APIs
* No session or user state
* Suitable for LLM integration and automation

---

## Known Limitations

* Single exchange (Binance)
* In-memory cache only
* No WebSocket streaming
* No persistent storage

These were deliberate scope decisions given time constraints.

---

## Future Improvements

* Redis-based cache
* Multi-exchange support
* WebSocket price streaming
* Authentication and rate limiting
* Deployment configuration

---


