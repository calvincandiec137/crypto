# Crypto MCP Server

Async Python MCP-style server providing real-time and historical cryptocurrency
market data using CCXT.

## Features
- Real-time ticker endpoint
- Historical OHLCV endpoint
- Async CCXT integration (Binance)
- In-memory TTL cache
- Unified error handling
- Fully tested with pytest

## Endpoints
GET /api/v1/ticker  
GET /api/v1/ohlcv

## Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app

## MCP Alignment
- Deterministic JSON responses
- Strict input/output schemas
- Stateless endpoints
- Tool-call friendly HTTP API

## Known Limitations
- Single exchange (Binance)
- In-memory cache only
- No WebSocket streaming

## Future Improvements
- Redis cache
- Multi-exchange support
- WebSocket price streaming
