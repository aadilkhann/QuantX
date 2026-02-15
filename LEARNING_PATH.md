# QuantX Learning Path: Understanding the Full Source Code & Architecture

**Created**: February 2, 2026  
**Purpose**: Step-by-step guide to understand the entire QuantX codebase  
**Difficulty**: Beginner → Intermediate → Advanced

---

## 📚 Table of Contents

1. [Learning Strategy](#learning-strategy)
2. [Phase 1: Core Foundations (Start Here)](#phase-1-core-foundations-start-here)
3. [Phase 2: Data & Strategy Layer](#phase-2-data--strategy-layer)
4. [Phase 3: Backtesting Engine](#phase-3-backtesting-engine)
5. [Phase 4: Machine Learning Pipeline](#phase-4-machine-learning-pipeline)
6. [Phase 5: Live Trading System](#phase-5-live-trading-system)
7. [Phase 6: API & Dashboard](#phase-6-api--dashboard)
8. [Hands-On Exercises](#hands-on-exercises)
9. [Deep Dive Topics](#deep-dive-topics)

---

## 🎯 Learning Strategy

### Recommended Approach

1. **Read Documentation First** (30 minutes)
2. **Understand Core Architecture** (1 hour)
3. **Study Code Layer by Layer** (4-6 hours)
4. **Run Examples** (1-2 hours)
5. **Experiment & Modify** (ongoing)

### Prerequisites

- Python fundamentals (classes, decorators, async/await)
- Basic understanding of trading concepts (orders, positions, P&L)
- Familiarity with pandas and numpy
- Basic knowledge of event-driven architecture

---

## 📖 Phase 1: Core Foundations (START HERE)

### Step 1.1: Read High-Level Documentation (30 min)

**Order of Reading**:

1. **`README.md`** - Project overview, features, quick start
   - Understand the vision and key features
   - Note the project structure
   - Review the roadmap

2. **`CODEBASE_ANALYSIS.md`** - Complete codebase overview
   - Understand the 5-layer architecture
   - Review component responsibilities
   - Note file organization

3. **`docs/ARCHITECTURE.md`** (first 200 lines)
   - Deep dive into architectural decisions
   - Understand design principles (SOLID)
   - Study the component diagram

**Key Concepts to Grasp**:
- Event-driven architecture
- Layered design pattern
- Plugin-based extensibility
- Separation of concerns

---

### Step 1.2: Core Event System (1 hour)

**File**: `src/quantx/core/events.py` (278 lines)

**Study Order**:

1. **Read the EventType enum** (lines 17-52)
   ```python
   class EventType(Enum):
       MARKET_DATA = "market_data"
       SIGNAL = "signal"
       ORDER = "order"
       FILL = "fill"
       # ... etc
   ```
   - Understand all event types in the system
   - Note how events flow through the system

2. **Study the Event class** (lines 55-87)
   ```python
   @dataclass
   class Event:
       priority: int
       event_type: EventType
       timestamp: datetime
       data: Any
       source: str
   ```
   - Understand event structure
   - Note the priority-based processing
   - See how events are converted to dictionaries

3. **Analyze the EventBus class** (lines 90-277)
   - **subscribe()** - How components register for events
   - **publish()** - How events are published
   - **start()/stop()** - Thread management
   - **_process_events()** - Event processing loop
   - **_dispatch_event()** - Event routing to subscribers

**Key Concepts**:
- Publisher-Subscriber pattern
- Priority queue for event ordering
- Thread-safe event processing
- Loose coupling between components

**Hands-On Exercise**:
```bash
# Create a simple test to understand events
cd /home/adil-khan/Builds/QuantX
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from quantx.core.events import EventBus, Event, EventType
from datetime import datetime

# Create event bus
bus = EventBus()

# Subscribe to events
def on_market_data(event):
    print(f"Received market data: {event.data}")

bus.subscribe(EventType.MARKET_DATA, on_market_data)

# Start processing
bus.start()

# Publish event
event = Event(
    priority=1,
    event_type=EventType.MARKET_DATA,
    timestamp=datetime.now(),
    data={"symbol": "AAPL", "price": 150.0},
    source="test"
)
bus.publish(event)

# Wait and stop
import time
time.sleep(1)
bus.stop()
EOF
```

---

### Step 1.3: Configuration System (30 min)

**File**: `src/quantx/core/config.py` (6,899 bytes)

**Study Order**:

1. **Understand Pydantic Settings** (top of file)
   - Type-safe configuration
   - Environment variable loading
   - Validation

2. **Review Config class structure**
   - Application settings
   - Data provider settings
   - Risk management settings
   - Feature flags

**Key Concepts**:
- Type-safe configuration with Pydantic
- Environment variable management
- Configuration validation

---

## 📊 Phase 2: Data & Strategy Layer

### Step 2.1: Data Layer Architecture (1 hour)

**Files to Study**:

1. **`src/quantx/data/base.py`** (5,392 bytes)
   
   **Study Order**:
   - **MarketData dataclass** - How market data is structured
   - **IDataProvider interface** - Abstract interface for data sources
   - **IDataStore interface** - Abstract interface for data storage
   
   **Key Concepts**:
   - Interface segregation (different interfaces for different purposes)
   - Dependency inversion (depend on abstractions)

2. **`src/quantx/data/providers/yahoo.py`**
   
   **Study Order**:
   - **YahooFinanceProvider class** - Concrete implementation
   - **get_historical_data()** - How data is fetched
   - **Caching mechanism** - How data is cached
   
   **Key Concepts**:
   - Concrete implementation of abstract interface
   - Error handling and retries
   - Data validation

3. **`src/quantx/data/instruments.py`** (6,573 bytes)
   
   **Study Order**:
   - **Instrument class** - How instruments are defined
   - **InstrumentType enum** - Different asset types
   
4. **`src/quantx/data/streaming.py`** (16,427 bytes)
   
   **Study Order**:
   - **MarketDataStream class** - Real-time data streaming
   - **WebSocket handling** - How real-time data is received
   - **Event publishing** - How data is converted to events

**Hands-On Exercise**:
```bash
# Test data fetching
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/fetch_data.py
```

---

### Step 2.2: Strategy Framework (1.5 hours)

**File**: `src/quantx/strategies/base.py` (322 lines, 8,693 bytes)

**Study Order**:

1. **Action and Signal classes** (lines 19-54)
   ```python
   class Action(Enum):
       BUY = "buy"
       SELL = "sell"
       HOLD = "hold"
   
   @dataclass
   class Signal:
       symbol: str
       action: Action
       quantity: int
       price: Optional[float]
   ```
   - How trading signals are represented
   - Signal to event conversion

2. **BaseStrategy class** (lines 57-218)
   
   **Key Methods**:
   - `__init__()` - Strategy initialization
   - `set_event_bus()` - Connect to event system
   - `on_data()` - **ABSTRACT** - Called on market data (YOU IMPLEMENT THIS)
   - `on_fill()` - **ABSTRACT** - Called on order fill (YOU IMPLEMENT THIS)
   - `buy()` - Generate buy signal
   - `sell()` - Generate sell signal
   - `has_position()` - Check if has position
   - `get_position()` - Get current position
   
   **Key Concepts**:
   - Template Method pattern
   - Abstract base class
   - Event-driven callbacks

3. **RuleBasedStrategy class** (lines 221-238)
   - Base for technical indicator strategies
   - Inherits from BaseStrategy

4. **AIPoweredStrategy class** (lines 241-283)
   - Base for ML model strategies
   - `set_model()` - Set ML model
   - `prepare_features()` - **ABSTRACT** - Feature preparation
   
5. **HybridStrategy class** (lines 286-322)
   - Combines AI and rule-based approaches
   - `combine_signals()` - **ABSTRACT** - Signal combination logic

**Study a Real Strategy**:

**File**: `src/quantx/strategies/rule_based/ma_crossover.py`

```python
@StrategyRegistry.register("ma_crossover")
class MACrossoverStrategy(RuleBasedStrategy):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.fast_period = config.get("fast_period", 50)
        self.slow_period = config.get("slow_period", 200)
        self.position = 0
    
    def on_data(self, event: Event):
        # Calculate moving averages
        # Generate buy/sell signals
        # Publish signals via self.buy() or self.sell()
    
    def on_fill(self, event: Event):
        # Update internal position tracking
```

**Key Concepts**:
- Strategy pattern
- Decorator pattern (for registration)
- Event-driven signal generation

**Hands-On Exercise**:
```bash
# Test strategy registry
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/strategy_registry.py
```

---

### Step 2.3: Strategy Registry (30 min)

**File**: `src/quantx/strategies/registry.py` (2,735 bytes)

**Study Order**:

1. **StrategyRegistry class**
   - `register()` - Decorator to register strategies
   - `create()` - Factory method to create strategy instances
   - `list_strategies()` - List all registered strategies

**Key Concepts**:
- Registry pattern
- Factory pattern
- Decorator pattern for registration

---

## 🔄 Phase 3: Backtesting Engine

### Step 3.1: Portfolio Management (1 hour)

**File**: `src/quantx/backtesting/portfolio.py` (9,567 bytes)

**Study Order**:

1. **Position class**
   - Track individual position (quantity, entry price, P&L)
   - `update()` - Update position on trade
   - `get_pnl()` - Calculate unrealized P&L

2. **Portfolio class**
   
   **Key Methods**:
   - `__init__()` - Initialize with capital
   - `update_position()` - Update position after trade
   - `get_position()` - Get current position
   - `get_total_value()` - Calculate total portfolio value
   - `get_cash()` - Get available cash
   - `get_equity_curve()` - Get historical equity values
   - `calculate_pnl()` - Calculate realized and unrealized P&L
   
   **Key Concepts**:
   - Position tracking
   - Cash management
   - P&L calculation (realized vs unrealized)
   - Equity curve tracking

**Hands-On Exercise**:
```python
# Test portfolio manually
from quantx.backtesting.portfolio import Portfolio

portfolio = Portfolio(initial_capital=100000)
print(f"Initial cash: ${portfolio.cash:,.2f}")

# Simulate a buy
portfolio.update_position("AAPL", 100, 150.0)
print(f"After buying 100 AAPL @ $150:")
print(f"  Cash: ${portfolio.cash:,.2f}")
print(f"  Position: {portfolio.get_position('AAPL')}")

# Calculate value with current price
current_prices = {"AAPL": 155.0}
total_value = portfolio.get_total_value(current_prices)
pnl = portfolio.calculate_pnl(current_prices)
print(f"  Total Value: ${total_value:,.2f}")
print(f"  P&L: ${pnl:,.2f}")
```

---

### Step 3.2: Performance Metrics (45 min)

**File**: `src/quantx/backtesting/metrics.py` (9,429 bytes)

**Study Order**:

1. **PerformanceMetrics class**
   
   **Key Methods**:
   - `calculate_returns()` - Total and annual returns
   - `calculate_sharpe_ratio()` - Risk-adjusted return
   - `calculate_sortino_ratio()` - Downside risk-adjusted return
   - `calculate_max_drawdown()` - Maximum peak-to-trough decline
   - `calculate_win_rate()` - Percentage of winning trades
   - `calculate_profit_factor()` - Gross profit / gross loss
   - `get_all_metrics()` - Calculate all metrics at once

**Key Concepts**:
- Risk-adjusted returns (Sharpe, Sortino)
- Drawdown analysis
- Trade statistics
- Performance measurement

---

### Step 3.3: Backtest Engine (1.5 hours)

**File**: `src/quantx/backtesting/engine.py` (328 lines, 10,785 bytes)

**Study Order**:

1. **BacktestEngine class initialization** (lines 28-71)
   ```python
   def __init__(
       self,
       strategy: BaseStrategy,
       data_provider: IDataProvider,
       initial_capital: float = 100000.0,
       commission_rate: float = 0.001,
       slippage_rate: float = 0.0005,
   ):
   ```
   - Understand dependencies (strategy, data provider)
   - Note commission and slippage modeling

2. **run() method** (lines 73-183) - **MOST IMPORTANT**
   
   **Flow**:
   ```
   1. Fetch historical data for all symbols
   2. Align data to common timestamps
   3. Initialize portfolio and event bus
   4. Subscribe to signal events
   5. For each timestamp:
      a. Create market data event
      b. Publish to strategy
      c. Strategy generates signals
      d. Execute approved signals
      e. Update portfolio
   6. Calculate performance metrics
   7. Return results
   ```
   
   **Key Concepts**:
   - Event-driven simulation
   - Time-based iteration
   - Signal to order conversion
   - Realistic execution (commission + slippage)

3. **_align_data() method** (lines 185-214)
   - How multi-symbol data is aligned
   - Handling missing data

4. **_on_signal() method** (lines 216-266)
   - Signal event handler
   - Order execution simulation
   - Portfolio updates
   - Fill event generation

5. **_calculate_results() method** (lines 268-303)
   - Metrics calculation
   - Results packaging

**Complete Flow Diagram**:
```
User calls engine.run()
    ↓
Fetch historical data
    ↓
Align data to common timestamps
    ↓
Initialize portfolio, event bus
    ↓
Subscribe to SIGNAL events
    ↓
FOR EACH TIMESTAMP:
    ├─→ Create MARKET_DATA event
    ├─→ Publish to event bus
    ├─→ Strategy.on_data() receives event
    ├─→ Strategy generates signals (buy/sell)
    ├─→ Signals published as SIGNAL events
    ├─→ BacktestEngine._on_signal() receives
    ├─→ Execute order (with commission/slippage)
    ├─→ Update portfolio
    ├─→ Create FILL event
    └─→ Strategy.on_fill() receives event
    ↓
Calculate performance metrics
    ↓
Return results
```

**Hands-On Exercise**:
```bash
# Run complete backtest
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/complete_backtest.py
```

**Study the Output**:
- Understand each metric
- Look at the equity curve
- Analyze trade statistics

---

## 🤖 Phase 4: Machine Learning Pipeline

### Step 4.1: Feature Engineering (1.5 hours)

**Files to Study**:

1. **`src/quantx/ml/features/base.py`** (17,012 bytes)
   
   **Study Order**:
   - **IFeatureEngineer interface** - Abstract feature engineering
   - **FeatureEngineer class** - Main feature engineering pipeline
   - **create_features()** - Feature creation workflow
   - **Feature validation** - Data quality checks
   
2. **`src/quantx/ml/features/technical.py`** (12,947 bytes)
   
   **Study Order**:
   - **TechnicalFeatures class** - Technical indicator features
   - **calculate_sma()** - Simple Moving Average
   - **calculate_ema()** - Exponential Moving Average
   - **calculate_rsi()** - Relative Strength Index
   - **calculate_macd()** - MACD indicator
   - **calculate_bollinger_bands()** - Bollinger Bands
   
3. **`src/quantx/ml/features/statistical.py`** (7,036 bytes)
   
   **Study Order**:
   - **StatisticalFeatures class** - Statistical features
   - **calculate_returns()** - Price returns
   - **calculate_volatility()** - Rolling volatility
   - **calculate_momentum()** - Price momentum

**Key Concepts**:
- Feature engineering pipeline
- Technical indicators
- Statistical features
- Feature validation

**Hands-On Exercise**:
```bash
# Test feature engineering
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/ml/feature_engineering_demo.py
```

---

### Step 4.2: ML Models (2 hours)

**Files to Study**:

1. **`src/quantx/ml/models/base.py`** (14,245 bytes)
   
   **Study Order**:
   - **IModel interface** - Abstract model interface
   - **train()** - Training method
   - **predict()** - Prediction method
   - **save()/load()** - Model persistence
   
2. **`src/quantx/ml/models/traditional.py`** (14,074 bytes)
   
   **Study Order**:
   - **RandomForestModel** - Random Forest implementation
   - **GradientBoostingModel** - Gradient Boosting
   - **XGBoostModel** - XGBoost implementation
   - **LightGBMModel** - LightGBM implementation
   
   **Key Concepts**:
   - Ensemble methods
   - Hyperparameter tuning
   - Cross-validation
   - Model evaluation

3. **`src/quantx/ml/models/deep_learning.py`** (16,790 bytes)
   
   **Study Order**:
   - **LSTMModel** - LSTM for time series
   - **TransformerModel** - Transformer architecture
   - **Training loop** - PyTorch training
   - **GPU support** - CUDA handling
   
   **Key Concepts**:
   - Deep learning for time series
   - LSTM architecture
   - Transformer architecture
   - PyTorch implementation

**Hands-On Exercise**:
```bash
# Train traditional ML models
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/ml/train_traditional_models.py

# Train deep learning models (takes longer)
PYTHONPATH="$(pwd)/src" python examples/ml/train_deep_learning.py
```

---

### Step 4.3: ML Pipeline Integration (1 hour)

**Study Order**:

1. **`src/quantx/ml/pipeline/`** - Training pipelines
2. **`src/quantx/ml/evaluation/`** - Model evaluation
3. **`src/quantx/ml/registry/`** - Model versioning

**Hands-On Exercise**:
```bash
# Complete ML pipeline
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/ml/complete_pipeline.py

# MLflow integration
PYTHONPATH="$(pwd)/src" python examples/ml/mlflow_integration.py

# View MLflow UI
mlflow ui
# Open http://localhost:5000
```

---

## 🚀 Phase 5: Live Trading System

### Step 5.1: Broker Interface (1 hour)

**File**: `src/quantx/execution/brokers/base.py`

**Study Order**:

1. **Order class** - Order representation
   ```python
   @dataclass
   class Order:
       symbol: str
       order_type: OrderType
       side: OrderSide
       quantity: int
       price: Optional[float]
       status: OrderStatus
   ```

2. **IBroker interface** - Abstract broker interface
   ```python
   class IBroker(ABC):
       @abstractmethod
       def connect(self) -> bool
       
       @abstractmethod
       def place_order(self, order: Order) -> str
       
       @abstractmethod
       def cancel_order(self, order_id: str) -> bool
       
       @abstractmethod
       def get_positions(self) -> List[Position]
       
       @abstractmethod
       def get_account_info(self) -> Dict
   ```

**Key Concepts**:
- Broker abstraction
- Order lifecycle
- Position management

---

### Step 5.2: Paper Trading Broker (45 min)

**File**: `src/quantx/execution/brokers/paper.py`

**Study Order**:

1. **PaperBroker class** - Simulated trading
   - **connect()** - Initialization
   - **place_order()** - Simulate order placement
   - **_execute_order()** - Simulate execution with slippage
   - **get_positions()** - Track simulated positions
   - **get_account_info()** - Simulated account

**Key Concepts**:
- Paper trading simulation
- Realistic execution modeling
- Position tracking

**Hands-On Exercise**:
```bash
# Test paper trading
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/live/paper_trading_example.py
```

---

### Step 5.3: Live Execution Engine (2 hours)

**File**: `src/quantx/execution/live_engine.py` (515 lines, 18,299 bytes)

**Study Order**:

1. **EngineState enum** - Engine states
   ```python
   CREATED → STARTING → RUNNING → PAUSED/STOPPING → STOPPED
                                 ↓
                               ERROR
   ```

2. **LiveExecutionEngine class initialization** (lines 63-109)
   ```python
   def __init__(
       self,
       strategy: BaseStrategy,
       broker: IBroker,
       order_manager: OrderManager,
       risk_manager: RiskManager,
       event_bus: Optional[EventBus] = None,
       config: Optional[EngineConfig] = None
   ):
   ```
   - Understand all dependencies
   - Note the configuration options

3. **start() method** (lines 122-179) - **CRITICAL**
   
   **Flow**:
   ```
   1. Validate state
   2. Connect to broker
   3. Sync positions
   4. Start event bus
   5. Subscribe to events
   6. Start background threads
   7. Notify strategy.on_start()
   8. Set state to RUNNING
   ```

4. **Event Handlers**:
   - **_on_signal()** (lines 351-375) - Handle strategy signals
   - **_on_fill()** (lines 377-388) - Handle order fills
   - **_on_market_data()** (lines 400-403) - Handle market data
   - **_on_risk_violation()** (lines 405-413) - Handle risk violations

5. **Background Threads**:
   - **_position_sync_loop()** (lines 275-286) - Sync positions with broker
   - **_heartbeat_loop()** (lines 288-315) - Health monitoring

**Complete Live Trading Flow**:
```
Market Data Stream
    ↓
EventBus.publish(MARKET_DATA)
    ↓
Strategy.on_data(event)
    ↓
Strategy generates Signal
    ↓
EventBus.publish(SIGNAL)
    ↓
LiveEngine._on_signal(event)
    ↓
Convert Signal to Order
    ↓
OrderManager.submit_order(order)
    ↓
RiskManager.check_order(order)
    ├─→ PASS: Broker.place_order(order)
    │           ↓
    │       EventBus.publish(FILL)
    │           ↓
    │       Strategy.on_fill(event)
    │           ↓
    │       Update positions
    │
    └─→ FAIL: EventBus.publish(RISK_VIOLATION)
```

**Key Concepts**:
- State machine pattern
- Event-driven live trading
- Background thread management
- Position synchronization
- Error handling and recovery

---

### Step 5.4: Risk Management (1 hour)

**File**: `src/quantx/execution/risk/`

**Study Order**:

1. **RiskManager class**
   - **check_order()** - Pre-trade risk checks
   - **Position size limits** - Max position per symbol
   - **Daily loss limits** - Max daily loss
   - **Kill switch** - Emergency stop

**Key Concepts**:
- Pre-trade risk checks
- Position limits
- Loss limits
- Emergency controls

**Hands-On Exercise**:
```bash
# Test risk management
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python examples/live/oms_risk_example.py
```

---

### Step 5.5: Live P&L Tracking (45 min)

**File**: `src/quantx/execution/live_pnl.py` (13,875 bytes)

**Study Order**:

1. **LivePnLTracker class**
   - **update_position()** - Update on trade
   - **calculate_pnl()** - Real-time P&L
   - **get_daily_pnl()** - Daily P&L
   - **get_realized_pnl()** - Realized profits
   - **get_unrealized_pnl()** - Unrealized profits

**Key Concepts**:
- Real-time P&L calculation
- Realized vs unrealized P&L
- Daily P&L tracking

---

## 🌐 Phase 6: API & Dashboard

### Step 6.1: FastAPI Backend (1 hour)

**File**: `src/quantx/api/main.py` (185 lines)

**Study Order**:

1. **FastAPI app setup** (lines 1-49)
   - App initialization
   - CORS middleware
   - Router inclusion

2. **Health endpoints** (lines 51-94)
   - `/` - Root endpoint
   - `/health` - Health check
   - `/api/v1/info` - System info

3. **WebSocket endpoint** (lines 101-129)
   - `/ws/live` - Real-time updates
   - Connection management
   - Broadcasting updates

**Study Routers**:

1. **`src/quantx/api/routers/engine.py`** - Engine control
   - Start/stop engine
   - Get engine status
   - Pause/resume trading

2. **`src/quantx/api/routers/positions.py`** - Position management
   - Get all positions
   - Get position by symbol
   - Close position

3. **`src/quantx/api/routers/orders.py`** - Order management
   - Submit order
   - Cancel order
   - Get order history

4. **`src/quantx/api/routers/pnl.py`** - P&L tracking
   - Get current P&L
   - Get daily P&L
   - Get P&L history

**Hands-On Exercise**:
```bash
# Start API server
cd /home/adil-khan/Builds/QuantX
./start_api.sh

# Or manually
PYTHONPATH="$(pwd)/src" uvicorn quantx.api.main:app --reload --port 8000

# Access API docs
# http://localhost:8000/docs
```

---

### Step 6.2: Next.js Dashboard (1 hour)

**Files to Study**:

1. **`dashboard/package.json`** - Dependencies
   - Next.js, React, TypeScript
   - Tailwind CSS for styling
   - Recharts for charts
   - SWR for data fetching

2. **`dashboard/app/layout.tsx`** - Root layout
   - App structure
   - Global providers

3. **`dashboard/app/page.tsx`** - Home page
   - Dashboard components
   - Real-time updates

**Hands-On Exercise**:
```bash
# Start dashboard
cd /home/adil-khan/Builds/QuantX/dashboard
npm install
npm run dev

# Access dashboard
# http://localhost:3000
```

---

## 🎓 Hands-On Exercises

### Exercise 1: Create a Simple Strategy

**Goal**: Implement a basic RSI strategy

```python
# File: my_rsi_strategy.py
import sys
sys.path.insert(0, 'src')

from quantx.strategies import RuleBasedStrategy, StrategyRegistry
from quantx.core.events import Event
import pandas as pd

@StrategyRegistry.register("my_rsi")
class MyRSIStrategy(RuleBasedStrategy):
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.rsi_period = config.get("rsi_period", 14)
        self.oversold = config.get("oversold", 30)
        self.overbought = config.get("overbought", 70)
        self.prices = []
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        deltas = pd.Series(prices).diff()
        gain = deltas.where(deltas > 0, 0).rolling(window=period).mean()
        loss = -deltas.where(deltas < 0, 0).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if len(rsi) > 0 else 50
    
    def on_data(self, event: Event):
        data = event.data
        symbol = data.get('symbol')
        close = data.get('close')
        
        # Store prices
        self.prices.append(close)
        if len(self.prices) > 100:
            self.prices.pop(0)
        
        # Need enough data
        if len(self.prices) < self.rsi_period + 1:
            return
        
        # Calculate RSI
        rsi = self.calculate_rsi(self.prices, self.rsi_period)
        
        # Generate signals
        if rsi < self.oversold and not self.has_position(symbol):
            # Oversold - buy signal
            self.buy(symbol, 100, close)
            print(f"BUY signal: RSI={rsi:.2f}")
        
        elif rsi > self.overbought and self.has_position(symbol):
            # Overbought - sell signal
            position = self.get_position(symbol)
            self.sell(symbol, abs(position), close)
            print(f"SELL signal: RSI={rsi:.2f}")
    
    def on_fill(self, event: Event):
        fill_data = event.data
        symbol = fill_data.get('symbol')
        quantity = fill_data.get('quantity')
        price = fill_data.get('price')
        
        self.update_position(symbol, quantity)
        print(f"Order filled: {quantity} {symbol} @ ${price:.2f}")

# Test the strategy
if __name__ == "__main__":
    from quantx.backtesting import BacktestEngine
    from quantx.data.providers.yahoo import YahooFinanceProvider
    from datetime import datetime, timedelta
    
    # Create strategy
    config = {
        "rsi_period": 14,
        "oversold": 30,
        "overbought": 70
    }
    strategy = MyRSIStrategy("my_rsi", config)
    
    # Create backtest engine
    provider = YahooFinanceProvider()
    engine = BacktestEngine(
        strategy=strategy,
        data_provider=provider,
        initial_capital=100000
    )
    
    # Run backtest
    results = engine.run(
        symbols=["AAPL"],
        start_date=datetime.now() - timedelta(days=365),
        end_date=datetime.now(),
        interval="1d"
    )
    
    # Print results
    engine.print_results(results)
```

**Run it**:
```bash
cd /home/adil-khan/Builds/QuantX
PYTHONPATH="$(pwd)/src" python my_rsi_strategy.py
```

---

### Exercise 2: Modify MA Crossover Strategy

**Goal**: Add a volume filter to the MA crossover strategy

**Steps**:
1. Open `src/quantx/strategies/rule_based/ma_crossover.py`
2. Add volume parameter to config
3. Modify `on_data()` to check volume
4. Only generate signals when volume > average volume

---

### Exercise 3: Create Custom Feature

**Goal**: Add a custom technical indicator

**Steps**:
1. Open `src/quantx/ml/features/technical.py`
2. Add a new method for your indicator
3. Test it with feature engineering demo

---

### Exercise 4: Paper Trade Your Strategy

**Goal**: Run your strategy in paper trading mode

**Steps**:
1. Create your strategy
2. Set up PaperBroker
3. Create LiveExecutionEngine
4. Start trading
5. Monitor positions and P&L

---

## 🔍 Deep Dive Topics

### Topic 1: Event Flow Tracing

**Exercise**: Add logging to trace complete event flow

```python
# Add to each component
logger.info(f"[{component_name}] Event received: {event.event_type}")
logger.info(f"[{component_name}] Processing: {event.data}")
logger.info(f"[{component_name}] Result: {result}")
```

**Run a backtest and trace**:
- Market data event → Strategy
- Signal event → Backtest engine
- Fill event → Strategy

---

### Topic 2: Performance Optimization

**Study**:
1. How data is cached in YahooFinanceProvider
2. How events are queued and processed
3. How portfolio calculations are optimized

**Experiment**:
- Profile a backtest with cProfile
- Identify bottlenecks
- Optimize slow sections

---

### Topic 3: Error Handling

**Study**:
1. How errors are handled in event processing
2. How broker connection failures are handled
3. How risk violations are handled

**Experiment**:
- Trigger various error conditions
- Observe recovery mechanisms
- Add custom error handlers

---

### Topic 4: Extending the System

**Practice**:
1. Add a new data provider (e.g., Alpha Vantage)
2. Add a new broker (e.g., Interactive Brokers)
3. Add a new ML model (e.g., CNN)
4. Add a new risk check

---

## 📝 Study Checklist

### Core Foundations
- [ ] Understand event-driven architecture
- [ ] Read EventBus implementation
- [ ] Understand configuration system
- [ ] Grasp SOLID principles application

### Data & Strategy
- [ ] Understand data provider interface
- [ ] Study Yahoo Finance implementation
- [ ] Understand strategy base classes
- [ ] Study MA Crossover strategy
- [ ] Understand strategy registry

### Backtesting
- [ ] Understand portfolio management
- [ ] Study performance metrics
- [ ] Understand backtest engine flow
- [ ] Run complete backtest example
- [ ] Analyze backtest results

### Machine Learning
- [ ] Understand feature engineering
- [ ] Study technical indicators
- [ ] Understand ML model interface
- [ ] Train traditional ML models
- [ ] Train deep learning models
- [ ] Run complete ML pipeline

### Live Trading
- [ ] Understand broker interface
- [ ] Study paper trading broker
- [ ] Understand live execution engine
- [ ] Study risk management
- [ ] Test paper trading
- [ ] Understand P&L tracking

### API & Dashboard
- [ ] Understand FastAPI structure
- [ ] Study API routers
- [ ] Test API endpoints
- [ ] Understand dashboard structure
- [ ] Run dashboard locally

### Hands-On
- [ ] Create custom strategy
- [ ] Backtest custom strategy
- [ ] Create custom features
- [ ] Train custom ML model
- [ ] Paper trade strategy
- [ ] Extend the system

---

## 🎯 Learning Milestones

### Milestone 1: Beginner (Week 1)
- ✅ Understand architecture
- ✅ Read core event system
- ✅ Understand strategy framework
- ✅ Run backtest examples

### Milestone 2: Intermediate (Week 2-3)
- ✅ Create custom strategy
- ✅ Understand ML pipeline
- ✅ Train ML models
- ✅ Understand live trading basics

### Milestone 3: Advanced (Week 4+)
- ✅ Extend the system
- ✅ Optimize performance
- ✅ Add custom components
- ✅ Deploy to production

---

## 📚 Additional Resources

### Documentation
- `docs/ARCHITECTURE.md` - Deep architecture dive
- `docs/PRD.md` - Product requirements
- `docs/TESTING_GUIDE.md` - Testing guide
- `docs/LIVE_TRADING.md` - Live trading guide

### Examples
- `examples/` - All example scripts
- `examples/ml/` - ML examples
- `examples/live/` - Live trading examples

### Tests
- `tests/unit/` - Unit tests (learn from these!)
- `tests/integration/` - Integration tests

---

## 💡 Tips for Success

1. **Start Small**: Don't try to understand everything at once
2. **Run Examples**: Always run code to see it in action
3. **Add Logging**: Add print statements to understand flow
4. **Experiment**: Modify code and see what happens
5. **Read Tests**: Tests show how components are used
6. **Draw Diagrams**: Visualize the architecture
7. **Ask Questions**: Use comments to document your understanding
8. **Build Projects**: Create your own strategies and features

---

## 🎓 Next Steps After Completion

1. **Contribute**: Add features, fix bugs, improve docs
2. **Deploy**: Set up production environment
3. **Optimize**: Profile and optimize performance
4. **Scale**: Add distributed backtesting
5. **Extend**: Add new brokers, data sources, models

---

**Happy Learning! 🚀**

Start with Phase 1 and work your way through. Take your time, experiment, and don't hesitate to dive deep into any component that interests you!
