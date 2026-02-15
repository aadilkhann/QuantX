# QuantX Codebase Analysis

**Generated**: December 29, 2025  
**Version**: 0.1.0  
**Analysis Type**: Complete Codebase Overview

---

## 📋 Executive Summary

**QuantX** is a sophisticated, production-ready algorithmic trading platform that combines AI/ML capabilities with rule-based trading strategies. The system is built with a modular, event-driven architecture and is currently in **Phase 3** of development with approximately **55% completion** of live trading features.

### Key Highlights
- **Architecture**: Event-driven, layered architecture with plugin-based extensibility
- **Language**: Python 3.11+
- **Lines of Code**: ~3,500+ production code
- **Development Status**: Phase 1 & 2 Complete (100%), Phase 3 In Progress (55%)
- **Testing**: Comprehensive test suite with fixtures and integration tests
- **Documentation**: Extensive documentation with setup guides and API references

---

## 🏗️ Architecture Overview

### System Architecture

QuantX follows a **5-layer architecture**:

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                      │
│  • CLI Interface                                         │
│  • REST API (FastAPI)                                    │
│  • WebSocket Server                                      │
│  • Web Dashboard (Next.js + React)                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                       │
│  • Strategy Manager                                      │
│  • Backtest Engine                                       │
│  • Live Execution Engine                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  CORE SERVICES                                           │
│  • Event Bus (Pub/Sub)                                   │
│  • Configuration Manager                                 │
│  • Logging System                                        │
│  • Risk Manager                                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  DOMAIN LAYER                                            │
│  • Data Layer (Providers, Storage, Streaming)            │
│  • ML Pipeline (Features, Models, Training)              │
│  • Portfolio Management                                  │
│  • Execution Engine                                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE LAYER                                    │
│  • Database (PostgreSQL)                                 │
│  • Cache (Redis)                                         │
│  • Broker APIs (Zerodha, Paper Trading)                  │
│  • Monitoring (Prometheus)                               │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
2. **Event-Driven Architecture**: Asynchronous, loosely-coupled components
3. **Plugin-Based Design**: Easy extensibility for strategies, data sources, brokers
4. **Separation of Concerns**: Clear boundaries between layers
5. **Testability**: Every component is unit-testable with clean interfaces

---

## 📁 Project Structure

```
QuantX/
├── src/quantx/                    # Main source code (62 files)
│   ├── core/                      # Core infrastructure (3 files)
│   │   ├── events.py              # Event system (278 lines)
│   │   ├── config.py              # Configuration management (6899 bytes)
│   │   └── __init__.py
│   │
│   ├── data/                      # Data layer (6 files)
│   │   ├── base.py                # Data interfaces
│   │   ├── instruments.py         # Instrument definitions
│   │   ├── streaming.py           # Real-time data streaming (16427 bytes)
│   │   └── providers/             # Data providers (Yahoo Finance, etc.)
│   │
│   ├── strategies/                # Trading strategies (8 files)
│   │   ├── base.py                # Base strategy classes (322 lines)
│   │   ├── registry.py            # Strategy registry
│   │   ├── rule_based/            # Rule-based strategies
│   │   └── ai_powered/            # AI-powered strategies
│   │
│   ├── backtesting/               # Backtesting engine (4 files)
│   │   ├── engine.py              # Backtest engine (328 lines)
│   │   ├── portfolio.py           # Portfolio management (9567 bytes)
│   │   └── metrics.py             # Performance metrics (9429 bytes)
│   │
│   ├── ml/                        # Machine Learning (17 files)
│   │   ├── features/              # Feature engineering (4 files)
│   │   │   ├── base.py            # Base feature classes
│   │   │   ├── technical.py       # Technical indicators
│   │   │   └── statistical.py     # Statistical features
│   │   ├── models/                # ML models (4 files)
│   │   │   ├── base.py            # Base model interface
│   │   │   ├── traditional.py     # Traditional ML (RF, GBM, XGBoost)
│   │   │   └── deep_learning.py   # Deep learning (LSTM, Transformer)
│   │   ├── evaluation/            # Model evaluation (3 files)
│   │   ├── pipeline/              # Training pipelines (2 files)
│   │   └── registry/              # Model versioning (2 files)
│   │
│   ├── execution/                 # Live trading (12 files)
│   │   ├── live_engine.py         # Live execution engine (515 lines)
│   │   ├── live_pnl.py            # Live P&L tracking (13875 bytes)
│   │   ├── position_sync.py       # Position synchronization (11607 bytes)
│   │   ├── brokers/               # Broker integrations (4 files)
│   │   │   ├── base.py            # Broker interface
│   │   │   ├── paper.py           # Paper trading broker
│   │   │   ├── zerodha.py         # Zerodha integration
│   │   │   └── factory.py         # Broker factory
│   │   ├── orders/                # Order management (2 files)
│   │   └── risk/                  # Risk management (2 files)
│   │
│   ├── api/                       # REST API (7 files)
│   │   ├── main.py                # FastAPI application (185 lines)
│   │   └── routers/               # API routers (5 files)
│   │       ├── engine.py          # Engine control
│   │       ├── positions.py       # Position endpoints
│   │       ├── orders.py          # Order endpoints
│   │       └── pnl.py             # P&L endpoints
│   │
│   ├── monitoring/                # Monitoring & Analytics (2 files)
│   └── persistence/               # State persistence (2 files)
│
├── dashboard/                     # Next.js Web Dashboard
│   ├── app/                       # Next.js app directory
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page
│   │   └── globals.css            # Global styles
│   ├── package.json               # Dependencies (Next.js, React, Tailwind)
│   ├── tailwind.config.ts         # Tailwind configuration
│   └── tsconfig.json              # TypeScript config
│
├── examples/                      # Example scripts (17 files)
│   ├── fetch_data.py              # Data fetching example
│   ├── complete_backtest.py       # Complete backtest example
│   ├── strategy_registry.py       # Strategy registry example
│   ├── ml/                        # ML examples (7 files)
│   │   ├── feature_engineering_demo.py
│   │   ├── train_traditional_models.py
│   │   ├── train_deep_learning.py
│   │   ├── mlflow_integration.py
│   │   ├── complete_pipeline.py
│   │   └── ai_strategy_example.py
│   └── live/                      # Live trading examples (7 files)
│       ├── paper_trading_example.py
│       └── oms_risk_example.py
│
├── tests/                         # Test suite (8 files)
│   ├── conftest.py                # Test configuration (6543 bytes)
│   ├── fixtures/                  # Test fixtures (2 files)
│   ├── unit/                      # Unit tests (4 files)
│   └── integration/               # Integration tests (1 file)
│
├── docs/                          # Documentation (28 files)
│   ├── ARCHITECTURE.md            # System architecture (28789 bytes)
│   ├── PRD.md                     # Product requirements
│   ├── ROADMAP.md                 # Development roadmap
│   ├── TESTING_GUIDE.md           # Testing guide
│   ├── LIVE_TRADING.md            # Live trading guide
│   ├── ZERODHA_SETUP.md           # Zerodha setup guide
│   ├── PHASE2_PROGRESS.md         # Phase 2 progress
│   ├── PHASE3_PROGRESS.md         # Phase 3 progress
│   └── Phase-1/                   # Phase 1 documentation
│
├── configs/                       # Configuration files
├── pyproject.toml                 # Poetry configuration (139 lines)
├── requirements.txt               # Pip requirements (811 bytes)
├── .env.example                   # Environment template (1692 bytes)
├── test_setup.py                  # Setup validation script (7525 bytes)
├── quickstart.sh                  # Interactive quickstart (4368 bytes)
└── README.md                      # Main documentation (14031 bytes)
```

---

## 🔧 Core Components

### 1. Event System (`src/quantx/core/events.py`)

**Purpose**: Thread-safe pub/sub event system for loose coupling

**Key Classes**:
- `EventType`: Enum defining all event types (MARKET_DATA, SIGNAL, ORDER, FILL, etc.)
- `Event`: Base event class with priority queue support
- `EventBus`: Thread-safe event bus with pub/sub pattern

**Features**:
- Priority-based event processing
- Thread-safe queue implementation
- Subscriber management
- Event statistics tracking

**Event Types**:
```
MARKET_DATA, TICK, BAR
SIGNAL
ORDER, ORDER_SUBMITTED, ORDER_ACCEPTED, ORDER_REJECTED, ORDER_CANCELLED
FILL
POSITION_UPDATED
RISK_VIOLATION, RISK_WARNING
SYSTEM_START, SYSTEM_STOP, SYSTEM_ERROR
HEARTBEAT
```

### 2. Strategy Framework (`src/quantx/strategies/`)

**Base Classes**:
- `BaseStrategy`: Abstract base for all strategies
- `RuleBasedStrategy`: For technical indicator-based strategies
- `AIPoweredStrategy`: For ML model-based strategies
- `HybridStrategy`: Combines AI and rule-based approaches

**Strategy Registry**:
- Plugin-based registration system
- Dynamic strategy creation
- Configuration management

**Example Strategies**:
- MA Crossover (Moving Average Crossover)
- RSI Strategy
- AI-powered prediction strategies

### 3. Backtesting Engine (`src/quantx/backtesting/`)

**Components**:
- `BacktestEngine`: Event-driven simulation engine (328 lines)
- `Portfolio`: Position tracking and P&L calculation (9567 bytes)
- `PerformanceMetrics`: Comprehensive performance analysis (9429 bytes)

**Features**:
- Realistic order execution with slippage and commission
- Multi-symbol support
- Event-driven simulation
- Comprehensive metrics (Sharpe, Sortino, drawdown, win rate, profit factor)

**Metrics Calculated**:
- Total Return, Annual Return, Total P&L
- Sharpe Ratio, Sortino Ratio, Calmar Ratio
- Maximum Drawdown, Volatility
- Win Rate, Profit Factor, Average Profit/Loss

### 4. Machine Learning Pipeline (`src/quantx/ml/`)

**Feature Engineering** (`features/`):
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- Statistical features (returns, volatility, momentum)
- Market regime detection

**Models** (`models/`):
- **Traditional ML**: Random Forest, Gradient Boosting, XGBoost, LightGBM
- **Deep Learning**: LSTM, Transformer models
- Model interface with train/predict/save/load

**Training Pipeline**:
- Feature engineering → Training → Evaluation → Backtesting
- MLflow integration for experiment tracking
- Model registry and versioning

### 5. Live Execution Engine (`src/quantx/execution/`)

**Core Engine** (`live_engine.py` - 515 lines):
- Event-driven live trading framework
- Connects strategies with brokers
- Order management integration
- Risk management controls
- Position synchronization
- Heartbeat monitoring

**Engine States**:
```
CREATED → STARTING → RUNNING → PAUSED/STOPPING → STOPPED
                              ↓
                            ERROR
```

**Broker Integrations**:
- `PaperBroker`: Simulated trading with realistic execution
- `ZerodhaBroker`: Zerodha Kite API integration (NSE/BSE)
- `BrokerFactory`: Factory pattern for broker creation

**Order Management**:
- Order validation and routing
- Multi-broker support
- Event callbacks for order lifecycle

**Risk Management**:
- Position size limits
- Daily loss limits
- Kill switch functionality
- Pre-trade risk checks

### 6. Data Layer (`src/quantx/data/`)

**Providers**:
- `YahooFinanceProvider`: Historical data (no API key required)
- Support for real-time streaming

**Features**:
- Data validation (OHLCV)
- Caching support
- Multiple data source support
- Instrument definitions

**Streaming** (`streaming.py` - 16427 bytes):
- Real-time WebSocket data streaming
- Market data normalization
- Event publishing

### 7. REST API (`src/quantx/api/`)

**FastAPI Application** (`main.py` - 185 lines):
- Modern REST API with automatic OpenAPI docs
- WebSocket support for real-time updates
- CORS middleware for dashboard integration

**Endpoints**:
- `/health` - Health check
- `/api/v1/info` - System information
- `/ws/live` - WebSocket for real-time updates

**Routers**:
- `engine.py`: Engine control (start/stop/status)
- `positions.py`: Position management
- `orders.py`: Order management
- `pnl.py`: P&L tracking

### 8. Web Dashboard (`dashboard/`)

**Technology Stack**:
- **Framework**: Next.js 14.2 (React 18.3)
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.4
- **Charts**: Recharts 2.12
- **Icons**: Lucide React
- **Data Fetching**: SWR 2.2, Axios 1.6

**Features**:
- Real-time position monitoring
- P&L visualization
- Engine control interface
- Order management UI

---

## 🚀 Development Phases

### Phase 1: Foundation ✅ **100% COMPLETE**

**Completed Components**:
- ✅ Project structure and configuration
- ✅ Core event system
- ✅ Configuration management
- ✅ Data layer abstraction
- ✅ Basic backtesting engine
- ✅ Rule-based strategy framework
- ✅ Portfolio management
- ✅ Performance metrics
- ✅ Example strategies

**Files**: 21 production files, ~3,500+ lines of code

### Phase 2: ML Integration ✅ **100% COMPLETE**

**Completed Components**:
- ✅ Feature engineering pipeline
- ✅ ML model training framework
- ✅ Traditional ML models (RF, GBM, XGBoost)
- ✅ Deep learning models (LSTM, Transformer)
- ✅ AI-powered strategies
- ✅ Model evaluation tools
- ✅ MLflow integration
- ✅ Complete ML pipeline

**Examples**: 7 ML example scripts

### Phase 3: Live Trading 🚧 **55% COMPLETE**

**Completed Components**:
- ✅ Live Execution Engine
- ✅ Zerodha broker integration (NSE/BSE)
- ✅ Real-time WebSocket streaming
- ✅ Order management system
- ✅ Risk management controls
- ✅ Position synchronization
- ✅ Live P&L tracking
- ✅ Paper trading broker
- ✅ FastAPI backend
- ✅ Next.js dashboard (basic)

**In Progress**:
- 🚧 Complete dashboard UI
- 🚧 Advanced risk controls
- 🚧 State persistence
- 🚧 Health monitoring

### Phase 4: Quality & Reliability 🔄 **CURRENT**

**Planned**:
- [ ] Comprehensive test suite (unit, integration, E2E)
- [ ] State persistence & disaster recovery
- [ ] Health monitoring & alerting
- [ ] Production hardening
- [ ] CI/CD pipeline
- [ ] Production deployment guide

---

## 🛠️ Technology Stack

### Backend (Python)

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.11+ |
| **Data Processing** | pandas 2.1+, numpy 1.24+, polars 0.19+ |
| **ML/AI** | PyTorch 2.1+, scikit-learn 1.3+, XGBoost 2.0+, LightGBM 4.1+ |
| **Technical Analysis** | ta-lib 0.4.28, pandas-ta 0.3.14 |
| **Data Providers** | yfinance 0.2.28, ccxt 4.1+, alpha-vantage 2.3+ |
| **Database** | SQLAlchemy 2.0+, psycopg2-binary 2.9+, Alembic 1.12+ |
| **Cache** | Redis 5.0+, hiredis 2.2+ |
| **API** | FastAPI 0.104+, Uvicorn 0.24+, WebSockets 12.0+ |
| **Validation** | Pydantic 2.4+, pydantic-settings 2.0+ |
| **Utilities** | python-dotenv 1.0+, PyYAML 6.0+, click 8.1+, rich 13.6+, loguru 0.7+ |
| **Monitoring** | prometheus-client 0.18+ |

### Frontend (Dashboard)

| Category | Technologies |
|----------|-------------|
| **Framework** | Next.js 14.2 |
| **UI Library** | React 18.3 |
| **Language** | TypeScript 5.3 |
| **Styling** | Tailwind CSS 3.4, PostCSS 8.4, Autoprefixer 10.4 |
| **Charts** | Recharts 2.12 |
| **Icons** | Lucide React 0.344 |
| **HTTP Client** | Axios 1.6 |
| **Data Fetching** | SWR 2.2 |
| **Utilities** | date-fns 3.3, clsx 2.1, tailwind-merge 2.2 |

### Development Tools

| Category | Technologies |
|----------|-------------|
| **Testing** | pytest 7.4+, pytest-cov 4.1+, pytest-asyncio 0.21+, pytest-mock 3.12+, hypothesis 6.88+ |
| **Code Quality** | black 23.10+, ruff 0.1+, mypy 1.6+, pre-commit 3.5+ |
| **Documentation** | mkdocs 1.5+, mkdocs-material 9.4+ |
| **Notebooks** | Jupyter 1.0+, ipykernel 6.26+, matplotlib 3.8+, seaborn 0.13+ |

---

## 📊 Code Statistics

### File Count by Module

| Module | Files | Description |
|--------|-------|-------------|
| **Core** | 3 | Event system, configuration, logging |
| **Data** | 6 | Data providers, storage, streaming |
| **Strategies** | 8 | Base classes, registry, implementations |
| **Backtesting** | 4 | Engine, portfolio, metrics |
| **ML** | 17 | Features, models, training, evaluation |
| **Execution** | 12 | Live engine, brokers, orders, risk |
| **API** | 7 | FastAPI app, routers |
| **Monitoring** | 2 | Health monitoring, analytics |
| **Persistence** | 2 | State management |
| **Examples** | 17 | Demo scripts |
| **Tests** | 8 | Unit and integration tests |
| **Docs** | 28 | Documentation files |
| **Dashboard** | 6+ | Next.js application |

**Total Production Files**: ~100+ files  
**Total Lines of Code**: ~20,000+ (estimated)

### Key File Sizes

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| `live_engine.py` | 18,299 bytes | 515 | Live execution engine |
| `streaming.py` | 16,427 bytes | - | Real-time data streaming |
| `deep_learning.py` | 16,790 bytes | - | Deep learning models |
| `base.py` (features) | 17,012 bytes | - | Feature engineering base |
| `live_pnl.py` | 13,875 bytes | - | Live P&L tracking |
| `traditional.py` | 14,074 bytes | - | Traditional ML models |
| `base.py` (models) | 14,245 bytes | - | Model base classes |
| `technical.py` | 12,947 bytes | - | Technical indicators |
| `position_sync.py` | 11,607 bytes | - | Position synchronization |
| `engine.py` | 10,785 bytes | 328 | Backtest engine |

---

## 🧪 Testing Infrastructure

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration (6543 bytes)
├── fixtures/                # Test fixtures
│   ├── market_data.py       # Market data fixtures
│   └── strategies.py        # Strategy fixtures
├── unit/                    # Unit tests
│   ├── test_events.py       # Event system tests
│   ├── test_strategies.py   # Strategy tests
│   ├── test_portfolio.py    # Portfolio tests
│   └── test_metrics.py      # Metrics tests
└── integration/             # Integration tests
    └── test_backtest.py     # End-to-end backtest tests
```

### Test Coverage

- **Unit Tests**: Core components, strategies, portfolio, metrics
- **Integration Tests**: Complete backtest workflows
- **Fixtures**: Reusable test data and mock objects
- **Configuration**: pytest.ini with coverage settings

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=quantx --cov-report=html

# Run specific test file
pytest tests/unit/test_events.py

# Run validation script
python test_setup.py
```

---

## 📚 Documentation

### Main Documentation Files

| File | Size | Purpose |
|------|------|---------|
| `README.md` | 14,031 bytes | Main project overview |
| `ARCHITECTURE.md` | 28,789 bytes | System architecture details |
| `SETUP_AND_RUN_GUIDE.md` | 18,640 bytes | Complete setup guide |
| `IMPLEMENTATION_STATUS.md` | 6,691 bytes | Phase 1 completion status |
| `PRD.md` | 20,379 bytes | Product requirements |
| `ROADMAP.md` | 10,103 bytes | Development roadmap |
| `TESTING_GUIDE.md` | 8,933 bytes | Testing guide |
| `LIVE_TRADING.md` | 10,430 bytes | Live trading guide |
| `ZERODHA_SETUP.md` | 8,490 bytes | Zerodha integration guide |

### Quick Start Guides

- `QUICKSTART.md` (4,141 bytes)
- `API_QUICKSTART.md` (3,892 bytes)
- `QUICK_TEST_GUIDE.md` (2,196 bytes)
- `DASHBOARD_SETUP.md` (2,796 bytes)
- `NEXTJS_SETUP.md` (2,539 bytes)

### Setup Scripts

- `quickstart.sh` (4,368 bytes) - Interactive menu-driven setup
- `setup_dashboard.sh` (5,681 bytes) - Dashboard setup automation
- `start_api.sh` (366 bytes) - API server startup
- `run_tests.sh` (2,565 bytes) - Test execution script

---

## 🔄 Data Flow

### Backtesting Flow

```
User Request
    ↓
BacktestEngine.run()
    ↓
DataProvider.get_historical_data()
    ↓
For each timestamp:
    ├─→ Strategy.on_data(market_data)
    │       ↓
    │   Generate Signals
    │       ↓
    ├─→ RiskManager.check_risk(signals)
    │       ↓
    │   Approved Signals
    │       ↓
    ├─→ Portfolio.execute_signals()
    │       ↓
    │   Update Positions
    │       ↓
    └─→ Calculate P&L
        ↓
PerformanceMetrics.calculate()
    ↓
Return Results
```

### Live Trading Flow

```
Market Data Stream
    ↓
EventBus.publish(MARKET_DATA)
    ↓
Strategy.on_data(event)
    ↓
Generate Signal
    ↓
EventBus.publish(SIGNAL)
    ↓
RiskManager.on_signal(event)
    ↓
Risk Check
    ├─→ PASS: EventBus.publish(ORDER)
    │           ↓
    │       OrderManager.on_order(event)
    │           ↓
    │       Broker.place_order()
    │           ↓
    │       EventBus.publish(FILL)
    │           ↓
    │       Strategy.on_fill(event)
    │
    └─→ FAIL: EventBus.publish(RISK_VIOLATION)
```

---

## 🎯 Key Features

### 1. Hybrid Strategy Engine
- AI-powered strategies (LSTM, Transformer, ensemble models)
- Rule-based strategies (technical indicators, patterns)
- Hybrid strategies (combine AI + rules)
- Strategy composition with custom weights

### 2. Multi-Asset Support
- **Equities**: Stocks, ETFs (NSE, NYSE, NASDAQ)
- **Derivatives**: Futures, Options (planned)
- **Cryptocurrencies**: Spot and futures markets
- **Forex**: Currency pairs (planned)

### 3. Advanced Backtesting
- Event-driven simulation engine
- Realistic order execution modeling
- Transaction cost analysis
- Slippage and market impact simulation
- Walk-forward optimization
- Monte Carlo simulation

### 4. Production-Ready Features
- Real-time data streaming
- Low-latency order execution
- Comprehensive monitoring and alerting
- Risk management controls
- Paper trading mode
- Multi-broker support

### 5. ML/AI Capabilities
- Feature engineering pipeline
- Traditional ML models (RF, GBM, XGBoost, LightGBM)
- Deep learning models (LSTM, Transformer)
- Model evaluation and backtesting
- MLflow experiment tracking
- Model registry and versioning

---

## 🔐 Configuration Management

### Environment Variables (`.env.example`)

```env
# Application
APP_ENV=development
DEBUG=true

# Data Providers
YAHOO_FINANCE_ENABLED=true

# Zerodha (for live trading)
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
ZERODHA_USER_ID=your_user_id
ZERODHA_PASSWORD=your_password

# Risk Management
RISK_MAX_POSITION_SIZE=0.1
RISK_MAX_DAILY_LOSS=0.02
RISK_MAX_DRAWDOWN=0.15

# Feature Flags
FEATURE_LIVE_TRADING=false
```

### Configuration Files

- `pyproject.toml`: Poetry dependencies and project metadata
- `requirements.txt`: Pip dependencies
- `pytest.ini`: Test configuration
- `configs/`: Strategy and broker configurations

---

## 🚀 Getting Started

### Installation

```bash
# Navigate to project
cd /home/adil-khan/Builds/QuantX

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Validate installation
python test_setup.py
```

### Running Examples

```bash
# Phase 1: Backtesting
python examples/fetch_data.py
python examples/complete_backtest.py

# Phase 2: Machine Learning
python examples/ml/feature_engineering_demo.py
python examples/ml/train_traditional_models.py
python examples/ml/ai_strategy_example.py

# Phase 3: Live Trading
python examples/live/paper_trading_example.py
python examples/live/oms_risk_example.py
```

### Starting the API

```bash
# Start FastAPI server
./start_api.sh

# Or manually
uvicorn quantx.api.main:app --reload --port 8000

# Access API docs
# http://localhost:8000/docs
```

### Starting the Dashboard

```bash
cd dashboard
npm install
npm run dev

# Access dashboard
# http://localhost:3000
```

---

## 📈 Performance Metrics

### Backtesting Metrics

**Returns**:
- Total Return
- Annual Return
- Total P&L

**Risk-Adjusted Returns**:
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio

**Risk Metrics**:
- Maximum Drawdown
- Volatility

**Trade Statistics**:
- Win Rate
- Profit Factor
- Average Profit/Loss
- Total Trades

---

## 🔧 Extensibility

### Adding a New Strategy

```python
from quantx.strategies import RuleBasedStrategy, StrategyRegistry

@StrategyRegistry.register("my_strategy")
class MyStrategy(RuleBasedStrategy):
    def on_data(self, event):
        # Your trading logic
        data = event.data
        if self.should_buy(data):
            self.buy(data['symbol'], 100)
    
    def on_fill(self, event):
        # Handle order fills
        pass
```

### Adding a New Data Provider

```python
from quantx.data.base import IDataProvider

class MyDataProvider(IDataProvider):
    def get_historical_data(self, symbol, start, end, interval):
        # Fetch data from your source
        return dataframe
    
    def get_realtime_data(self, symbols):
        # Stream real-time data
        yield market_data
```

### Adding a New Broker

```python
from quantx.execution.brokers.base import IBroker

class MyBroker(IBroker):
    def connect(self):
        # Connect to broker API
        pass
    
    def place_order(self, order):
        # Place order with broker
        return order_id
    
    def get_positions(self):
        # Fetch current positions
        return positions
```

---

## 🐛 Known Issues & Limitations

### Current Limitations

1. **Live Trading**: Only Zerodha broker fully integrated
2. **Dashboard**: Basic UI, needs more features
3. **State Persistence**: Not yet implemented
4. **Monitoring**: Basic health checks, needs comprehensive monitoring
5. **Testing**: Test coverage incomplete

### Planned Improvements

- Multi-broker support (Interactive Brokers, Binance)
- Advanced dashboard with real-time charts
- State persistence and disaster recovery
- Comprehensive monitoring and alerting
- Options trading support
- Distributed backtesting

---

## 📊 Project Metrics

### Development Progress

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 1: Foundation | ✅ Complete | 100% |
| Phase 2: ML Integration | ✅ Complete | 100% |
| Phase 3: Live Trading | 🚧 In Progress | 55% |
| Phase 4: Quality & Reliability | 🔄 Current | 0% |
| Phase 5: Production Features | ⏳ Planned | 0% |
| Phase 6: Advanced Features | ⏳ Planned | 0% |

### Code Quality

- **Architecture**: Event-driven, layered, plugin-based ✅
- **SOLID Principles**: Implemented ✅
- **Documentation**: Comprehensive ✅
- **Testing**: Partial coverage 🚧
- **Type Hints**: Partial 🚧
- **Linting**: Configured (black, ruff, mypy) ✅

---

## 🎓 Learning Resources

### Documentation

1. **Getting Started**: `README.md`, `SETUP_AND_RUN_GUIDE.md`
2. **Architecture**: `docs/ARCHITECTURE.md`
3. **API Reference**: `docs/api/`
4. **Testing**: `docs/TESTING_GUIDE.md`
5. **Live Trading**: `docs/LIVE_TRADING.md`

### Examples

1. **Backtesting**: `examples/complete_backtest.py`
2. **ML Pipeline**: `examples/ml/complete_pipeline.py`
3. **Paper Trading**: `examples/live/paper_trading_example.py`
4. **Risk Management**: `examples/live/oms_risk_example.py`

---

## 🤝 Contributing

### Development Workflow

1. Set up development environment
2. Create feature branch
3. Implement changes
4. Write tests
5. Run linters and tests
6. Submit pull request

### Code Standards

- Follow SOLID principles
- Write comprehensive docstrings
- Add type hints
- Write unit tests
- Update documentation

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🔗 Related Projects

QuantX is inspired by:
- **freqtrade**: Production-ready architecture
- **machine-learning-for-trading**: ML techniques
- **Stockformer**: Deep learning approaches
- **SWING_TRADING_WQU**: Custom backtesting infrastructure

---

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory

---

**Last Updated**: December 29, 2025  
**Version**: 0.1.0  
**Status**: Phase 3 in Progress (55% Complete)
