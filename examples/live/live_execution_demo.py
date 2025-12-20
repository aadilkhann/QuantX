"""
Live Execution Engine Example.

Demonstrates how to use the LiveExecutionEngine for live trading
with strategies, order management, and risk controls.
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from loguru import logger

from quantx.core.events import EventBus, Event, EventType
from quantx.core.config import Config
from quantx.execution import (
    PaperBroker,
    OrderManager,
    RiskManager,
    RiskLimits,
    LiveExecutionEngine,
    EngineConfig
)
from quantx.strategies import StrategyRegistry
from quantx.data.providers.yahoo import YahooFinanceProvider


def setup_logging():
    """Setup logging configuration."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>",
        level="INFO"
    )


def example_1_basic_setup():
    """Example 1: Basic live execution engine setup."""
    print("\n" + "="*70)
    print("Example 1: Basic Live Execution Engine Setup")
    print("="*70 + "\n")
    
    # Create components
    event_bus = EventBus()
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    
    # Create strategy
    strategy = StrategyRegistry.create("ma_crossover", {
        "fast_period": 10,
        "slow_period": 20,
        "symbols": ["AAPL"]
    })
    
    # Create OMS and Risk Manager
    order_manager = OrderManager(broker, event_bus=event_bus)
    risk_manager = RiskManager(
        limits=RiskLimits(
            max_position_size_pct=0.1,
            max_daily_loss=1000.0,
            max_drawdown_pct=0.05
        )
    )
    order_manager.set_risk_manager(risk_manager)
    
    # Create execution engine
    engine_config = EngineConfig(
        position_sync_interval=30,
        heartbeat_interval=5,
        dry_run=True  # Don't actually place orders
    )
    
    engine = LiveExecutionEngine(
        strategy=strategy,
        broker=broker,
        order_manager=order_manager,
        risk_manager=risk_manager,
        event_bus=event_bus,
        config=engine_config
    )
    
    print(f"✅ LiveExecutionEngine created")
    print(f"   Strategy: {strategy.name}")
    print(f"   Broker: {broker.name}")
    print(f"   Initial Capital: ${broker.config['initial_capital']:,.2f}")
    print(f"   Dry Run Mode: {engine_config.dry_run}")
    
    # Start engine
    print("\n🚀 Starting engine...")
    if engine.start():
        print("✅ Engine started successfully")
        
        # Get status
        status = engine.get_status()
        print(f"\nEngine Status:")
        print(f"   State: {status['state']}")
        print(f"   Broker Connected: {status['broker_connected']}")
        print(f"   Strategy: {status['strategy']}")
        
        # Let it run for a few seconds
        print("\n⏳ Running for 5 seconds...")
        time.sleep(5)
        
        # Get statistics
        stats = engine.get_statistics()
        print(f"\nEngine Statistics:")
        print(f"   Uptime: {stats['engine']['uptime']:.1f}s")
        print(f"   Signals Received: {stats['engine']['signals_received']}")
        print(f"   Orders Submitted: {stats['engine']['orders_submitted']}")
        print(f"   Account Equity: ${stats['account']['equity']:,.2f}")
        
        # Stop engine
        print("\n🛑 Stopping engine...")
        engine.stop()
        print("✅ Engine stopped")
    
    return engine


def example_2_with_signals():
    """Example 2: Live trading with manual signals."""
    print("\n" + "="*70)
    print("Example 2: Live Trading with Manual Signals")
    print("="*70 + "\n")
    
    # Setup components
    event_bus = EventBus()
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    
    # Update market prices
    broker.update_prices({"AAPL": 150.0, "GOOGL": 2800.0})
    
    # Create simple strategy
    from quantx.strategies.base import RuleBasedStrategy
    
    class SimpleStrategy(RuleBasedStrategy):
        def on_data(self, event):
            # Strategy just receives signals, we'll send manually
            pass
        
        def on_fill(self, event):
            fill = event.data
            logger.info(f"Strategy received fill: {fill}")
    
    strategy = SimpleStrategy("simple", {"symbols": ["AAPL", "GOOGL"]})
    
    # Create OMS and Risk
    order_manager = OrderManager(broker, event_bus=event_bus)
    risk_manager = RiskManager(
        limits=RiskLimits(
            max_position_size_pct=0.2,
            max_daily_loss=5000.0
        )
    )
    order_manager.set_risk_manager(risk_manager)
    
    # Create engine (not dry run this time)
    engine = LiveExecutionEngine(
        strategy=strategy,
        broker=broker,
        order_manager=order_manager,
        risk_manager=risk_manager,
        event_bus=event_bus,
        config=EngineConfig(dry_run=False)
    )
    
    # Start engine
    engine.start()
    event_bus.start()
    
    print("✅ Engine running in live mode")
    print(f"   Initial Equity: ${broker.get_account().equity:,.2f}\n")
    
    # Generate buy signals
    print("📊 Generating BUY signal for AAPL...")
    strategy.buy("AAPL", quantity=10)
    time.sleep(1)
    
    print("📊 Generating BUY signal for GOOGL...")
    strategy.buy("GOOGL", quantity=5)
    time.sleep(2)
    
    # Check positions
    positions = broker.get_positions()
    print(f"\n📍 Current Positions: {len(positions)}")
    for pos in positions:
        print(f"   {pos.symbol}: {pos.quantity} @ ${pos.average_price:.2f} = ${pos.unrealized_pnl:+,.2f}")
    
    # Update prices (simulate price movement)
    print("\n💹 Simulating price movement...")
    broker.update_prices({"AAPL": 155.0, "GOOGL": 2850.0})
    time.sleep(1)
    
    # Check updated P&L
    account = broker.get_account()
    print(f"\n💰 Updated Account:")
    print(f"   Equity: ${account.equity:,.2f}")
    print(f"   Unrealized P&L: ${account.unrealized_pnl:+,.2f}")
    
    # Generate sell signals
    print("\n📊 Generating SELL signals...")
    strategy.sell("AAPL", quantity=10)
    time.sleep(1)
    strategy.sell("GOOGL", quantity=5)
    time.sleep(1)
    
    # Final statistics
    stats = engine.get_statistics()
    print(f"\n📈 Final Statistics:")
    print(f"   Signals Received: {stats['engine']['signals_received']}")
    print(f"   Orders Filled: {stats['engine']['orders_filled']}")
    print(f"   Final Equity: ${stats['account']['equity']:,.2f}")
    print(f"   Total P&L: ${stats['account']['total_pnl']:+,.2f}")
    print(f"   Return: {stats['account']['return_pct']:+.2f}%")
    
    # Stop engine
    engine.stop()
    event_bus.stop()
    
    print("\n✅ Example complete")


def example_3_position_sync():
    """Example 3: Position synchronization."""
    print("\n" + "="*70)
    print("Example 3: Position Synchronization")
    print("="*70 + "\n")
    
    from quantx.execution.position_sync import PositionSynchronizer
    
    # Setup broker with some positions
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    broker.update_prices({"AAPL": 150.0, "MSFT": 300.0, "GOOGL": 2800.0})
    
    # Place some orders to create positions
    from quantx.execution.brokers.base import Order, OrderType, OrderSide
    
    orders = [
        Order("", "AAPL", OrderSide.BUY, OrderType.MARKET, 10),
        Order("", "MSFT", OrderSide.BUY, OrderType.MARKET, 5),
    ]
    
    for order in orders:
        broker.place_order(order)
    
    print(f"📍 Created {len(broker.get_positions())} positions at broker")
    
    # Create local positions (simulating strategy positions)
    local_positions = {
        "AAPL": 10,   # Matches
        "MSFT": 3,    # Mismatch (should be 5)
        "TSLA": 7,    # Missing from broker
        # Missing GOOGL which might be at broker later
    }
    
    print(f"📍 Local tracking: {len(local_positions)} positions\n")
    
    # Create synchronizer
    sync = PositionSynchronizer(broker, auto_reconcile=True)
    
    # Perform sync
    print("🔄 Synchronizing positions...")
    report = sync.sync_positions(local_positions)
    
    # Display report
    print(f"\n📋 Reconciliation Report:")
    print(f"   Synced: {report.synced}")
    print(f"   Broker Positions: {report.total_positions_broker}")
    print(f"   Local Positions: {report.total_positions_local}")
    print(f"   Discrepancies: {len(report.discrepancies)}")
    
    if report.discrepancies:
        print("\n   Discrepancy Details:")
        for disc in report.discrepancies:
            print(f"     - {disc.symbol}: {disc.type.value}")
            print(f"         Local: {disc.local_quantity}, Broker: {disc.broker_quantity}")
            print(f"         Resolved: {disc.resolved}")
    
    # Check reconciled positions
    print(f"\n✅ Reconciled Local Positions:")
    for symbol, qty in local_positions.items():
        if qty != 0:
            print(f"   {symbol}: {qty}")
    
    # Sync statistics
    stats = sync.get_statistics()
    print(f"\n📊 Sync Statistics:")
    print(f"   Total Syncs: {stats['sync_count']}")
    print(f"   Total Discrepancies Found: {stats['total_discrepancies']}")


def example_4_pnl_tracking():
    """Example 4: Live P&L tracking."""
    print("\n" + "="*70)
    print("Example 4: Live P&L Tracking")
    print("="*70 + "\n")
    
    from quantx.execution.live_pnl import LivePnLTracker
    from quantx.execution.brokers.base import Position
    
    # Create P&L tracker
    tracker = LivePnLTracker(initial_capital=100000)
    
    print(f"💰 Initial Capital: ${tracker.initial_capital:,.2f}\n")
    
    # Simulate some trades
    print("📊 Recording Trade 1: Long AAPL")
    trade1 = tracker.record_trade(
        symbol="AAPL",
        entry_time=datetime.now() - timedelta(hours=2),
        exit_time=datetime.now() - timedelta(hours=1),
        entry_price=150.0,
        exit_price=155.0,
        quantity=10,
        side="long",
        commission=2.0
    )
    print(f"   P&L: ${trade1.net_pnl:+,.2f} ({trade1.pnl_pct:+.2f}%)")
    
    print("\n📊 Recording Trade 2: Long MSFT")
    trade2 = tracker.record_trade(
        symbol="MSFT",
        entry_time=datetime.now() - timedelta(hours=1),
        exit_time=datetime.now() - timedelta(minutes=30),
        entry_price=300.0,
        exit_price=295.0,
        quantity=5,
        side="long",
        commission=1.5
    )
    print(f"   P&L: ${trade2.net_pnl:+,.2f} ({trade2.pnl_pct:+.2f}%)")
    
    # Add open positions for unrealized P&L
    print("\n📍 Adding Open Position: GOOGL")
    tracker.update_position_pnl(
        symbol="GOOGL",
        quantity=3,
        average_price=2800.0,
        current_price=2850.0
    )
    
    # Get snapshot
    snapshot = tracker.get_snapshot()
    print(f"\n💰 Current P&L Snapshot:")
    print(f"   Realized P&L: ${snapshot.realized_pnl:+,.2f}")
    print(f"   Unrealized P&L: ${snapshot.unrealized_pnl:+,.2f}")
    print(f"   Total P&L: ${snapshot.total_pnl:+,.2f}")
    print(f"   Commission: ${snapshot.total_commission:,.2f}")
    print(f"   Open Positions: {snapshot.open_positions}")
    print(f"   Closed Trades: {snapshot.closed_trades}")
    print(f"   Win Rate: {snapshot.win_rate:.1f}%")
    
    # Get performance summary
    summary = tracker.get_performance_summary()
    print(f"\n📈 Performance Summary:")
    print(f"   Total Equity: ${summary['equity']:,.2f}")
    print(f"   Return: {summary['return_pct']:+.2f}%")
    print(f"   Winning Trades: {summary['winning_trades']}")
    print(f"   Losing Trades: {summary['losing_trades']}")
    print(f"   Avg Win: ${summary['avg_win']:+,.2f}")
    print(f"   Avg Loss: ${summary['avg_loss']:+,.2f}")
    print(f"   Profit Factor: {summary['profit_factor']:.2f}")


def main():
    """Run all examples."""
    setup_logging()
    
    print("\n" + "="*70)
    print(" " * 15 + "Live Execution Engine Examples")
    print("="*70)
    
    try:
        # Run examples
        example_1_basic_setup()
        input("\nPress Enter to continue to Example 2...")
        
        example_2_with_signals()
        input("\nPress Enter to continue to Example 3...")
        
        example_3_position_sync()
        input("\nPress Enter to continue to Example 4...")
        
        example_4_pnl_tracking()
        
        print("\n" + "="*70)
        print(" " * 20 + "✅ All Examples Complete!")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Examples interrupted by user")
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        raise


if __name__ == "__main__":
    main()
