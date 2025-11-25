# QuantX - AI-Powered & Rule-Based Trading System

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**QuantX** is a next-generation, modular algorithmic trading platform that combines the power of **AI/ML models** with **rule-based strategies** to create fast, efficient, and reliable trading systems.

## 🎯 Vision

Build a production-ready trading system that:
- ✅ Supports both AI-powered and rule-based strategies
- ✅ Enables seamless strategy composition and switching
- ✅ Provides comprehensive backtesting with realistic market simulation
- ✅ Maintains clean, modular architecture for easy extensibility
- ✅ Delivers institutional-grade performance and reliability

## 🌟 Key Features

### Hybrid Strategy Engine
- **AI-Powered Strategies**: Deep learning, ensemble models, reinforcement learning
- **Rule-Based Strategies**: Technical indicators, pattern recognition, statistical arbitrage
- **Hybrid Strategies**: Combine AI predictions with rule-based filters
- **Strategy Composition**: Mix and match multiple strategies with custom weights

### Multi-Asset Support
- **Equities**: Stocks, ETFs (NSE, NYSE, NASDAQ)
- **Derivatives**: Futures, Options (planned)
- **Cryptocurrencies**: Spot and futures markets
- **Forex**: Currency pairs (planned)

### Advanced Backtesting
- Event-driven simulation engine
- Realistic order execution modeling
- Transaction cost analysis
- Slippage and market impact simulation
- Walk-forward optimization
- Monte Carlo simulation

### Modular Architecture
- **Plugin-based design**: Add/remove modules without affecting core
- **Strategy isolation**: Each strategy runs independently
- **Clean interfaces**: Well-defined contracts between components
- **Dependency injection**: Easy testing and mocking

### Production-Ready
- Real-time data streaming
- Low-latency order execution
- Comprehensive monitoring and alerting
- Risk management controls
- Paper trading mode
- Multi-broker support

## 📁 Project Structure

```
QuantX/
├── docs/                          # Documentation
│   ├── architecture/              # Architecture diagrams and design docs
│   ├── api/                       # API documentation
│   ├── guides/                    # User and developer guides
│   ├── PRD.md                     # Product Requirements Document
│   ├── ARCHITECTURE.md            # System Architecture
│   └── DEPLOYMENT.md              # Deployment Guide
│
├── src/                           # Source code
│   ├── quantx/                    # Main package
│   │   ├── core/                  # Core framework
│   │   │   ├── events/            # Event system
│   │   │   ├── config/            # Configuration management
│   │   │   └── logging/           # Logging framework
│   │   │
│   │   ├── data/                  # Data layer
│   │   │   ├── providers/         # Data source integrations
│   │   │   ├── storage/           # Data storage backends
│   │   │   ├── features/          # Feature engineering
│   │   │   └── pipeline/          # Data processing pipelines
│   │   │
│   │   ├── strategies/            # Strategy framework
│   │   │   ├── base/              # Base strategy classes
│   │   │   ├── rule_based/        # Rule-based strategies
│   │   │   ├── ai_powered/        # AI/ML strategies
│   │   │   ├── hybrid/            # Hybrid strategies
│   │   │   └── registry/          # Strategy registry
│   │   │
│   │   ├── ml/                    # Machine Learning
│   │   │   ├── models/            # ML model implementations
│   │   │   ├── training/          # Training pipelines
│   │   │   ├── evaluation/        # Model evaluation
│   │   │   └── registry/          # Model versioning
│   │   │
│   │   ├── backtesting/           # Backtesting engine
│   │   │   ├── engine/            # Core backtesting logic
│   │   │   ├── portfolio/         # Portfolio management
│   │   │   ├── execution/         # Order execution simulation
│   │   │   ├── metrics/           # Performance metrics
│   │   │   └── reports/           # Report generation
│   │   │
│   │   ├── execution/             # Live trading execution
│   │   │   ├── brokers/           # Broker integrations
│   │   │   ├── orders/            # Order management
│   │   │   ├── positions/         # Position tracking
│   │   │   └── risk/              # Risk management
│   │   │
│   │   ├── monitoring/            # Monitoring & Analytics
│   │   │   ├── dashboard/         # Real-time dashboard
│   │   │   ├── alerts/            # Alert system
│   │   │   └── analytics/         # Performance analytics
│   │   │
│   │   └── utils/                 # Utilities
│   │       ├── indicators/        # Technical indicators
│   │       ├── math/              # Mathematical utilities
│   │       └── validation/        # Data validation
│   │
│   └── examples/                  # Example strategies and usage
│
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── strategies/                # Strategy backtests
│
├── configs/                       # Configuration files
│   ├── strategies/                # Strategy configurations
│   ├── data/                      # Data source configurations
│   └── brokers/                   # Broker configurations
│
├── notebooks/                     # Jupyter notebooks
│   ├── research/                  # Research and analysis
│   ├── backtests/                 # Backtest analysis
│   └── tutorials/                 # Tutorials
│
├── scripts/                       # Utility scripts
│   ├── setup/                     # Setup scripts
│   ├── data/                      # Data download scripts
│   └── deployment/                # Deployment scripts
│
├── data/                          # Data directory (gitignored)
│   ├── raw/                       # Raw market data
│   ├── processed/                 # Processed features
│   └── models/                    # Trained models
│
├── pyproject.toml                 # Project dependencies (Poetry)
├── requirements.txt               # Pip requirements
├── docker-compose.yml             # Docker setup
├── Dockerfile                     # Docker image
└── .env.example                   # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, recommended)
- Poetry (for dependency management)

### Installation

```bash
# Clone the repository
cd /Users/adii/Builds/Algo-Trading/QuantX

# Install dependencies using Poetry
poetry install

# Or using pip
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

### Run Your First Backtest

```python
from quantx.strategies import MACrossoverStrategy
from quantx.backtesting import BacktestEngine
from quantx.data import YahooFinanceProvider

# Create a simple moving average crossover strategy
strategy = MACrossoverStrategy(
    fast_period=50,
    slow_period=200
)

# Initialize backtest engine
engine = BacktestEngine(
    strategy=strategy,
    data_provider=YahooFinanceProvider(),
    initial_capital=100000,
    start_date="2020-01-01",
    end_date="2024-01-01"
)

# Run backtest
results = engine.run()

# Display results
results.plot()
results.print_summary()
```

## 🧠 Strategy Development

### Rule-Based Strategy Example

```python
from quantx.strategies.base import RuleBasedStrategy
from quantx.utils.indicators import SMA, RSI

class MyRuleBasedStrategy(RuleBasedStrategy):
    def __init__(self, rsi_period=14, rsi_oversold=30, rsi_overbought=70):
        super().__init__()
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def on_data(self, data):
        # Calculate indicators
        rsi = RSI(data.close, self.rsi_period)
        
        # Generate signals
        if rsi < self.rsi_oversold and not self.has_position():
            self.buy(size=1000)
        elif rsi > self.rsi_overbought and self.has_position():
            self.sell_all()
```

### AI-Powered Strategy Example

```python
from quantx.strategies.base import AIPoweredStrategy
from quantx.ml.models import LSTMPredictor

class MyAIStrategy(AIPoweredStrategy):
    def __init__(self, model_path):
        super().__init__()
        self.model = LSTMPredictor.load(model_path)
    
    def on_data(self, data):
        # Prepare features
        features = self.prepare_features(data)
        
        # Get prediction
        prediction = self.model.predict(features)
        
        # Generate signals based on prediction
        if prediction > 0.6 and not self.has_position():
            self.buy(size=1000)
        elif prediction < 0.4 and self.has_position():
            self.sell_all()
```

### Hybrid Strategy Example

```python
from quantx.strategies.base import HybridStrategy
from quantx.utils.indicators import RSI, MACD

class MyHybridStrategy(HybridStrategy):
    def __init__(self, model_path):
        super().__init__()
        self.model = LSTMPredictor.load(model_path)
    
    def on_data(self, data):
        # AI prediction
        ai_signal = self.model.predict(self.prepare_features(data))
        
        # Rule-based filters
        rsi = RSI(data.close, 14)
        macd, signal = MACD(data.close)
        
        # Combine signals
        if ai_signal > 0.7 and rsi < 70 and macd > signal:
            self.buy(size=1000)
        elif ai_signal < 0.3 or rsi > 80:
            self.sell_all()
```

## 📊 Design Principles

### 1. **Modularity**
Each component is self-contained and can be replaced independently.

### 2. **Extensibility**
New strategies, data sources, or brokers can be added via plugins.

### 3. **Separation of Concerns**
Clear boundaries between data, strategy, execution, and monitoring layers.

### 4. **SOLID Principles**
- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

### 5. **Event-Driven Architecture**
Asynchronous, loosely-coupled components communicating via events.

### 6. **Testability**
Every component is unit-testable with clear interfaces.

## 📚 Documentation

- [Product Requirements Document](docs/PRD.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/api/README.md)
- [Developer Guide](docs/guides/DEVELOPER_GUIDE.md)
- [User Guide](docs/guides/USER_GUIDE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=quantx --cov-report=html
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t quantx:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🛣️ Roadmap

### Phase 1: Foundation (Current)
- [x] Project structure
- [ ] Core event system
- [ ] Configuration management
- [ ] Data layer abstraction
- [ ] Basic backtesting engine

### Phase 2: Strategy Framework
- [ ] Rule-based strategy interface
- [ ] AI strategy interface
- [ ] Hybrid strategy combiner
- [ ] Strategy registry
- [ ] Example strategies

### Phase 3: ML Integration
- [ ] Feature engineering pipeline
- [ ] Model training framework
- [ ] Model evaluation tools
- [ ] Model versioning
- [ ] Pre-trained models

### Phase 4: Live Trading
- [ ] Broker integrations
- [ ] Order management
- [ ] Risk controls
- [ ] Paper trading mode
- [ ] Real-time monitoring

### Phase 5: Advanced Features
- [ ] Options trading support
- [ ] Multi-asset portfolio optimization
- [ ] Reinforcement learning agents
- [ ] Distributed backtesting
- [ ] Web dashboard

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

QuantX is inspired by and builds upon concepts from:
- **freqtrade**: Production-ready architecture and broker integrations
- **machine-learning-for-trading**: Comprehensive ML techniques
- **Stockformer**: Modern deep learning approaches
- **SWING_TRADING_WQU**: Custom backtesting infrastructure

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/quantx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/quantx/discussions)
- **Email**: support@quantx.io

---

**⚠️ Disclaimer**: This software is for educational and research purposes. Trading involves substantial risk of loss. Always test strategies thoroughly before deploying with real capital.
