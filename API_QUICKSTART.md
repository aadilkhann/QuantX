# QuantX API Quick Start

## 🚀 Running the API Server

### 1. Install Dependencies
```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
pip install fastapi uvicorn websockets python-multipart
```

### 2. Start the Server
```bash
# From project root
PYTHONPATH="$(pwd)/src" python3 -m uvicorn quantx.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the convenience script:
```bash
PYTHONPATH="$(pwd)/src" python3 src/quantx/api/main.py
```

### 3. Access the API

- **API Root**: http://localhost:8000/
- **Interactive Docs**: http://localhost:8000/docs ⭐
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws/live

---

## 📡 API Endpoints

### Health & Info
- `GET /` - API root
- `GET /health` - System health check
- `GET /api/v1/info` - System information

### Engine Control
- `GET /api/v1/engine/status` - Get engine status
- `POST /api/v1/engine/start` - Start trading engine
- `POST /api/v1/engine/stop` - Stop trading engine
- `POST /api/v1/engine/pause` - Pause engine
- `POST /api/v1/engine/resume` - Resume engine
- `GET /api/v1/engine/statistics` - Engine stats

### Positions
- `GET /api/v1/positions` - List all positions
- `GET /api/v1/positions/{symbol}` - Get position for symbol
- `POST /api/v1/positions/{symbol}/close` - Close position
- `GET /api/v1/positions/summary` - Positions summary

### Orders
- `POST /api/v1/orders` - Place new order
- `GET /api/v1/orders` - List all orders
- `GET /api/v1/orders/{order_id}` - Get specific order
- `DELETE /api/v1/orders/{order_id}` - Cancel order
- `GET /api/v1/orders/history` - Order history

### P&L
- `GET /api/v1/pnl/current` - Current P&L snapshot
- `GET /api/v1/pnl/daily` - Daily P&L history
- `GET /api/v1/pnl/equity-curve` - Equity curve data
- `GET /api/v1/pnl/metrics` - Performance metrics
- `GET /api/v1/pnl/by-symbol` - P&L by symbol

### WebSocket
- `WS /ws/live` - Real-time updates

---

## 🧪 Try It Out

### Using Browser (Easiest!)
1. Start the server
2. Open http://localhost:8000/docs
3. Try the interactive API docs!

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Get engine status
curl http://localhost:8000/api/v1/engine/status

# Get positions
curl http://localhost:8000/api/v1/positions

# Place order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NSE:INFY",
    "quantity": 10,
    "order_type": "market",
    "side": "buy"
  }'
```

### Using Python
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Get positions
response = requests.get("http://localhost:8000/api/v1/positions")
print(response.json())

# Place order
order = {
    "symbol": "NSE:INFY",
    "quantity": 10,
    "order_type": "market",
    "side": "buy"
}
response = requests.post("http://localhost:8000/api/v1/orders", json=order)
print(response.json())
```

### WebSocket Example
```python
import asyncio
import websockets
import json

async def listen():
    async with websockets.connect("ws://localhost:8000/ws/live") as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Update: {data}")

asyncio.run(listen())
```

---

## 📊 What's Working

✅ FastAPI server with auto-docs  
✅ WebSocket for real-time updates  
✅ All REST endpoints defined  
✅ CORS configured for frontend  
✅ Pydantic models for validation  

⏳ **Note**: Endpoints return mock data for now. Will connect to actual QuantX engine in next step!

---

## 🎯 Next Steps

1. ✅ API backend complete
2. ⏳ Connect to actual LiveExecutionEngine
3. ⏳ Build Next.js frontend
4. ⏳ Real-time data integration

---

**Status**: API Backend Ready!  
**Ready for**: Frontend development
