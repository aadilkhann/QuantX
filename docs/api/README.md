# API Documentation
# QuantX Trading System

**Version**: 1.0  
**Base URL**: `http://localhost:8000/api/v1`  
**Authentication**: Bearer Token (JWT)

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Strategies API](#2-strategies-api)
3. [Backtesting API](#3-backtesting-api)
4. [Live Trading API](#4-live-trading-api)
5. [Data API](#5-data-api)
6. [Portfolio API](#6-portfolio-api)
7. [ML Models API](#7-ml-models-api)
8. [WebSocket API](#8-websocket-api)
9. [Error Codes](#9-error-codes)

---

## 1. Authentication

### 1.1 Login

**Endpoint**: `POST /auth/login`

**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 1.2 Using Authentication

Include the token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 2. Strategies API

### 2.1 List Strategies

**Endpoint**: `GET /strategies`

**Query Parameters**:
- `type` (optional): Filter by type (`rule_based`, `ai_powered`, `hybrid`)
- `status` (optional): Filter by status (`active`, `inactive`)

**Response**:
```json
{
  "strategies": [
    {
      "id": "uuid",
      "name": "MA Crossover",
      "type": "rule_based",
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z",
      "config": {
        "fast_period": 50,
        "slow_period": 200
      }
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

### 2.2 Get Strategy Details

**Endpoint**: `GET /strategies/{strategy_id}`

**Response**:
```json
{
  "id": "uuid",
  "name": "MA Crossover",
  "type": "rule_based",
  "status": "active",
  "description": "Simple moving average crossover strategy",
  "config": {
    "fast_period": 50,
    "slow_period": 200,
    "symbols": ["AAPL", "GOOGL"]
  },
  "performance": {
    "total_return": 0.15,
    "sharpe_ratio": 1.5,
    "max_drawdown": -0.10
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T00:00:00Z"
}
```

### 2.3 Create Strategy

**Endpoint**: `POST /strategies`

**Request**:
```json
{
  "name": "My Strategy",
  "type": "rule_based",
  "description": "Description of strategy",
  "config": {
    "fast_period": 50,
    "slow_period": 200,
    "symbols": ["AAPL", "GOOGL"],
    "initial_capital": 100000
  },
  "code": "# Python code for strategy\nclass MyStrategy(RuleBasedStrategy):\n    ..."
}
```

**Response**:
```json
{
  "id": "uuid",
  "name": "My Strategy",
  "status": "created",
  "message": "Strategy created successfully"
}
```

### 2.4 Update Strategy

**Endpoint**: `PUT /strategies/{strategy_id}`

**Request**: Same as Create Strategy

**Response**:
```json
{
  "id": "uuid",
  "message": "Strategy updated successfully"
}
```

### 2.5 Delete Strategy

**Endpoint**: `DELETE /strategies/{strategy_id}`

**Response**:
```json
{
  "message": "Strategy deleted successfully"
}
```

### 2.6 Activate/Deactivate Strategy

**Endpoint**: `POST /strategies/{strategy_id}/activate`  
**Endpoint**: `POST /strategies/{strategy_id}/deactivate`

**Response**:
```json
{
  "id": "uuid",
  "status": "active",
  "message": "Strategy activated successfully"
}
```

---

## 3. Backtesting API

### 3.1 Run Backtest

**Endpoint**: `POST /backtests`

**Request**:
```json
{
  "strategy_id": "uuid",
  "config": {
    "start_date": "2020-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 100000,
    "commission": 0.001,
    "slippage": 0.0005,
    "data_frequency": "1d"
  }
}
```

**Response**:
```json
{
  "backtest_id": "uuid",
  "status": "running",
  "message": "Backtest started successfully",
  "estimated_completion": "2025-01-01T00:05:00Z"
}
```

### 3.2 Get Backtest Status

**Endpoint**: `GET /backtests/{backtest_id}`

**Response**:
```json
{
  "backtest_id": "uuid",
  "status": "completed",
  "progress": 100,
  "started_at": "2025-01-01T00:00:00Z",
  "completed_at": "2025-01-01T00:03:45Z",
  "results": {
    "total_return": 0.25,
    "annual_return": 0.06,
    "sharpe_ratio": 1.8,
    "sortino_ratio": 2.1,
    "max_drawdown": -0.12,
    "win_rate": 0.58,
    "total_trades": 150,
    "profitable_trades": 87,
    "avg_profit": 250.50,
    "avg_loss": -180.25
  }
}
```

### 3.3 Get Backtest Results

**Endpoint**: `GET /backtests/{backtest_id}/results`

**Response**:
```json
{
  "backtest_id": "uuid",
  "equity_curve": [
    {"date": "2020-01-01", "value": 100000},
    {"date": "2020-01-02", "value": 100500},
    ...
  ],
  "trades": [
    {
      "entry_date": "2020-01-15",
      "exit_date": "2020-01-20",
      "symbol": "AAPL",
      "side": "long",
      "entry_price": 150.00,
      "exit_price": 155.00,
      "quantity": 100,
      "pnl": 500.00,
      "return": 0.033
    }
  ],
  "metrics": {
    "total_return": 0.25,
    "sharpe_ratio": 1.8,
    "max_drawdown": -0.12,
    ...
  }
}
```

### 3.4 List Backtests

**Endpoint**: `GET /backtests`

**Query Parameters**:
- `strategy_id` (optional): Filter by strategy
- `status` (optional): Filter by status

**Response**:
```json
{
  "backtests": [
    {
      "backtest_id": "uuid",
      "strategy_id": "uuid",
      "strategy_name": "MA Crossover",
      "status": "completed",
      "total_return": 0.25,
      "sharpe_ratio": 1.8,
      "started_at": "2025-01-01T00:00:00Z",
      "completed_at": "2025-01-01T00:03:45Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

---

## 4. Live Trading API

### 4.1 Start Live Trading

**Endpoint**: `POST /live/start`

**Request**:
```json
{
  "strategy_id": "uuid",
  "mode": "paper",  // or "live"
  "config": {
    "broker": "zerodha",
    "symbols": ["AAPL", "GOOGL"],
    "capital": 100000,
    "risk_limits": {
      "max_position_size": 0.1,
      "max_daily_loss": 0.02,
      "max_drawdown": 0.15
    }
  }
}
```

**Response**:
```json
{
  "session_id": "uuid",
  "status": "running",
  "mode": "paper",
  "message": "Live trading started successfully"
}
```

### 4.2 Stop Live Trading

**Endpoint**: `POST /live/stop/{session_id}`

**Request**:
```json
{
  "close_positions": true  // Close all open positions
}
```

**Response**:
```json
{
  "session_id": "uuid",
  "status": "stopped",
  "message": "Live trading stopped successfully",
  "final_pnl": 1250.50
}
```

### 4.3 Get Live Trading Status

**Endpoint**: `GET /live/{session_id}`

**Response**:
```json
{
  "session_id": "uuid",
  "strategy_id": "uuid",
  "status": "running",
  "mode": "paper",
  "started_at": "2025-01-01T09:00:00Z",
  "current_pnl": 1250.50,
  "open_positions": 3,
  "total_trades": 15,
  "win_rate": 0.60
}
```

### 4.4 Get Open Positions

**Endpoint**: `GET /live/{session_id}/positions`

**Response**:
```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "side": "long",
      "quantity": 100,
      "entry_price": 150.00,
      "current_price": 155.00,
      "unrealized_pnl": 500.00,
      "entry_time": "2025-01-01T10:30:00Z"
    }
  ]
}
```

### 4.5 Emergency Stop

**Endpoint**: `POST /live/emergency-stop`

**Description**: Immediately stops all live trading sessions and closes all positions.

**Response**:
```json
{
  "message": "Emergency stop executed",
  "sessions_stopped": 3,
  "positions_closed": 8
}
```

---

## 5. Data API

### 5.1 Get Historical Data

**Endpoint**: `GET /data/historical`

**Query Parameters**:
- `symbol`: Stock symbol (required)
- `start_date`: Start date (required)
- `end_date`: End date (required)
- `interval`: Data interval (`1m`, `5m`, `1h`, `1d`, etc.)

**Response**:
```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "data": [
    {
      "timestamp": "2020-01-01T00:00:00Z",
      "open": 150.00,
      "high": 155.00,
      "low": 149.00,
      "close": 154.00,
      "volume": 1000000
    }
  ]
}
```

### 5.2 Get Real-time Quote

**Endpoint**: `GET /data/quote/{symbol}`

**Response**:
```json
{
  "symbol": "AAPL",
  "price": 155.50,
  "bid": 155.45,
  "ask": 155.55,
  "volume": 50000,
  "timestamp": "2025-01-01T10:30:00Z"
}
```

### 5.3 Search Symbols

**Endpoint**: `GET /data/search`

**Query Parameters**:
- `query`: Search query

**Response**:
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ",
      "type": "stock"
    }
  ]
}
```

---

## 6. Portfolio API

### 6.1 Get Portfolio Summary

**Endpoint**: `GET /portfolio`

**Response**:
```json
{
  "total_value": 125000.00,
  "cash": 25000.00,
  "positions_value": 100000.00,
  "total_pnl": 25000.00,
  "total_return": 0.25,
  "positions_count": 5
}
```

### 6.2 Get Portfolio Positions

**Endpoint**: `GET /portfolio/positions`

**Response**:
```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "avg_price": 150.00,
      "current_price": 155.00,
      "market_value": 15500.00,
      "unrealized_pnl": 500.00,
      "unrealized_pnl_pct": 0.033
    }
  ]
}
```

### 6.3 Get Trade History

**Endpoint**: `GET /portfolio/trades`

**Query Parameters**:
- `start_date` (optional)
- `end_date` (optional)
- `symbol` (optional)

**Response**:
```json
{
  "trades": [
    {
      "trade_id": "uuid",
      "timestamp": "2025-01-01T10:30:00Z",
      "symbol": "AAPL",
      "side": "buy",
      "quantity": 100,
      "price": 150.00,
      "commission": 1.50,
      "total": 15001.50
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

## 7. ML Models API

### 7.1 List Models

**Endpoint**: `GET /models`

**Response**:
```json
{
  "models": [
    {
      "model_id": "uuid",
      "name": "LSTM Price Predictor",
      "type": "lstm",
      "status": "trained",
      "accuracy": 0.75,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### 7.2 Train Model

**Endpoint**: `POST /models/train`

**Request**:
```json
{
  "name": "My LSTM Model",
  "type": "lstm",
  "config": {
    "input_dim": 10,
    "hidden_dim": 64,
    "output_dim": 1,
    "epochs": 100,
    "batch_size": 32
  },
  "training_data": {
    "symbols": ["AAPL", "GOOGL"],
    "start_date": "2020-01-01",
    "end_date": "2024-01-01",
    "features": ["close", "volume", "rsi", "macd"]
  }
}
```

**Response**:
```json
{
  "model_id": "uuid",
  "status": "training",
  "message": "Model training started"
}
```

### 7.3 Get Model Status

**Endpoint**: `GET /models/{model_id}`

**Response**:
```json
{
  "model_id": "uuid",
  "name": "My LSTM Model",
  "status": "trained",
  "progress": 100,
  "metrics": {
    "train_accuracy": 0.80,
    "val_accuracy": 0.75,
    "train_loss": 0.15,
    "val_loss": 0.20
  }
}
```

### 7.4 Make Prediction

**Endpoint**: `POST /models/{model_id}/predict`

**Request**:
```json
{
  "features": [
    [150.0, 1000000, 65.5, 0.5],
    [151.0, 1100000, 66.0, 0.6]
  ]
}
```

**Response**:
```json
{
  "predictions": [0.65, 0.68],
  "confidence": [0.85, 0.82]
}
```

---

## 8. WebSocket API

### 8.1 Connect to WebSocket

**URL**: `ws://localhost:8000/ws`

**Authentication**: Send token in first message

```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 8.2 Subscribe to Market Data

```json
{
  "type": "subscribe",
  "channel": "market_data",
  "symbols": ["AAPL", "GOOGL"]
}
```

**Server Response**:
```json
{
  "type": "market_data",
  "symbol": "AAPL",
  "price": 155.50,
  "volume": 1000,
  "timestamp": "2025-01-01T10:30:00Z"
}
```

### 8.3 Subscribe to Portfolio Updates

```json
{
  "type": "subscribe",
  "channel": "portfolio"
}
```

**Server Response**:
```json
{
  "type": "portfolio_update",
  "total_value": 125000.00,
  "pnl": 25000.00,
  "timestamp": "2025-01-01T10:30:00Z"
}
```

### 8.4 Subscribe to Trade Notifications

```json
{
  "type": "subscribe",
  "channel": "trades"
}
```

**Server Response**:
```json
{
  "type": "trade",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 100,
  "price": 150.00,
  "timestamp": "2025-01-01T10:30:00Z"
}
```

---

## 9. Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate name) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

**Error Response Format**:
```json
{
  "error": {
    "code": 400,
    "message": "Invalid request parameters",
    "details": {
      "field": "start_date",
      "reason": "Date format must be YYYY-MM-DD"
    }
  }
}
```

---

## 10. Rate Limits

| Endpoint | Rate Limit |
|----------|-----------|
| Authentication | 10 requests/minute |
| Market Data | 100 requests/minute |
| Trading | 50 requests/minute |
| Backtesting | 10 requests/hour |
| Other | 60 requests/minute |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

---

## 11. Pagination

All list endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Headers**:
```
X-Total-Count: 500
X-Page: 1
X-Page-Size: 20
X-Total-Pages: 25
```

---

## 12. Code Examples

### Python Example

```python
import requests

# Authentication
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# Create headers
headers = {"Authorization": f"Bearer {token}"}

# Run backtest
backtest_config = {
    "strategy_id": "uuid",
    "config": {
        "start_date": "2020-01-01",
        "end_date": "2024-01-01",
        "initial_capital": 100000
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/backtests",
    json=backtest_config,
    headers=headers
)

backtest_id = response.json()["backtest_id"]
print(f"Backtest started: {backtest_id}")
```

### JavaScript Example

```javascript
// Authentication
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'user', password: 'pass'})
});

const {access_token} = await response.json();

// Get strategies
const strategies = await fetch('http://localhost:8000/api/v1/strategies', {
  headers: {'Authorization': `Bearer ${access_token}`}
});

const data = await strategies.json();
console.log(data.strategies);
```

---

**API Version**: 1.0  
**Last Updated**: November 25, 2025  
**Support**: api-support@quantx.io
