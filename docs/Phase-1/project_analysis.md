# Algorithmic Trading Projects Analysis

## Overview

This directory contains **4 distinct algorithmic trading projects**, each with different approaches, technologies, and use cases. Below is a comprehensive analysis of each project.

---

## Project 1: SWING_TRADING_WQU

### 📋 Summary
A **World Quant University Capstone Project** focused on swing trading strategies using technical analysis and machine learning for short to intermediate-term trading (5 minutes to 1 week holding periods).

### 🎯 Objectives
- Systematic approach to creating swing trading strategies
- Generate Entry, Stop Loss, Target, and Maximum Holding Period signals
- Test strategies appropriate for different market conditions (trending vs. range-bound)
- Identify hidden patterns using ML for profitable trades

### 🏗️ Architecture

**Three Main Components:**

1. **Technical Analysis & Feature Matrix Creation**
   - Processes OHLCV data at multiple timeframes (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)
   - Adds comprehensive technical indicators
   - Normalizes data for ML input

2. **Backtesting Infrastructure**
   - Custom `Portfolio` class ([portfolio/portfolio.py](file:///Users/adii/Builds/Algo-Trading/SWING_TRADING_WQU/portfolio/portfolio.py))
   - Custom `Order` class ([order/order.py](file:///Users/adii/Builds/Algo-Trading/SWING_TRADING_WQU/order/order.py))
   - Commission tracking for accurate profitability
   - Statistics generation (hit rate, mean holding period, etc.)

3. **ML Strategy Improvement**
   - Uses ML to identify hidden patterns
   - Improves trading strategy parameters

### 📊 Data Sources
- **Market**: NSE (National Stock Exchange of India)
- **Instruments**: 150 stocks + Nifty50 index
- **Training Data**: 28-11-2018 to 29-03-2019 (1-minute DOHLCV)
- **Test Data**: 01-10-2019 to 11-11-2019
- **Historical**: Last 5 years EOD data

### 🛠️ Technology Stack
```
numpy==1.16.3
pandas==0.24.2
talib==0.4.17
sklearn==0.20.3
matplotlib==0.20.3
mpl_finance
```

### 📁 Directory Structure
```
SWING_TRADING_WQU/
├── data_processing/     # Data preprocessing and feature engineering
├── indicators/          # Technical indicator implementations
├── ml/                  # Machine learning models (30 files)
├── portfolio/           # Portfolio management class
├── order/               # Order execution class
├── strategy/            # Trading strategies
├── examples/            # Usage examples
├── raw_data/            # Raw market data (184 files)
└── consolidated_data/   # Processed data
```

### ⚠️ Status
- **Age**: Older project (2020)
- **Dependencies**: Outdated versions (Python likely 3.6-3.7)
- **Maintenance**: Academic project, may not be actively maintained

---

## Project 2: Stockformer

### 📋 Summary
Implementation of **"StockFormer: A Swing Trading Strategy Based on STL Decomposition and Self-Attention Networks"** - a research paper under consideration for publication in the International Journal of Forecasting.

### 🎯 Objectives
- Apply self-attention networks (Transformer architecture) to stock trading
- Use STL (Seasonal and Trend decomposition using Loess) for time series decomposition
- Generate trading signals for swing trading strategies

### 🏗️ Architecture

**Key Components:**

1. **Neural Network Model** ([Stockformermodel/](file:///Users/adii/Builds/Algo-Trading/Stockformer/Stockformermodel/))
   - Self-attention based architecture
   - Processes decomposed time series data
   - Generates trading signals

2. **Data Processing**
   - Raw data cleaning ([data_cleaned.ipynb](file:///Users/adii/Builds/Algo-Trading/Stockformer/data_cleaned.ipynb))
   - Correlation matrix generation
   - Struc2vec for high-dimensional vector embeddings

3. **Backtesting Framework** ([backtest/](file:///Users/adii/Builds/Algo-Trading/Stockformer/backtest/))
   - Built on [qlib](https://github.com/microsoft/qlib) framework
   - US market data (2021-2023)
   - SOTA baseline comparisons

### 📊 Data Structure
```
data/STOCK/
├── corr_adj.npy              # Correlation matrix
├── corr_struc2vec_adjgat.npy # High-dimensional vectors (Struc2vec)
└── flow.npz                  # Processed input data
```

### 🛠️ Technology Stack
- **Deep Learning**: PyTorch/TensorFlow (likely)
- **Graph Embeddings**: Struc2vec
- **Backtesting**: qlib (Microsoft's quantitative investment platform)
- **Data Processing**: NumPy, pandas

### 📖 Research Paper
- **SSRN**: https://ssrn.com/abstract=4648073
- **Focus**: Swing trading with self-attention networks
- **Innovation**: Combines STL decomposition with Transformer architecture

### 🚀 Usage
```bash
python Stockformer_train.py --config STOCKV4.conf
```

### 📁 Directory Structure
```
Stockformer/
├── Stockformermodel/    # Neural network architecture
├── data/STOCK/          # Processed data files
├── backtest/            # Backtesting code and data (3031 files)
├── lib/                 # Utility functions
├── config/              # Configuration files
├── cpt/STOCK/           # Saved model checkpoints
├── log/STOCK/           # Training logs
└── output/              # Results
```

### ⚠️ Status
- **Age**: Recent (2023-2024)
- **Type**: Research implementation
- **Paper**: Under review
- **Maintenance**: Active research project

---

## Project 3: freqtrade

### 📋 Summary
**Production-ready, open-source crypto trading bot** written in Python. Supports all major exchanges, controlled via Telegram or WebUI, with comprehensive backtesting, plotting, and money management tools.

### 🎯 Objectives
- Automated cryptocurrency trading
- Strategy optimization using machine learning
- Risk management and portfolio tracking
- Multi-exchange support

### 🏗️ Architecture

**Enterprise-Grade Features:**

1. **Trading Engine**
   - Event-driven architecture
   - Real-time trade execution
   - Dry-run mode for testing
   - Persistence via SQLite

2. **Strategy Framework**
   - Custom strategy development
   - Built-in technical indicators
   - FreqAI: Adaptive ML prediction modeling
   - Strategy optimization via hyperparameter tuning

3. **User Interfaces**
   - Built-in WebUI
   - Telegram bot integration
   - REST API
   - Command-line interface

4. **Analysis Tools**
   - Backtesting engine
   - Performance analytics
   - Profit/loss tracking in fiat
   - Plot generation

### 🔌 Supported Exchanges

**Spot Trading:**
- Binance, BingX, Bitget, Bitmart, Bybit
- Gate.io, HTX, Hyperliquid (DEX)
- Kraken, OKX, MyOKX
- Many others via CCXT

**Futures Trading (Experimental):**
- Binance, Bitget, Gate.io
- Hyperliquid, OKX, Bybit

### 🛠️ Technology Stack
```
Python >= 3.11
numpy==2.3.5
pandas==2.3.3
ccxt==4.5.20              # Exchange connectivity
SQLAlchemy==2.0.44        # Database ORM
fastapi==0.121.3          # REST API
python-telegram-bot==22.5 # Telegram integration
ta-lib==0.6.8             # Technical analysis
ft-pandas-ta==0.3.16      # Additional indicators
```

### 📊 Key Features
- ✅ **FreqAI**: Self-training ML models that adapt to market conditions
- ✅ **Backtesting**: Simulate strategies on historical data
- ✅ **Hyperopt**: ML-based strategy parameter optimization
- ✅ **WebUI**: Modern web interface for bot management
- ✅ **Telegram**: Remote bot control and notifications
- ✅ **Docker**: Containerized deployment
- ✅ **Multi-timeframe**: Support for various trading timeframes

### 🚀 Usage Examples

**Basic Commands:**
```bash
freqtrade trade                    # Start trading
freqtrade backtesting             # Run backtest
freqtrade hyperopt                # Optimize strategy
freqtrade download-data           # Download market data
freqtrade plot-dataframe          # Visualize indicators
freqtrade webserver               # Start web interface
```

**Telegram Commands:**
- `/start` - Start the trader
- `/stop` - Stop the trader
- `/status` - View open trades
- `/profit` - Show cumulative profit
- `/balance` - Account balance
- `/forceexit` - Close trades manually

### 📁 Directory Structure
```
freqtrade/
├── freqtrade/           # Core bot code (350 files)
├── ft_client/           # API client
├── user_data/           # User strategies and data
├── tests/               # Test suite (188 files)
├── docs/                # Documentation (99 files)
├── docker/              # Docker configurations
├── config_examples/     # Example configurations
└── build_helpers/       # Build scripts
```

### ⚠️ Status
- **Maturity**: Production-ready
- **Community**: Very active (Discord, GitHub)
- **Documentation**: Comprehensive (https://www.freqtrade.io)
- **CI/CD**: Automated testing and deployment
- **License**: Open source
- **Updates**: Actively maintained

### 💡 Use Cases
- Automated crypto trading
- Strategy development and testing
- Portfolio management
- Market making
- Arbitrage opportunities

---

## Project 4: machine-learning-for-trading

### 📋 Summary
Comprehensive **educational resource** accompanying the book **"Machine Learning for Algorithmic Trading - 2nd Edition"** by Stefan Jansen. Contains **150+ Jupyter notebooks** demonstrating ML techniques for trading across **23 chapters + appendix** on **800+ pages**.

### 🎯 Objectives
- Teach ML applications in algorithmic trading
- Demonstrate end-to-end ML4T workflow
- Cover data sourcing, feature engineering, model building, backtesting
- Replicate recent academic research

### 🏗️ Architecture

**Four Main Parts:**

### Part 1: Data to Strategy Development
1. **ML for Trading Overview** ([01_machine_learning_for_trading](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/01_machine_learning_for_trading/))
2. **Market & Fundamental Data** ([02_market_and_fundamental_data](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/02_market_and_fundamental_data/))
   - NASDAQ ITCH tick data
   - Algoseek minute bars
   - SEC XBRL filings
3. **Alternative Data** ([03_alternative_data](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/03_alternative_data/))
   - Web scraping
   - Earnings call transcripts
   - Satellite imagery
4. **Alpha Factor Research** ([04_alpha_factor_research](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/04_alpha_factor_research/))
   - Factor creation with NumPy, pandas, TA-Lib
   - Wavelets and Kalman filters
   - Alphalens evaluation
5. **Portfolio Optimization** ([05_strategy_evaluation](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/05_strategy_evaluation/))
   - Mean-variance optimization
   - Pyfolio performance evaluation

### Part 2: ML Fundamentals
6. **ML Process** ([06_machine_learning_process](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/06_machine_learning_process/))
7. **Linear Models** ([07_linear_models](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/07_linear_models/))
8. **ML4T Workflow** ([08_ml4t_workflow](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/08_ml4t_workflow/))
   - Zipline backtesting
   - Backtrader integration
9. **Time Series Models** ([09_time_series_models](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/09_time_series_models/))
   - ARIMA, GARCH
   - Pairs trading with cointegration
10. **Bayesian ML** ([10_bayesian_machine_learning](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/10_bayesian_machine_learning/))
    - PyMC3 probabilistic programming
11. **Random Forests** ([11_decision_trees_random_forests](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/11_decision_trees_random_forests/))
    - Long-short strategy for Japanese stocks
12. **Gradient Boosting** ([12_gradient_boosting_machines](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/12_gradient_boosting_machines/))
    - XGBoost, LightGBM, CatBoost
    - Intraday strategy with minute data
13. **Unsupervised Learning** ([13_unsupervised_learning](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/13_unsupervised_learning/))
    - PCA, ICA for risk factors
    - Hierarchical risk parity

### Part 3: NLP for Trading
14. **Sentiment Analysis** ([14_working_with_text_data](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/14_working_with_text_data/))
    - spaCy, TextBlob
    - Naive Bayes classification
15. **Topic Modeling** ([15_topic_modeling](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/15_topic_modeling/))
    - LSI, pLSA, LDA
    - Earnings calls analysis
16. **Word Embeddings** ([16_word_embeddings](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/16_word_embeddings/))
    - Word2vec, doc2vec
    - BERT fine-tuning on SEC filings

### Part 4: Deep & Reinforcement Learning
17. **Deep Learning** ([17_deep_learning](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/17_deep_learning/))
    - TensorFlow 2, PyTorch
    - Feedforward networks
18. **CNNs** ([18_convolutional_neural_nets](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/18_convolutional_neural_nets/))
    - Time series as images
    - Satellite image classification
19. **RNNs** ([19_recurrent_neural_nets](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/19_recurrent_neural_nets/))
    - LSTM, GRU
    - Sentiment analysis
20. **Autoencoders** ([20_autoencoders_for_conditional_risk_factors](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/20_autoencoders_for_conditional_risk_factors/))
    - Replicates AQR research paper
    - Conditional risk factors
21. **GANs** ([21_gans_for_synthetic_time_series](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/21_gans_for_synthetic_time_series/))
    - Synthetic time series generation
    - Replicates NeurIPS 2019 paper
22. **Deep RL** ([22_deep_reinforcement_learning](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/22_deep_reinforcement_learning/))
    - Q-learning
    - Trading agent with OpenAI Gym
23. **Conclusions** ([23_next_steps](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/23_next_steps/))
24. **Alpha Factor Library** ([24_alpha_factor_library](file:///Users/adii/Builds/Algo-Trading/machine-learning-for-trading/24_alpha_factor_library/))
    - 100+ alpha factors
    - WorldQuant's 101 Formulaic Alphas

### 🛠️ Technology Stack
```
Python >= 3.8
pandas >= 1.2
TensorFlow >= 2.2
PyTorch
scikit-learn
zipline-reloaded        # Backtesting
pyfolio-reloaded        # Performance analysis
alphalens-reloaded      # Factor analysis
ta-lib                  # Technical indicators
PyMC3                   # Bayesian ML
XGBoost, LightGBM, CatBoost
spaCy, TextBlob         # NLP
OpenAI Gym              # RL environments
```

### 📊 Data Sources
- Market data (US equities, international stocks, ETFs)
- Minute-frequency equity data (Algoseek)
- SEC filings (EDGAR)
- Earnings call transcripts
- Financial news
- Satellite images
- Alternative data sources

### 📖 Book Information
- **Title**: Machine Learning for Algorithmic Trading - 2nd Edition
- **Author**: Stefan Jansen
- **Publisher**: Packt
- **Amazon**: [Link](https://www.amazon.com/Machine-Learning-Algorithmic-Trading-alternative/dp/1839217715)
- **Website**: ml4trading.io
- **Community**: [ML4T Exchange](https://exchange.ml4trading.io/)

### 📁 Directory Structure
```
machine-learning-for-trading/
├── 01_machine_learning_for_trading/
├── 02_market_and_fundamental_data/
├── 03_alternative_data/
├── 04_alpha_factor_research/
├── 05_strategy_evaluation/
├── 06_machine_learning_process/
├── 07_linear_models/
├── 08_ml4t_workflow/
├── 09_time_series_models/
├── 10_bayesian_machine_learning/
├── 11_decision_trees_random_forests/
├── 12_gradient_boosting_machines/
├── 13_unsupervised_learning/
├── 14_working_with_text_data/
├── 15_topic_modeling/
├── 16_word_embeddings/
├── 17_deep_learning/
├── 18_convolutional_neural_nets/
├── 19_recurrent_neural_nets/
├── 20_autoencoders_for_conditional_risk_factors/
├── 21_gans_for_synthetic_time_series/
├── 22_deep_reinforcement_learning/
├── 23_next_steps/
├── 24_alpha_factor_library/
├── data/                # Shared data files
├── installation/        # Setup instructions
└── figures/             # Book figures
```

### ⚠️ Status
- **Type**: Educational/Tutorial
- **Maturity**: Well-maintained
- **Updates**: Active (2nd edition released)
- **Community**: Active forum and exchange
- **Purpose**: Learning resource, not production trading

### 💡 Key Innovations
- Replicates recent academic research papers
- End-to-end ML4T workflow
- Custom Zipline version for ML integration
- Comprehensive coverage of modern ML techniques

---

## 📊 Comparative Analysis

| Feature | SWING_TRADING_WQU | Stockformer | freqtrade | ML-for-Trading |
|---------|-------------------|-------------|-----------|----------------|
| **Type** | Academic Project | Research Implementation | Production Bot | Educational Resource |
| **Market** | Indian Equities (NSE) | US Stocks | Cryptocurrency | Multi-asset |
| **Strategy** | Swing Trading | Swing Trading | Various | Various |
| **ML Focus** | Traditional ML | Deep Learning (Transformers) | FreqAI (Adaptive ML) | Comprehensive ML |
| **Timeframe** | 5min - 1 week | Swing (days) | Minutes - Days | Tick - Daily |
| **Backtesting** | Custom | qlib | Built-in | Zipline/Backtrader |
| **Maturity** | Older (2020) | Recent (2023-24) | Production-ready | Well-maintained |
| **Dependencies** | Outdated | Modern | Latest | Modern |
| **Use Case** | Learning/Research | Research | Live Trading | Learning |
| **Documentation** | Minimal | Research Paper | Extensive | Book + Notebooks |
| **Community** | Academic | Research | Very Active | Active |

---

## 🎯 Recommendations by Use Case

### 1. **Learning ML for Trading**
→ **machine-learning-for-trading**
- Most comprehensive educational resource
- 150+ notebooks with detailed explanations
- Covers entire spectrum of ML techniques
- Well-documented and maintained

### 2. **Live Crypto Trading**
→ **freqtrade**
- Production-ready with active community
- Multi-exchange support
- Built-in risk management
- WebUI and Telegram integration
- Extensive documentation

### 3. **Research & Experimentation**
→ **Stockformer** or **SWING_TRADING_WQU**
- Stockformer: Modern deep learning approach
- SWING_TRADING_WQU: Traditional ML with custom infrastructure
- Both provide good starting points for research

### 4. **Building Custom Trading System**
→ **Combine approaches:**
- Use **freqtrade** architecture as foundation
- Apply **ML-for-Trading** techniques for strategy development
- Incorporate **Stockformer** deep learning models
- Adapt **SWING_TRADING_WQU** backtesting infrastructure

---

## 🔧 Technical Debt & Modernization Needs

### SWING_TRADING_WQU
- ⚠️ Outdated dependencies (Python 3.6-3.7 era)
- ⚠️ No Docker support
- ⚠️ Limited documentation
- ✅ Good: Custom backtesting infrastructure

### Stockformer
- ✅ Modern deep learning approach
- ⚠️ Large data files on cloud (not included)
- ⚠️ Research code (may need refactoring for production)
- ✅ Good: Based on recent research

### freqtrade
- ✅ Production-ready
- ✅ Modern dependencies
- ✅ Docker support
- ✅ Active maintenance
- ✅ Comprehensive testing

### machine-learning-for-trading
- ✅ Well-maintained
- ✅ Modern stack (Python 3.8+, TF 2.2+)
- ⚠️ Educational focus (not production-ready)
- ✅ Excellent documentation

---

## 🚀 Next Steps

1. **For Learning**: Start with **machine-learning-for-trading** chapters 1-8
2. **For Trading**: Set up **freqtrade** with paper trading
3. **For Research**: Explore **Stockformer** architecture and **SWING_TRADING_WQU** backtesting
4. **For Production**: Build on **freqtrade** with custom strategies from other projects

---

## 📚 Additional Resources

- **freqtrade**: https://www.freqtrade.io
- **ML4T Book**: https://ml4trading.io
- **Stockformer Paper**: https://ssrn.com/abstract=4648073
- **ML4T Community**: https://exchange.ml4trading.io/
- **freqtrade Discord**: https://discord.gg/p7nuUNVfP7
