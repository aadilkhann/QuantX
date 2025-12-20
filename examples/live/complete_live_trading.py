"""
Complete Live Trading Example with Zerodha.

Demonstrates end-to-end live trading combining:
- LiveExecutionEngine
- ZerodhaBroker  
- WebSocket streaming
- Real-time strategy execution
- Position and risk management
- Live P&L tracking
"""

import sys
from pathlib import Path
import json
import time
from datetime import datetime
import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from loguru import logger

from quantx.core.events import EventBus, EventType
from quantx.core.config import Config
from quantx.execution import (
    ZerodhaBroker,
    OrderManager,
    RiskManager,
    RiskLimits,
    LiveExecutionEngine,
    EngineConfig,
    EngineState
)
from quantx.data import LiveDataProvider, InstrumentManager
from quantx.strategies.base import RuleBasedStrategy, Signal, Action


def setup_logging():
    """Setup logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Also log to file
    logger.add(
        "live_trading_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )


def load_session(filename: str = "zerodha_session.json") -> dict:
    """Load saved Zerodha session."""
    filepath = Path(__file__).parent / filename
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


class LiveMAStrategy(RuleBasedStrategy):
    """
    Live Moving Average Crossover Strategy.
    
    Generates signals based on real-time price data using
    simple moving average crossover logic.
    """
    
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        
        self.fast_period = config.get("fast_period", 5)
        self.slow_period = config.get("slow_period", 10)
        self.symbols = config.get("symbols", [])
        
        # Price buffers for MA calculation
        self._price_buffers = {symbol: [] for symbol in self.symbols}
        
        logger.info(f"LiveMAStrategy initialized: fast={self.fast_period}, slow={self.slow_period}")
    
    def on_data(self, event):
        """Process market data tick."""
        if event.event_type != EventType.TICK:
            return
        
        data = event.data
        token = data.get('instrument_token')
        price = data.get('last_price')
        
        if not price:
            return
        
        # Find symbol for this token
        symbol = None
        for sym in self.symbols:
            # Match by token or symbol in event data
            if str(token) in str(sym) or sym in str(data):
                symbol = sym
                break
        
        if not symbol or symbol not in self._price_buffers:
            return
        
        # Update price buffer
        buffer = self._price_buffers[symbol]
        buffer.append(price)
        
        # Keep only what we need
        max_period = max(self.fast_period, self.slow_period)
        if len(buffer) > max_period:
            buffer.pop(0)
        
        # Need enough data for slow MA
        if len(buffer) < self.slow_period:
            return
        
        # Calculate MAs
        fast_ma = sum(buffer[-self.fast_period:]) / self.fast_period
        slow_ma = sum(buffer[-self.slow_period:]) / self.slow_period
        
        # Check for crossover
        current_position = self.get_position(symbol)
        
        # Buy signal: fast MA crosses above slow MA
        if fast_ma > slow_ma and current_position == 0:
            logger.info(f"📈 BUY signal for {symbol}: fast_ma={fast_ma:.2f} > slow_ma={slow_ma:.2f}")
            self.buy(symbol, quantity=1, metadata={"fast_ma": fast_ma, "slow_ma": slow_ma})
        
        # Sell signal: fast MA crosses below slow MA
        elif fast_ma < slow_ma and current_position > 0:
            logger.info(f"📉 SELL signal for {symbol}: fast_ma={fast_ma:.2f} < slow_ma={slow_ma:.2f}")
            self.sell(symbol, quantity=current_position, metadata={"fast_ma": fast_ma, "slow_ma": slow_ma})
    
    def on_fill(self, event):
        """Handle order fill."""
        fill_data = event.data
        symbol = fill_data.get('symbol', '')
        quantity = fill_data.get('quantity', 0)
        side = fill_data.get('side', '')
        
        logger.info(f"✅ Fill received: {side} {quantity} {symbol}")
        
        # Update position
        if side == "BUY":
            self.update_position(symbol, quantity)
        elif side == "SELL":
            self.update_position(symbol, -quantity)


def main():
    """Run complete live trading example."""
    setup_logging()
    
    print("\n" + "="*70)
    print(" " * 15 + "QuantX Live Trading - Complete Example")
    print("="*70 + "\n")
    
    # Load session
    print("📋 Loading Zerodha session...")
    session = load_session()
    if not session or "access_token" not in session:
        print("❌ No saved session found!")
        print("   Please run zerodha_authentication.py first to authenticate.")
        return
    
    print(f"✅ Session loaded for user: {session.get('user_id')}\n")
    
    # Warning
    print("⚠️  " + "="*66)
    print("⚠️  WARNING: This will execute LIVE TRADES on your Zerodha account!")
    print("⚠️  " + "="*66)
    print("\n   Recommendations:")
    print("   1. Test during market hours (9:15 AM - 3:30 PM IST)")
    print("   2. Use small quantities (1-2 shares)")
    print("   3. Monitor positions closely")
    print("   4. Have stop-loss limits configured\n")
    
    proceed = input("Do you want to proceed with LIVE trading? (type 'yes' to continue): ").strip().lower()
    if proceed != "yes":
        print("\n❌ Cancelled. Use paper trading mode for testing.")
        return
    
    print("\n🚀 Starting live trading system...\n")
    
    # =================================================================
    # SETUP
    # =================================================================
    
    # 1. Create event bus
    print("1️⃣  Creating event bus...")
    event_bus = EventBus()
    event_bus.start()
    print("   ✅ Event bus started\n")
    
    # 2. Create broker
    print("2️⃣  Connecting to Zerodha...")
    broker = ZerodhaBroker("zerodha", session)
    if not broker.connect():
        print("   ❌ Failed to connect to broker!")
        return
    print("   ✅ Connected to Zerodha\n")
    
    # 3. Load instruments
    print("3️⃣  Loading instrument tokens...")
    manager = InstrumentManager(broker)
    try:
        manager.load_instruments(exchange="NSE")
        print(f"   ✅ Loaded {len(manager._symbol_to_token)} instruments\n")
    except Exception as e:
        print(f"   ⚠️  Could not load instruments: {e}")
        print("   Using hardcoded tokens...\n")
        # Fallback to hardcoded tokens
        manager._symbol_to_token = {
            "NSE:INFY": 408065,
            "NSE:TCS": 2953217
        }
    
    # 4. Create live data provider
    print("4️⃣  Setting up live data stream...")
    live_data = LiveDataProvider(
        api_key=session["api_key"],
        access_token=session["access_token"],
        event_bus=event_bus,
        instrument_lookup=manager._symbol_to_token
    )
    print("   ✅ Live data provider ready\n")
    
    # 5. Create strategy
    print("5️⃣  Initializing trading strategy...")
    strategy_config = {
        "fast_period": 5,   # 5-tick fast MA
        "slow_period": 10,  # 10-tick slow MA
        "symbols": ["NSE:INFY", "NSE:TCS"]
    }
    strategy = LiveMAStrategy("live_ma_crossover", strategy_config)
    print(f"   ✅ Strategy: MA Crossover (fast=5, slow=10)")
    print(f"   ✅ Symbols: {strategy_config['symbols']}\n")
    
    # 6. Create OMS and Risk Manager
    print("6️⃣  Setting up risk management...")
    oms = OrderManager(broker, event_bus=event_bus)
    
    risk_limits = RiskLimits(
        max_position_size_pct=0.05,      # Max 5% per position
        max_daily_loss=2000.0,            # Max ₹2,000 daily loss
        max_drawdown_pct=0.03,           # Max 3% drawdown
        max_open_positions=2              # Max 2 positions
    )
    risk_manager = RiskManager(limits=risk_limits)
    oms.set_risk_manager(risk_manager)
    print(f"   ✅ Risk limits configured:")
    print(f"      - Max position size: 5%")
    print(f"      - Max daily loss: ₹2,000")
    print(f"      - Max drawdown: 3%")
    print(f"      - Max open positions: 2\n")
    
    # 7. Create live execution engine
    print("7️⃣  Creating live execution engine...")
    engine_config = EngineConfig(
        position_sync_interval=60,  # Sync every 60s
        heartbeat_interval=10,      # Heartbeat every 10s
        dry_run=False               # LIVE MODE!
    )
    
    engine = LiveExecutionEngine(
        strategy=strategy,
        broker=broker,
        order_manager=oms,
        risk_manager=risk_manager,
        event_bus=event_bus,
        config=engine_config
    )
    print("   ✅ Live execution engine created\n")
    
    # =================================================================
    # START TRADING
    # =================================================================
    
    print("="*70)
    print(" " * 25 + "STARTING LIVE TRADING")
    print("="*70 + "\n")
    
    # Start live data
    print("📡 Connecting to WebSocket...")
    live_data.connect()
    time.sleep(2)
    
    print("📡 Subscribing to live data...")
    live_data.subscribe_symbols(strategy_config['symbols'], mode="quote")
    print(f"   ✅ Subscribed to {len(strategy_config['symbols'])} symbols\n")
    
    # Start execution engine
    print("🚀 Starting live execution engine...")
    if not engine.start():
        print("❌ Failed to start engine!")
        live_data.disconnect()
        return
    
    print("\n" + "="*70)
    print("✅ LIVE TRADING ACTIVE!")
    print("="*70)
    print("\nSystem Status:")
    print("   🟢 WebSocket streaming: Active")
    print("   🟢 Execution engine: Running")
    print("   🟢 Risk management: Enabled")
    print("\nPress Ctrl+C to stop trading...\n")
    
    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutdown signal received...")
        raise KeyboardInterrupt()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # =================================================================
    # MONITORING LOOP
    # =================================================================
    
    try:
        iteration = 0
        while engine.state == EngineState.RUNNING:
            time.sleep(10)  # Update every 10 seconds
            iteration += 1
            
            # Get statistics
            stats = engine.get_statistics()
            ws_stats = live_data.get_statistics()
            
            # Display status
            print(f"\n{'='*70}")
            print(f"Status Update #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*70}")
            
            # Engine stats
            print(f"\n📊 Engine:")
            print(f"   State: {stats['engine']['state']}")
            print(f"   Uptime: {stats['engine']['uptime']:.0f}s")
            print(f"   Signals: {stats['engine']['signals_received']}")
            print(f"   Orders: {stats['engine']['orders_submitted']} submitted, "
                  f"{stats['engine']['orders_filled']} filled, "
                  f"{stats['engine']['orders_rejected']} rejected")
            
            # Account stats
            print(f"\n💰 Account:")
            print(f"   Equity: ₹{stats['account']['equity']:,.2f}")
            print(f"   Cash: ₹{stats['account']['cash']:,.2f}")
            print(f"   P&L: ₹{stats['account']['total_pnl']:+,.2f} "
                  f"({stats['account']['return_pct']:+.2f}%)")
            
            # Positions
            if stats['positions']['count'] > 0:
                print(f"\n📍 Positions: {stats['positions']['count']}")
                print(f"   Symbols: {', '.join(stats['positions']['symbols'])}")
            else:
                print(f"\n📍 Positions: None")
            
            # WebSocket stats
            print(f"\n📡 WebSocket:")
            print(f"   Connected: {ws_stats['connected']}")
            print(f"   Ticks received: {ws_stats['ticks_received']}")
            print(f"   Uptime: {ws_stats.get('uptime_seconds', 0):.0f}s")
            
            # Risk status
            risk_status = stats['risk']
            print(f"\n🛡️  Risk:")
            print(f"   Status: {risk_status.get('status', 'OK')}")
            print(f"   Daily P&L: ₹{risk_status.get('daily_pnl', 0):+,.2f}")
            
            print(f"\n{'='*70}\n")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping live trading...")
    
    except Exception as e:
        logger.error(f"Error in monitoring loop: {e}")
        print(f"\n❌ Error: {e}")
    
    finally:
        # =================================================================
        # SHUTDOWN
        # =================================================================
        
        print("\n" + "="*70)
        print(" " * 25 + "SHUTTING DOWN")
        print("="*70 + "\n")
        
        # Stop execution engine
        print("1️⃣  Stopping execution engine...")
        engine.stop()
        print("   ✅ Engine stopped\n")
        
        # Disconnect live data
        print("2️⃣  Closing WebSocket connection...")
        live_data.disconnect()
        print("   ✅ WebSocket closed\n")
        
        # Stop event bus
        print("3️⃣  Stopping event bus...")
        event_bus.stop()
        print("   ✅ Event bus stopped\n")
        
        # Final statistics
        final_stats = engine.get_statistics()
        
        print("="*70)
        print(" " * 25 + "FINAL SUMMARY")
        print("="*70)
        print(f"\n📊 Trading Session:")
        print(f"   Duration: {final_stats['engine']['uptime']:.0f}s")
        print(f"   Signals: {final_stats['engine']['signals_received']}")
        print(f"   Orders Filled: {final_stats['engine']['orders_filled']}")
        
        print(f"\n💰 Final Account:")
        print(f"   Equity: ₹{final_stats['account']['equity']:,.2f}")
        print(f"   Total P&L: ₹{final_stats['account']['total_pnl']:+,.2f}")
        print(f"   Return: {final_stats['account']['return_pct']:+.2f}%")
        
        print(f"\n📡 Data Stream:")
        print(f"   Total Ticks: {ws_stats['ticks_received']}")
        
        print("\n" + "="*70)
        print("✅ Shutdown complete. Thank you for using QuantX!")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
