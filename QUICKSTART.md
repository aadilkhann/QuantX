# QuantX - Quick Start Guide

## Installation

### Prerequisites
- Python 3.11 or higher
- pip or Poetry

### Setup

1. **Clone/Navigate to QuantX directory**:
```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:

Using pip:
```bash
pip install -r requirements.txt
```

Or using Poetry (recommended):
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration (optional for basic usage)
```

## Running Examples

### Example 1: Fetch Market Data

```bash
python examples/fetch_data.py
```

This will:
- Load configuration
- Create Yahoo Finance data provider
- Fetch 30 days of AAPL data
- Display statistics

### Example 2: Strategy Registry

```bash
python examples/strategy_registry.py
```

This will:
- List registered strategies
- Create a MA Crossover strategy instance
- Display strategy configuration

## Basic Usage

### 1. Fetch Historical Data

```python
from datetime import datetime, timedelta
from quantx.data.providers.yahoo import YahooFinanceProvider

# Create provider
provider = YahooFinanceProvider()

# Fetch data
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
data = provider.get_historical_data("AAPL", start_date, end_date)

print(data.head())
```

### 2. Create a Strategy

```python
from quantx.strategies import StrategyRegistry

# Create MA Crossover strategy
config = {
    "fast_period": 50,
    "slow_period": 200,
    "symbols": ["AAPL", "GOOGL"]
}

strategy = StrategyRegistry.create("ma_crossover", config)
```

### 3. Use Event Bus

```python
from quantx.core.events import EventBus, Event, EventType
from datetime import datetime

# Create event bus
event_bus = EventBus()

# Subscribe to events
def on_signal(event):
    print(f"Signal received: {event.data}")

event_bus.subscribe(EventType.SIGNAL, on_signal)

# Start event bus
event_bus.start()

# Publish event
event = Event(
    priority=1,
    event_type=EventType.SIGNAL,
    timestamp=datetime.now(),
    data={"symbol": "AAPL", "action": "BUY"},
    source="example"
)
event_bus.publish(event)

# Stop event bus
event_bus.stop()
```

## Project Structure

```
QuantX/
├── src/quantx/          # Source code
│   ├── core/            # Core infrastructure
│   ├── data/            # Data layer
│   └── strategies/      # Trading strategies
├── examples/            # Example scripts
├── docs/                # Documentation
├── tests/               # Tests (coming soon)
└── configs/             # Configuration files
```

## What's Implemented

✅ Core Infrastructure:
- Event system with pub/sub
- Configuration management
- Logging setup

✅ Data Layer:
- Yahoo Finance provider
- Data validation
- Market data standardization

✅ Strategy Framework:
- Base strategy classes
- Strategy registry
- MA Crossover example strategy

## Next Steps

1. **Run the examples** to see the system in action
2. **Create your own strategy** by extending `RuleBasedStrategy`
3. **Explore the documentation** in the `docs/` directory
4. **Wait for backtesting engine** (coming soon!)

## Troubleshooting

### Import Errors

If you get import errors, make sure you're in the virtual environment:
```bash
source venv/bin/activate  # or: poetry shell
```

### Missing Dependencies

Install missing packages:
```bash
pip install yfinance pandas loguru pydantic pydantic-settings
```

### Data Fetch Errors

Yahoo Finance may have rate limits. If you get errors:
- Wait a few minutes and try again
- Use longer time intervals
- Enable caching in the provider

## Support

- **Documentation**: See `docs/` directory
- **Issues**: Create GitHub issue
- **Examples**: Check `examples/` directory

---

**Status**: Phase 1 - Foundation (60% Complete)  
**Last Updated**: November 25, 2025
