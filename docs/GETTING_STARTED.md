# Getting Started with QuantX

Welcome to QuantX! This document will help you get started quickly.

## 📂 Key Documents

### Setup & Installation

1. **[SETUP_AND_RUN_GUIDE.md](../SETUP_AND_RUN_GUIDE.md)** ⭐ **START HERE**
   - Complete setup and installation guide
   - How to run all examples
   - Troubleshooting tips
   - Learning path

2. **[README.md](../README.md)**
   - Project overview
   - Architecture
   - Feature list

3. **[QUICKSTART.md](../QUICKSTART.md)**
   - Quick reference guide
   - Basic usage examples

### Progress & Status

4. **[IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md)**
   - Phase 1 (Backtesting) - 100% Complete
   - What's implemented
   - What you can do

5. **[PHASE3_PROGRESS.md](./PHASE3_PROGRESS.md)**
   - Phase 3 (Live Trading) - 55% Complete
   - Paper trading
   - Order management
   - Risk controls

## 🚀 Quick Start

### Option 1: Interactive Menu (Easiest)

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
./quickstart.sh
```

This interactive script will guide you through:
- Running Phase 1 backtesting examples
- Trying Phase 2 ML features
- Testing Phase 3 paper trading
- Validating your setup

### Option 2: Validate Installation

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
python3 test_setup.py
```

This will verify:
- Python version (3.11+)
- All modules can be imported
- Dependencies are installed
- Data fetching works

### Option 3: Manual Setup

Follow the detailed guide in [SETUP_AND_RUN_GUIDE.md](../SETUP_AND_RUN_GUIDE.md).

## 📚 What to Read First

### For Beginners

1. Read: [SETUP_AND_RUN_GUIDE.md](../SETUP_AND_RUN_GUIDE.md) - Section "Quick Start"
2. Run: `./quickstart.sh` - Option 1 (Fetch market data)
3. Run: `./quickstart.sh` - Option 2 (Complete backtest)
4. Read: [IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md) - See what's possible

### For ML Enthusiasts

1. Read: [SETUP_AND_RUN_GUIDE.md](../SETUP_AND_RUN_GUIDE.md) - "Phase 2: Machine Learning"
2. Run: Feature engineering demo
3. Run: Train traditional models
4. Check: MLflow UI to see experiments

### For Live Trading

1. Read: [PHASE3_PROGRESS.md](./PHASE3_PROGRESS.md) - Current progress
2. Run: Paper trading example
3. Run: OMS and risk management example
4. Note: Live broker integration coming soon

## 🎯 Learning Path

```
Day 1: Setup and Basics
├── Install dependencies
├── Validate setup with test_setup.py
├── Run fetch_data.py example
└── Run complete_backtest.py

Day 2: Advanced Backtesting
├── Understand strategy registry
├── Create your own strategy
├── Experiment with parameters
└── Analyze performance metrics

Day 3: Machine Learning
├── Feature engineering
├── Train traditional ML models
├── Build AI-powered strategy
└── Compare ML vs rule-based

Day 4: Paper Trading
├── Understand broker abstraction
├── Place orders with paper broker
├── Learn OMS and risk management
└── Build complete trading system
```

## 📖 Documentation Structure

```
docs/
├── README.md (this file)           # Getting started guide
├── PHASE3_PROGRESS.md              # Phase 3 progress
├── API.md                          # API documentation
├── ARCHITECTURE.md                 # System architecture
├── BACKTESTING.md                  # Backtesting guide
├── DATA_PROVIDERS.md               # Data provider docs
├── DEPLOYMENT.md                   # Deployment guide
├── DEVELOPMENT.md                  # Development guide
├── ML_FEATURES.md                  # ML feature engineering
├── MONITORING.md                   # Monitoring setup
├── RISK_MANAGEMENT.md              # Risk management
├── STRATEGIES.md                   # Strategy development
└── TESTING.md                      # Testing guide
```

## 🛠️ Helper Scripts

### test_setup.py

Validates your installation:

```bash
python3 test_setup.py
```

Checks:
- ✅ Python version (3.11+)
- ✅ Core module imports
- ✅ Phase 2 (ML) imports
- ✅ Phase 3 (Live) imports
- ✅ Critical dependencies
- ✅ Optional ML dependencies
- ✅ Data fetching capability

### quickstart.sh

Interactive menu for running examples:

```bash
./quickstart.sh
```

Options:
1. Fetch market data (5 sec)
2. Complete backtest (30 sec)
3. Strategy registry demo (5 sec)
4. Feature engineering demo (15 sec)
5. AI-powered strategy (1-2 min)
6. Complete ML pipeline (2-3 min)
7. Paper trading basics (10 sec)
8. Order management & risk (15 sec)
9. Run setup validation

## 🎓 Examples

All examples are in the `examples/` directory:

### Phase 1 (Backtesting)
- `fetch_data.py` - Fetch market data
- `strategy_registry.py` - Strategy registration
- `complete_backtest.py` - Full backtest with metrics

### Phase 2 (Machine Learning)
- `ml/feature_engineering_demo.py` - Feature engineering
- `ml/train_traditional_models.py` - Train ML models
- `ml/train_deep_learning.py` - Train deep learning
- `ml/mlflow_integration.py` - MLflow tracking
- `ml/complete_pipeline.py` - End-to-end pipeline
- `ml/ai_strategy_example.py` - AI trading strategy
- `ml/configuration_flexibility.py` - Configuration patterns

### Phase 3 (Live Trading)
- `live/paper_trading_example.py` - Paper trading (5 scenarios)
- `live/oms_risk_example.py` - OMS and risk (5 scenarios)

## 💬 Getting Help

1. **Read Documentation**: Start with [SETUP_AND_RUN_GUIDE.md](../SETUP_AND_RUN_GUIDE.md)
2. **Run Validation**: Use `python3 test_setup.py`
3. **Check Examples**: All examples have detailed comments
4. **Review Progress**: See what's implemented in each phase

## 🎉 Ready to Start?

Run this now:

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
./quickstart.sh
```

**Happy Trading! 📈**

---

**Last Updated**: December 14, 2025
