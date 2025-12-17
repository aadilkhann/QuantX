# QuantX - Complete Setup and Running Guide 🚀

**Last Updated**: December 14, 2025  
**Project Status**: Phase 3 in Progress (55% Complete)

This comprehensive guide will help you set up and run the QuantX algorithmic trading system locally.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running Examples](#running-examples)
5. [Project Structure](#project-structure)
6. [Testing Your Setup](#testing-your-setup)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **Python 3.11 or higher** - Check version:
  ```bash
  python3 --version
  ```

- **pip** - Python package installer (comes with Python)
  ```bash
  pip3 --version
  ```

### Optional but Recommended

- **Poetry** - Modern Python dependency management
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

- **Git** - Version control (if cloning from repository)
  ```bash
  git --version
  ```

### System Requirements

- **RAM**: Minimum 4GB, 8GB+ recommended for ML models
- **Storage**: At least 2GB free space
- **OS**: macOS, Linux, or Windows (WSL2 recommended for Windows)

---

## 🔧 Installation

### Step 1: Navigate to Project Directory

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
```

### Step 2: Create Virtual Environment

Using **venv** (built-in):

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

Using **Poetry** (recommended):

```bash
# Install dependencies and create virtual environment
poetry install

# Activate virtual environment
poetry shell
```

### Step 3: Install Dependencies

#### Option A: Using pip (Simple)

Install basic dependencies for Phase 1 & 2:

```bash
pip install -r requirements.txt
```

#### Option B: Using Poetry (Recommended)

Install all dependencies including dev tools:

```bash
poetry install
```

This will install:
- Core dependencies (pandas, numpy, yfinance, etc.)
- Machine learning libraries (scikit-learn, xgboost, lightgbm, torch)
- ML model management (mlflow)
- Development tools (pytest, black, mypy)
- Documentation tools (mkdocs)

### Step 4: Verify Installation

#### Option A: Quick Test (Recommended)

```bash
# Run the setup validation script
python3 test_setup.py
```

This will check:
- ✅ Python version compatibility
- ✅ Module imports (Core, ML, Execution)
- ✅ Dependencies (pandas, numpy, yfinance, etc.)
- ✅ Data fetching capability

**Expected output**: "🎉 All tests passed! Your QuantX installation is ready to use."

#### Option B: Manual Test

```bash
# Check if quantx can be imported
python3 -c "import sys; sys.path.insert(0, 'src'); from quantx.core.config import Config; print('✅ QuantX installed successfully!')"
```

---

## 🚀 Quick Start (Interactive)

Want to jump right in? Use the interactive quick start script:

```bash
# Make it executable (first time only)
chmod +x quickstart.sh

# Run it
./quickstart.sh
```

This will present an interactive menu to:
- Run Phase 1 backtesting examples
- Try Phase 2 ML features
- Test Phase 3 paper trading
- Validate your setup

**Perfect for first-time users!** 🎯

---

## ⚙️ Configuration

### Step 1: Create Environment File

```bash
# Copy example environment file
cp .env.example .env
```

### Step 2: Edit Configuration (Optional)

For basic usage, the defaults work fine. Edit `.env` if you need to:

```bash
nano .env  # or use your preferred editor
```

**Key Configuration Options**:

```env
# Application
APP_ENV=development
DEBUG=true

# Data Providers
YAHOO_FINANCE_ENABLED=true  # No API key required!

# Risk Management (for Phase 3)
RISK_MAX_POSITION_SIZE=0.1   # Max 10% of portfolio per position
RISK_MAX_DAILY_LOSS=0.02     # Max 2% daily loss
RISK_MAX_DRAWDOWN=0.15       # Max 15% drawdown

# Feature Flags
FEATURE_LIVE_TRADING=false   # Set to true when ready for paper trading
```

> **Note**: Yahoo Finance doesn't require an API key and is perfect for getting started!

---

## 🏃 Running Examples

### Phase 1: Backtesting (100% Complete) ✅

#### Example 1: Fetch Market Data

```bash
python examples/fetch_data.py
```

**What it does**:
- Loads configuration
- Creates Yahoo Finance data provider
- Fetches 30 days of AAPL historical data
- Displays basic statistics

**Expected Output**:
```
✅ Successfully fetched 30 days of data
OHLCV data shape: (30, 6)
Average volume: 1,234,567
```

#### Example 2: Strategy Registry

```bash
python examples/strategy_registry.py
```

**What it does**:
- Lists all registered strategies
- Creates a Moving Average Crossover strategy
- Displays strategy configuration

#### Example 3: Complete Backtest (⭐ Recommended)

```bash
python examples/complete_backtest.py
```

**What it does**:
- Fetches 2 years of AAPL historical data
- Runs MA Crossover strategy
- Calculates comprehensive performance metrics
- Generates equity curve plot
- Displays detailed results

**Expected Output**:
```
=== Backtest Results ===
Total Return: 45.23%
Sharpe Ratio: 1.85
Max Drawdown: -12.34%
Win Rate: 58.5%
Total Trades: 47
```

### Phase 2: Machine Learning (100% Complete) ✅

#### Example 1: Feature Engineering

```bash
python examples/ml/feature_engineering_demo.py
```

**What it does**:
- Demonstrates feature engineering pipeline
- Creates technical indicators
- Shows statistical features
- Displays market regime detection

#### Example 2: Train Traditional ML Models

```bash
python examples/ml/train_traditional_models.py
```

**What it does**:
- Trains Random Forest, Gradient Boosting, and XGBoost models
- Evaluates model performance
- Saves trained models

**Duration**: ~2-5 minutes depending on your machine

#### Example 3: Train Deep Learning Models

```bash
python examples/ml/train_deep_learning.py
```

**What it does**:
- Trains LSTM and Transformer models
- Uses GPU if available (falls back to CPU)
- Evaluates deep learning performance

**Duration**: ~5-15 minutes depending on hardware

> **Note**: Deep learning examples may take longer. Start with traditional ML first!

#### Example 4: MLflow Integration

```bash
python examples/ml/mlflow_integration.py
```

**What it does**:
- Demonstrates MLflow experiment tracking
- Logs parameters, metrics, and models
- Shows model registry usage

**To view MLflow UI**:
```bash
mlflow ui
# Then open http://localhost:5000 in your browser
```

#### Example 5: Complete ML Pipeline

```bash
python examples/ml/complete_pipeline.py
```

**What it does**:
- End-to-end ML pipeline
- Feature engineering → Training → Evaluation → Backtesting
- Compares ML strategy vs baseline

#### Example 6: AI-Powered Strategy

```bash
python examples/ml/ai_strategy_example.py
```

**What it does**:
- Creates an AI-powered trading strategy
- Uses trained ML model for predictions
- Backtests the strategy

### Phase 3: Live Trading (55% Complete) 🚧

#### Example 1: Paper Trading Basics

```bash
python examples/live/paper_trading_example.py
```

**What it does**:
- Demonstrates 5 paper trading scenarios
- Shows order placement, position tracking, P&L calculation
- Simulates realistic trading with slippage and commissions

**Scenarios**:
1. Basic paper trading setup
2. Multiple trades and position tracking
3. Selling and realizing P&L
4. Using BrokerFactory pattern
5. Realistic trading with real market data

#### Example 2: Order Management & Risk Controls

```bash
python examples/live/oms_risk_example.py
```

**What it does**:
- Demonstrates Order Management System (OMS)
- Shows risk management controls
- Position limits, daily loss limits, kill switch
- Order validation and event callbacks

**Scenarios**:
1. Basic OMS with order validation
2. Risk manager with position limits
3. Daily loss limits and kill switch
4. Multi-broker order routing
5. Complete integration with paper trading

---

## 📁 Project Structure

```
QuantX/
├── src/quantx/              # Source code
│   ├── core/                # Core infrastructure
│   │   ├── events.py        # Event-driven system
│   │   └── config.py        # Configuration management
│   ├── data/                # Data layer
│   │   ├── base.py          # Data interfaces
│   │   └── providers/       # Data providers (Yahoo Finance, etc.)
│   ├── strategies/          # Trading strategies
│   │   ├── base.py          # Base strategy classes
│   │   ├── registry.py      # Strategy registry
│   │   └── rule_based/      # Rule-based strategies
│   ├── backtesting/         # Backtesting engine
│   │   ├── portfolio.py     # Portfolio management
│   │   ├── metrics.py       # Performance metrics
│   │   └── engine.py        # Backtest engine
│   ├── ml/                  # Machine learning (Phase 2)
│   │   ├── features/        # Feature engineering
│   │   ├── models/          # ML models
│   │   └── evaluation/      # Model evaluation
│   └── execution/           # Live trading (Phase 3)
│       ├── brokers/         # Broker implementations
│       ├── orders/          # Order management
│       └── risk/            # Risk management
├── examples/                # Example scripts
│   ├── fetch_data.py        # Phase 1: Fetch data
│   ├── complete_backtest.py # Phase 1: Backtest
│   ├── ml/                  # Phase 2: ML examples
│   └── live/                # Phase 3: Live trading
├── docs/                    # Documentation
├── tests/                   # Unit tests
├── configs/                 # Configuration files
├── data/                    # Data storage
├── pyproject.toml           # Poetry configuration
├── requirements.txt         # Pip requirements
└── .env.example             # Environment template
```

---

## 🧪 Testing Your Setup

### Quick Health Check

Run this script to verify everything is working:

```bash
python3 << 'EOF'
import sys
print("=== QuantX Setup Health Check ===\n")

# Check Python version
print(f"✓ Python version: {sys.version.split()[0]}")

# Check core imports
try:
    from quantx.core.config import Config
    print("✓ Core module imported successfully")
except ImportError as e:
    print(f"✗ Core module import failed: {e}")

# Check data providers
try:
    from quantx.data.providers.yahoo import YahooFinanceProvider
    print("✓ Data providers imported successfully")
except ImportError as e:
    print(f"✗ Data providers import failed: {e}")

# Check strategies
try:
    from quantx.strategies import StrategyRegistry
    print("✓ Strategy framework imported successfully")
except ImportError as e:
    print(f"✗ Strategy framework import failed: {e}")

# Check backtesting
try:
    from quantx.backtesting import BacktestEngine
    print("✓ Backtesting engine imported successfully")
except ImportError as e:
    print(f"✗ Backtesting engine import failed: {e}")

# Check ML (Phase 2)
try:
    from quantx.ml.features import FeatureEngineer
    print("✓ ML module imported successfully")
except ImportError as e:
    print(f"✗ ML module import failed: {e}")

# Check execution (Phase 3)
try:
    from quantx.execution.brokers import PaperBroker
    print("✓ Execution module imported successfully")
except ImportError as e:
    print(f"✗ Execution module import failed: {e}")

print("\n=== Setup Complete! ===")
EOF
```

### Run a Quick Backtest

```bash
# This should complete in under a minute
python examples/complete_backtest.py
```

If you see performance metrics and an equity curve, you're all set! 🎉

---

## 🐛 Troubleshooting

### Issue 1: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'quantx'`

**Solution**:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # or: poetry shell

# Verify you're in the project directory
pwd  # Should show: /Users/adii/Builds/Algo-Trading/QuantX

# Add project to Python path temporarily
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or install in development mode
pip install -e .
```

### Issue 2: Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'pandas'` (or other package)

**Solution**:
```bash
# Install all required packages
pip install -r requirements.txt

# Or specific package
pip install pandas yfinance loguru pydantic
```

### Issue 3: Yahoo Finance Errors

**Problem**: Yahoo Finance data fetch fails or times out

**Solutions**:
```bash
# 1. Wait a few minutes (rate limiting)
# 2. Try different ticker symbol
# 3. Use shorter date range
# 4. Check internet connection
# 5. Update yfinance package
pip install --upgrade yfinance
```

### Issue 4: MLflow Not Found

**Problem**: `ModuleNotFoundError: No module named 'mlflow'`

**Solution**:
```bash
pip install mlflow
```

### Issue 5: PyTorch/GPU Issues

**Problem**: PyTorch not using GPU or CUDA errors

**Solution**:
```python
# Check PyTorch installation
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"

# CPU-only is fine for getting started!
# GPU will just make training faster
```

### Issue 6: Permission Errors

**Problem**: Permission denied when creating directories

**Solution**:
```bash
# Create necessary directories
mkdir -p data/models data/cache data/logs

# Check permissions
ls -la data/
```

### Issue 7: Port Already in Use (for MLflow UI)

**Problem**: Port 5000 already in use

**Solution**:
```bash
# Use different port
mlflow ui --port 5001
```

---

## 📚 Learning Path

### 1. Start with Phase 1 (Backtesting)

**Goal**: Understand the basics of algorithmic trading

**Run these in order**:
1. `python examples/fetch_data.py` - Learn data fetching
2. `python examples/strategy_registry.py` - Understand strategies
3. `python examples/complete_backtest.py` - Run your first backtest

**Time**: 30 minutes

### 2. Explore Phase 2 (Machine Learning)

**Goal**: Add ML capabilities to your strategies

**Run these**:
1. `python examples/ml/feature_engineering_demo.py` - See feature engineering
2. `python examples/ml/train_traditional_models.py` - Train ML models
3. `python examples/ml/ai_strategy_example.py` - AI-powered trading

**Time**: 1-2 hours (training takes time)

### 3. Try Phase 3 (Paper Trading)

**Goal**: Simulate live trading safely

**Run these**:
1. `python examples/live/paper_trading_example.py` - Paper trading basics
2. `python examples/live/oms_risk_example.py` - Order management & risk

**Time**: 30 minutes

---

## 🎯 Next Steps

### After Setup, You Can:

1. **Experiment with Parameters**
   ```python
   # Edit examples/complete_backtest.py
   # Try different MA periods: 20/50, 10/30, etc.
   # Try different symbols: GOOGL, MSFT, TSLA
   ```

2. **Create Your Own Strategy**
   ```python
   from quantx.strategies import RuleBasedStrategy, StrategyRegistry
   
   @StrategyRegistry.register("my_strategy")
   class MyStrategy(RuleBasedStrategy):
       def on_data(self, event):
           # Your custom logic here
           pass
   ```

3. **Train Your Own ML Models**
   ```bash
   # Customize ML pipeline
   python examples/ml/complete_pipeline.py
   
   # View results in MLflow
   mlflow ui
   ```

4. **Paper Trade Your Strategy**
   ```python
   # Test your strategy with simulated money
   from quantx.execution.brokers import PaperBroker
   broker = PaperBroker({"initial_capital": 100000})
   ```

### Recommended Reading

- [`README.md`](file:///Users/adii/Builds/Algo-Trading/QuantX/README.md) - Complete project overview
- [`IMPLEMENTATION_STATUS.md`](file:///Users/adii/Builds/Algo-Trading/QuantX/IMPLEMENTATION_STATUS.md) - Phase 1 details
- [`docs/PHASE3_PROGRESS.md`](file:///Users/adii/Builds/Algo-Trading/QuantX/docs/PHASE3_PROGRESS.md) - Phase 3 progress
- `docs/` directory - Full documentation

---

## 🔥 Quick Start Commands (TL;DR)

### Super Quick (Interactive Menu)

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
./quickstart.sh
# Select option from the menu
```

### Standard Setup

```bash
# Setup
cd /Users/adii/Builds/Algo-Trading/QuantX
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Validate installation
python3 test_setup.py

# Run examples (with PYTHONPATH)
PYTHONPATH="$(pwd)/src" python examples/fetch_data.py
PYTHONPATH="$(pwd)/src" python examples/complete_backtest.py
PYTHONPATH="$(pwd)/src" python examples/live/paper_trading_example.py
```

> **Note**: Examples need `PYTHONPATH` set to find the `quantx` module, or you can use the interactive `quickstart.sh` script which handles this automatically!


---

## 📊 What You Can Do Now

| Feature | Status | Command |
|---------|--------|---------|
| Fetch market data | ✅ Ready | `python examples/fetch_data.py` |
| Backtest strategies | ✅ Ready | `python examples/complete_backtest.py` |
| Feature engineering | ✅ Ready | `python examples/ml/feature_engineering_demo.py` |
| Train ML models | ✅ Ready | `python examples/ml/train_traditional_models.py` |
| Train deep learning | ✅ Ready | `python examples/ml/train_deep_learning.py` |
| AI-powered strategies | ✅ Ready | `python examples/ml/ai_strategy_example.py` |
| Paper trading | ✅ Ready | `python examples/live/paper_trading_example.py` |
| Order management | ✅ Ready | `python examples/live/oms_risk_example.py` |
| Live trading | 🚧 In Progress | Coming soon |

---

## 💡 Tips for Success

1. **Start Simple**: Begin with Phase 1 backtesting before jumping to ML
2. **Use Paper Trading**: Never test with real money initially
3. **Track Experiments**: Use MLflow to track all your ML experiments
4. **Monitor Risk**: Always use risk management controls
5. **Stay Updated**: Check `docs/` for latest documentation

---

## 🆘 Getting Help

If you encounter issues:

1. **Check Documentation**: See `docs/` directory
2. **Review Examples**: All examples have detailed comments
3. **Check Logs**: Look in `data/logs/` if configured
4. **Debug Mode**: Set `DEBUG=true` in `.env`

---

## 🎉 You're All Set!

Your QuantX trading system is ready to use. Start with a simple backtest and work your way up to ML-powered strategies and paper trading.

**Happy Trading! 📈**

---

**Project**: QuantX - AI-Powered & Rule-Based Trading System  
**Version**: 0.1.0 (Phase 3 in Progress)  
**License**: MIT  
**Last Updated**: December 14, 2025
