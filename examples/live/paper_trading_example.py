"""
Paper Trading Example - Demonstrates paper trading functionality.

This example shows how to:
1. Create and configure a paper trading broker
2. Place orders and track executions
3. Monitor positions and P&L
4. Compare paper trading with backtesting
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from quantx.execution import (
    PaperBroker, BrokerFactory,
    Order, OrderType, OrderSide, OrderStatus
)
from quantx.data.providers.yahoo import YahooFinanceProvider


def example_1_basic_paper_trading():
    """Example 1: Basic paper trading setup and order execution."""
    logger.info("=" * 80)
    logger.info("Example 1: Basic Paper Trading")
    logger.info("=" * 80)
    
    # Create paper broker
    broker = PaperBroker(
        name="paper",
        config={
            "initial_capital": 100000,
            "commission": 0.001,  # 0.1%
            "slippage": 0.0005    # 0.05%
        }
    )
    
    # Connect
    broker.connect()
    logger.info(f"Connected: {broker.is_connected()}")
    
    # Get initial account state
    account = broker.get_account()
    logger.info(f"\nInitial Account:")
    logger.info(f"  Cash: ${account.cash:,.2f}")
    logger.info(f"  Equity: ${account.equity:,.2f}")
    logger.info(f"  Buying Power: ${account.buying_power:,.2f}")
    
    # Set current price for AAPL
    broker.update_prices({"AAPL": 150.00})
    
    # Place a market buy order
    logger.info("\nPlacing market buy order...")
    order = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100
    )
    
    order_id = broker.place_order(order)
    logger.info(f"Order placed: {order_id}")
    
    # Check order status
    filled_order = broker.get_order(order_id)
    logger.info(f"\nOrder Status: {filled_order.status.value}")
    logger.info(f"Filled Quantity: {filled_order.filled_quantity}")
    logger.info(f"Average Fill Price: ${filled_order.average_fill_price:.2f}")
    
    # Check position
    position = broker.get_position("AAPL")
    if position:
        logger.info(f"\nPosition:")
        logger.info(f"  Symbol: {position.symbol}")
        logger.info(f"  Quantity: {position.quantity}")
        logger.info(f"  Average Price: ${position.average_price:.2f}")
        logger.info(f"  Market Value: ${position.market_value:,.2f}")
        logger.info(f"  Unrealized P&L: ${position.unrealized_pnl:,.2f}")
    
    # Check account after trade
    account = broker.get_account()
    logger.info(f"\nAccount After Trade:")
    logger.info(f"  Cash: ${account.cash:,.2f}")
    logger.info(f"  Positions Value: ${account.positions_value:,.2f}")
    logger.info(f"  Equity: ${account.equity:,.2f}")
    logger.info(f"  Total P&L: ${account.total_pnl:,.2f}")
    
    return broker


def example_2_multiple_trades():
    """Example 2: Multiple trades and position tracking."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: Multiple Trades")
    logger.info("=" * 80)
    
    broker = PaperBroker(name="paper", config={"initial_capital": 100000})
    broker.connect()
    
    # Set prices
    broker.update_prices({
        "AAPL": 150.00,
        "GOOGL": 2800.00,
        "MSFT": 380.00
    })
    
    # Place multiple orders
    symbols = ["AAPL", "GOOGL", "MSFT"]
    quantities = [100, 10, 50]
    
    logger.info("\nPlacing multiple orders...")
    for symbol, qty in zip(symbols, quantities):
        order = Order(
            order_id="",
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=qty
        )
        order_id = broker.place_order(order)
        logger.info(f"  {symbol}: {qty} shares - Order ID: {order_id}")
    
    # Check all positions
    logger.info("\nCurrent Positions:")
    positions = broker.get_positions()
    for pos in positions:
        logger.info(f"  {pos.symbol}: {pos.quantity} @ ${pos.average_price:.2f} = ${pos.market_value:,.2f}")
    
    # Simulate price changes
    logger.info("\nSimulating price changes...")
    broker.update_prices({
        "AAPL": 155.00,  # +3.33%
        "GOOGL": 2750.00,  # -1.79%
        "MSFT": 385.00   # +1.32%
    })
    
    # Check updated positions
    logger.info("\nUpdated Positions (after price changes):")
    positions = broker.get_positions()
    total_unrealized_pnl = 0
    for pos in positions:
        logger.info(
            f"  {pos.symbol}: {pos.quantity} @ ${pos.average_price:.2f} → "
            f"${pos.current_price:.2f} | P&L: ${pos.unrealized_pnl:,.2f}"
        )
        total_unrealized_pnl += pos.unrealized_pnl
    
    logger.info(f"\nTotal Unrealized P&L: ${total_unrealized_pnl:,.2f}")
    
    # Get account summary
    account = broker.get_account()
    logger.info(f"\nAccount Summary:")
    logger.info(f"  Cash: ${account.cash:,.2f}")
    logger.info(f"  Positions: ${account.positions_value:,.2f}")
    logger.info(f"  Equity: ${account.equity:,.2f}")
    logger.info(f"  Return: {account.return_pct:.2f}%")
    
    return broker


def example_3_sell_and_realize_pnl():
    """Example 3: Selling positions and realizing P&L."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Sell and Realize P&L")
    logger.info("=" * 80)
    
    broker = PaperBroker(name="paper", config={"initial_capital": 100000})
    broker.connect()
    
    # Buy AAPL
    broker.update_prices({"AAPL": 150.00})
    buy_order = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100
    )
    broker.place_order(buy_order)
    logger.info("Bought 100 AAPL @ $150.00")
    
    # Price goes up
    broker.update_prices({"AAPL": 160.00})
    position = broker.get_position("AAPL")
    logger.info(f"Price increased to $160.00")
    logger.info(f"Unrealized P&L: ${position.unrealized_pnl:,.2f}")
    
    # Sell half
    logger.info("\nSelling 50 shares...")
    sell_order = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        quantity=50
    )
    broker.place_order(sell_order)
    
    # Check position after partial sell
    position = broker.get_position("AAPL")
    logger.info(f"\nAfter selling 50 shares:")
    logger.info(f"  Remaining: {position.quantity} shares")
    logger.info(f"  Unrealized P&L: ${position.unrealized_pnl:,.2f}")
    logger.info(f"  Realized P&L: ${position.realized_pnl:,.2f}")
    
    # Sell remaining
    logger.info("\nSelling remaining 50 shares...")
    sell_order2 = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        quantity=50
    )
    broker.place_order(sell_order2)
    
    # Check account
    account = broker.get_account()
    logger.info(f"\nFinal Account:")
    logger.info(f"  Cash: ${account.cash:,.2f}")
    logger.info(f"  Realized P&L: ${account.realized_pnl:,.2f}")
    logger.info(f"  Return: {account.return_pct:.2f}%")
    
    # Trade history
    history = broker.get_trade_history()
    logger.info(f"\nTrade History:")
    logger.info(history.to_string())
    
    return broker


def example_4_using_factory():
    """Example 4: Using BrokerFactory to create brokers."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 4: Using Broker Factory")
    logger.info("=" * 80)
    
    # List available brokers
    brokers = BrokerFactory.list_brokers()
    logger.info(f"Available brokers: {brokers}")
    
    # Create broker using factory
    config = {
        "initial_capital": 50000,
        "commission": 0.002,  # 0.2%
        "slippage": 0.001     # 0.1%
    }
    
    broker = BrokerFactory.create("paper", config)
    logger.info(f"Created broker: {broker.name}")
    
    broker.connect()
    
    # Test trade
    broker.update_prices({"TSLA": 250.00})
    order = Order(
        order_id="",
        symbol="TSLA",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=20
    )
    broker.place_order(order)
    
    account = broker.get_account()
    logger.info(f"\nAccount after trade:")
    logger.info(f"  Initial Capital: ${account.initial_capital:,.2f}")
    logger.info(f"  Cash: ${account.cash:,.2f}")
    logger.info(f"  Equity: ${account.equity:,.2f}")
    
    return broker


def example_5_realistic_trading_scenario():
    """Example 5: Realistic trading scenario with real market data."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 5: Realistic Trading Scenario")
    logger.info("=" * 80)
    
    # Create broker
    broker = PaperBroker(
        name="paper",
        config={
            "initial_capital": 100000,
            "commission": 0.001,
            "slippage": 0.0005
        }
    )
    broker.connect()
    
    # Fetch real market data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    logger.info("Fetching market data...")
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    logger.info(f"\nSimulating trading over {len(data)} days...")
    
    # Simulate trading each day
    for i, (date, row) in enumerate(data.iterrows()):
        # Update price
        broker.update_prices({"AAPL": row['close']})
        
        # Simple strategy: buy on day 1, sell on last day
        if i == 0:
            # Buy on first day
            order = Order(
                order_id="",
                symbol="AAPL",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=100
            )
            broker.place_order(order)
            logger.info(f"Day {i+1}: Bought 100 AAPL @ ${row['close']:.2f}")
        
        elif i == len(data) - 1:
            # Sell on last day
            order = Order(
                order_id="",
                symbol="AAPL",
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                quantity=100
            )
            broker.place_order(order)
            logger.info(f"Day {i+1}: Sold 100 AAPL @ ${row['close']:.2f}")
        
        else:
            # Hold and update P&L
            position = broker.get_position("AAPL")
            if position:
                logger.info(
                    f"Day {i+1}: Holding - Price: ${row['close']:.2f}, "
                    f"Unrealized P&L: ${position.unrealized_pnl:,.2f}"
                )
    
    # Final results
    account = broker.get_account()
    logger.info(f"\nFinal Results:")
    logger.info(f"  Initial Capital: ${account.initial_capital:,.2f}")
    logger.info(f"  Final Equity: ${account.equity:,.2f}")
    logger.info(f"  Total P&L: ${account.total_pnl:,.2f}")
    logger.info(f"  Return: {account.return_pct:.2f}%")
    
    # Trade history
    history = broker.get_trade_history()
    logger.info(f"\nTrade Summary:")
    logger.info(f"  Total Trades: {len(history)}")
    logger.info(f"  Total Commission: ${history['commission'].sum():.2f}")


def main():
    """Run all examples."""
    logger.info("Paper Trading Examples")
    logger.info("=" * 80)
    
    try:
        # Example 1: Basic paper trading
        example_1_basic_paper_trading()
        
        # Example 2: Multiple trades
        example_2_multiple_trades()
        
        # Example 3: Sell and realize P&L
        example_3_sell_and_realize_pnl()
        
        # Example 4: Using factory
        example_4_using_factory()
        
        # Example 5: Realistic scenario
        example_5_realistic_trading_scenario()
        
        logger.info("\n" + "=" * 80)
        logger.info("All paper trading examples completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
