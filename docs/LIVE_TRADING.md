# QuantX Live Trading Guide

**Complete guide for live trading with QuantX on Indian markets (NSE/BSE)**

---

## 🎯 Overview

QuantX provides a complete live trading platform with:
- Real-time data streaming (WebSocket)
- Automated strategy execution
- Risk management
- Position synchronization
- Live P&L tracking

---

## 🚀 Quick Start

### 1. Authenticate with Zerodha

```bash
cd /Users/adii/Builds/Algo-Trading/QuantX
PYTHONPATH="$(pwd)/src" python examples/live/zerodha_authentication.py
```

Choose option 4 for interactive authentication flow.

### 2. Run Complete Live Trading Example

```bash
PYTHONPATH="$(pwd)/src" python examples/live/complete_live_trading.py
```

This runs a complete MA Crossover strategy with:
- Real-time WebSocket data
- Automated order execution
- Risk limits
- Live monitoring

---

## 📋 PrerequisitesFor Live Trading

### Account Requirements
- ✅ Active Zerodha Demat account
- ✅ Sufficient funds/margin
- ✅ 2FA (TOTP) enabled
- ✅ API access from kite.trade

### Technical Requirements
- ✅ Python 3.11+
- ✅ QuantX installed
- ✅ kiteconnect package (`pip install kiteconnect`)
- ✅ Valid access token (24h validity)

### Market Requirements
- ✅ Trading during market hours (9:15 AM - 3:30 PM IST)
- ✅ Network connectivity
- ✅ System resources for real-time processing

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Your Strategy                      │
│         (MA Crossover, ML-based, etc.)              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│            LiveExecutionEngine                       │
│  • Position Sync (60s)                              │
│  • Heartbeat Monitor (10s)                          │
│  • Event Processing                                  │
└────┬─────────────┬───────────────┬───────────────────┘
     │             │               │
     ▼             ▼               ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐
│LiveData │  │  OMS +   │  │   Zerodha    │
│Provider │  │   Risk   │  │    Broker    │
└────┬────┘  └────┬─────┘  └──────┬───────┘
     │            │                │
     └────────────┴────────────────┘
                  │
            ┌─────▼──────┐
            │ EventBus   │
            └────────────┘
```

---

## 💻 Code Structure

### Complete Live Trading Setup

```python
# 1. Setup infrastructure
event_bus = EventBus()
event_bus.start()

# 2. Connect to broker
broker = ZerodhaBroker("zerodha", session_config)
broker.connect()

# 3. Setup live data
manager = InstrumentManager(broker)
manager.load_instruments(exchange="NSE")

live_data = LiveDataProvider(
    api_key, access_token, event_bus,
    instrument_lookup=manager._symbol_to_token
)

# 4. Create strategy
strategy = YourStrategy("my_strategy", config)

# 5. Setup OMS and risk
oms = OrderManager(broker, event_bus)
risk = RiskManager(limits=RiskLimits(...))
oms.set_risk_manager(risk)

# 6. Create execution engine
engine = LiveExecutionEngine(
    strategy, broker, oms, risk, event_bus
)

# 7. Start everything
live_data.connect()
live_data.subscribe_symbols(symbols, mode="quote")
engine.start()

# 8. Monitor
while engine.state == EngineState.RUNNING:
    stats = engine.get_statistics()
    # ... display stats ...
    time.sleep(10)

# 9. Shutdown
engine.stop()
live_data.disconnect()
```

---

## 🛡️ Risk Management

### Configure Risk Limits

```python
risk_limits = RiskLimits(
    max_position_size_pct=0.10,    # Max 10% per position
    max_daily_loss=5000.0,          # Max ₹5,000 daily loss
    max_drawdown_pct=0.05,          # Max 5% drawdown
    max_open_positions=5            # Max 5 concurrent positions
)

risk_manager = RiskManager(limits=risk_limits)
```

### Safety Features

- **Pre-trade checks**: Every order validated before submission
- **Position limits**: Automatic rejection of oversized orders
- **Daily loss limit**: Auto-pause on reaching loss threshold
- **Drawdown protection**: Kill switch on excessive drawdown
- **Kill switch**: Emergency stop for all trading

---

## 📊 Monitoring

### Real-Time Statistics

```python
stats = engine.get_statistics()

# Engine stats
print(f"Uptime: {stats['engine']['uptime']}s")
print(f"Signals: {stats['engine']['signals_received']}")
print(f"Orders: {stats['engine']['orders_filled']}")

# Account stats
print(f"Equity: ₹{stats['account']['equity']:,.2f}")
print(f"P&L: ₹{stats['account']['total_pnl']:+,.2f}")

# Position stats
print(f"Positions: {stats['positions']['count']}")

# Risk stats
print(f"Daily P&L: ₹{stats['risk']['daily_pnl']:+,.2f}")
```

### WebSocket Statistics

```python
ws_stats = live_data.get_statistics()

print(f"Ticks received: {ws_stats['ticks_received']}")
print(f"Connected: {ws_stats['connected']}")
print(f"Uptime: {ws_stats['uptime_seconds']}s")
```

---

## 🎯 Strategy Development

### Create Custom Live Strategy

```python
from quantx.strategies.base import RuleBasedStrategy
from quantx.core.events import EventType

class MyLiveStrategy(RuleBasedStrategy):
    def __init__(self, name, config):
        super().__init__(name, config)
        # Your initialization
    
    def on_data(self, event):
        """Process real-time tick data."""
        if event.event_type != EventType.TICK:
            return
        
        data = event.data
        price = data.get('last_price')
        symbol = data.get('symbol')
        
        # Your trading logic
        if self.should_buy(symbol, price):
            self.buy(symbol, quantity=1)
        elif self.should_sell(symbol, price):
            self.sell(symbol, quantity=self.get_position(symbol))
    
    def on_fill(self, event):
        """Handle order fills."""
        fill_data = event.data
        # Update your internal state
```

---

## 🔧 Configuration

### Engine Configuration

```python
engine_config = EngineConfig(
    position_sync_interval=60,   # Seconds
    heartbeat_interval=10,       # Seconds
    max_reconnect_attempts=5,
    reconnect_delay=5,
    dry_run=False  # Set True for testing
)
```

### Data Streaming Configuration

```python
# Tick modes
MODE_LTP = "ltp"      # Last price only
MODE_QUOTE = "quote"  # LTP + volume + bid/ask
MODE_FULL = "full"    # Full market depth

# Subscribe
live_data.subscribe_symbols(
    ["NSE:INFY", "NSE:TCS"],
    mode="quote"  # Choose mode
)
```

---

## ⚠️ Best Practices

### 1. Testing
- ✅ **Always test in paper mode first**
- ✅ Start with small positions (1-2 shares)
- ✅ Test during market hours
- ✅ Monitor for at least a few hours

### 2. Risk Management
- ✅ Set conservative limits initially
- ✅ Use stop-loss orders
- ✅ Never risk more than 2% per trade
- ✅ Have maximum daily loss limit

### 3. Monitoring
- ✅ Monitor positions continuously
- ✅ Check system logs regularly
- ✅ Have alerts for errors
- ✅ Keep manual override ready

### 4. Operational
- ✅ Renew access token daily
- ✅ Check account before trading
- ✅ Ensure sufficient margin
- ✅ Have backup connectivity

---

## 🐛 Troubleshooting

### Issue: "Not connected to broker"
**Solution**: Ensure access token is valid (24h validity). Re-authenticate.

### Issue: "WebSocket disconnected"
**Solution**: Check network. System auto-reconnects (5 attempts).

### Issue: "Order rejected"
**Solution**: Check:
- Sufficient margin/cash
- Valid symbol format
- Market hours
- Risk limits not breached

### Issue: "No ticks received"
**Solution**:
- Confirm market hours (9:15 AM - 3:30 PM IST)
- Check WebSocket connection
- Verify symbol subscriptions

### Issue: "Position mismatch"
**Solution**: Position sync runs every 60s. Wait for next sync or force sync.

---

## 📈 Performance

### Expected Performance
- **Latency**: < 50ms tick-to-event
- **Throughput**: 1000+ ticks/second
- **Memory**: ~ 100-200 MB
- **CPU**: Low (< 10% on modern systems)

### Optimization Tips
- Use `MODE_LTP` for simple strategies (less data)
- Limit number of subscribed symbols
- Use appropriate sync intervals
- Clean up old logs regularly

---

## 📚 Examples

### 1. Simple Live Trading
```bash
python examples/live/complete_live_trading.py
```

### 2. WebSocket Streaming Only
```bash
python examples/live/zerodha_websocket_streaming.py
```

### 3. Manual Trading (No Engine)
```bash
python examples/live/zerodha_trading.py
```

### 4. Authentication
```bash
python examples/live/zerodha_authentication.py
```

---

## ✅ Checklist Before Going Live

- [ ] Zerodha account funded
- [ ] API credentials obtained
- [ ] Access token generated (< 24h old)
- [ ] Strategy backtested
- [ ] Paper trading successful
- [ ] Risk limits configured
- [ ] Small position sizes for first trades
- [ ] Monitoring system ready
- [ ] understand all fees/charges
- [ ] Emergency stop plan ready

---

## 🆘 Support

### Documentation
- [Setup Guide](.../ZERODHA_SETUP.md)
- [Phase 3 Walkthrough](.../walkthrough.md)
- [Example Code](../examples/live/)

### Logs
- Check `live_trading_*.log` for detailed logs
- Debug mode: Set logger level to DEBUG

### Emergency Stop
- Press `Ctrl+C` to stop gracefully
- Or call `engine.stop()` programmatically

---

## 📝 Notes

- Access tokens expire after 24 hours
- WebSocket auto-reconnects on disconnection
- Position sync runs every 60 seconds
- All orders go through risk checks
- System logs everything for audit

---

**Status**: Production Ready  
**Supported Markets**: NSE, BSE, NFO, CDS, MCX  
**Broker**: Zerodha (Kite Connect)  
**Mode**: Live Trading 🇮🇳
