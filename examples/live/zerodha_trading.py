"""
Zerodha Trading Example.

Demonstrates live trading with Zerodha broker including:
- Market data retrieval
- Order placement
- Position management
- Account monitoring
"""

import sys
from pathlib import Path
import json
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from loguru import logger

from quantx.execution.brokers import ZerodhaBroker, Order, OrderType, OrderSide


def setup_logging():
    """Setup logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>",
        level="INFO"
    )


def load_session(filename: str = "zerodha_session.json") -> dict:
    """Load saved session."""
    filepath = Path(__file__).parent / filename
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def example_1_get_quotes():
    """Example 1: Get market quotes."""
    print("\n" + "="*70)
    print("Example 1: Get Market Quotes")
    print("="*70 + "\n")
    
    session = load_session()
    if not session or "access_token" not in session:
        print("❌ Please run zerodha_authentication.py first!")
        return
    
    broker = ZerodhaBroker("zerodha", session)
    
    if not broker.connect():
        print("❌ Connection failed!")
        return
    
    # Get quotes for NSE stocks
    symbols = ["NSE:INFY", "NSE:TCS", "NSE:RELIANCE"]
    
    print("📊 Fetching quotes...\n")
    for symbol in symbols:
        quote = broker.get_quote(symbol)
        
        print(f"{symbol}:")
        print(f"   Last Price: ₹{quote['last']:,.2f}")
        print(f"   Bid: ₹{quote['bid']:,.2f}")
        print(f"   Ask: ₹{quote['ask']:,.2f}")
        print(f"   Day Range: ₹{quote['low']:,.2f} - ₹{quote['high']:,.2f}")
        print(f"   Volume: {quote.get('volume', 0):,}")
        print()
    
    broker.disconnect()


def example_2_place_market_order():
    """Example 2: Place market order (DEMO - will be rejected)."""
    print("\n" + "="*70)
    print("Example 2: Place Market Order")
    print("="*70 + "\n")
    
    print("⚠️  WARNING: This example shows how to place orders.")
    print("   The order will likely be rejected due to insufficient funds/margin.")
    print("   This is for DEMONSTRATION purposes only!\n")
    
    proceed = input("Continue? (yes/no): ").strip().lower()
    if proceed != "yes":
        print("Cancelled.")
        return
    
    session = load_session()
    if not session:
        print("❌ Please authenticate first!")
        return
    
    broker = ZerodhaBroker("zerodha", session)
    
    if not broker.connect():
        print("❌ Connection failed!")
        return
    
    # Create a small market order
    order = Order(
        order_id="",
        symbol="NSE:INFY",  # Infosys
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=1  # Just 1 share
    )
    
    print(f"\n📝 Placing order:")
    print(f"   Symbol: {order.symbol}")
    print(f"   Side: {order.side.value}")
    print(f"   Type: {order.order_type.value}")
    print(f"   Quantity: {order.quantity}")
    
    try:
        order_id = broker.place_order(order)
        print(f"\n✅ Order placed! Order ID: {order_id}")
        
        # Wait a bit for order to process
        time.sleep(2)
        
        # Check order status
        updated_order = broker.get_order(order_id)
        if updated_order:
            print(f"\n📊 Order Status: {updated_order.status.value}")
            if updated_order.filled_quantity > 0:
                print(f"   Filled: {updated_order.filled_quantity} @ ₹{updated_order.average_fill_price:,.2f}")
        
    except Exception as e:
        print(f"\n❌ Order failed: {e}")
        logger.error(f"Order error: {e}")
    
    broker.disconnect()


def example_3_view_positions():
    """Example 3: View current positions."""
    print("\n" + "="*70)
    print("Example 3: View Current Positions")
    print("="*70 + "\n")
    
    session = load_session()
    if not session:
        print("❌ Please authenticate first!")
        return
    
    broker = ZerodhaBroker("zerodha", session)
    
    if not broker.connect():
        print("❌ Connection failed!")
        return
    
    # Get positions
    positions = broker.get_positions()
    
    if not positions:
        print("📍 No open positions")
    else:
        print(f"📍 Current Positions: {len(positions)}\n")
        
        total_pnl = 0.0
        for pos in positions:
            print(f"{pos.symbol}:")
            print(f"   Quantity: {pos.quantity}")
            print(f"   Avg Price: ₹{pos.average_price:,.2f}")
            print(f"   Current Price: ₹{pos.current_price:,.2f}")
            print(f"   P&L: ₹{pos.unrealized_pnl:+,.2f}")
            print(f"   Value: ₹{pos.market_value:,.2f}")
            print()
            
            total_pnl += pos.unrealized_pnl
        
        print(f"Total Unrealized P&L: ₹{total_pnl:+,.2f}")
    
    broker.disconnect()


def example_4_account_summary():
    """Example 4: Account summary."""
    print("\n" + "="*70)
    print("Example 4: Account Summary")
    print("="*70 + "\n")
    
    session = load_session()
    if not session:
        print("❌ Please authenticate first!")
        return
    
    broker = ZerodhaBroker("zerodha", session)
    
    if not broker.connect():
        print("❌ Connection failed!")
        return
    
    # Get account info
    try:
        account = broker.get_account()
        
        print("💰 Account Information:\n")
        print(f"   Account ID: {account.account_id}")
        print(f"   Available Cash: ₹{account.cash:,.2f}")
        print(f"   Total Equity: ₹{account.equity:,.2f}")
        print(f"   Buying Power: ₹{account.buying_power:,.2f}")
        print(f"   Positions Value: ₹{account.positions_value:,.2f}")
        print(f"   Unrealized P&L: ₹{account.unrealized_pnl:+,.2f}")
        print(f"   Return: {account.return_pct:+.2f}%")
        
    except Exception as e:
        print(f"❌ Failed to get account info: {e}")
        logger.error(f"Account error: {e}")
    
    broker.disconnect()


def example_5_open_orders():
    """Example 5: View open orders."""
    print("\n" + "="*70)
    print("Example 5: View Open Orders")
    print("="*70 + "\n")
    
    session = load_session()
    if not session:
        print("❌ Please authenticate first!")
        return
    
    broker = ZerodhaBroker("zerodha", session)
    
    if not broker.connect():
        print("❌ Connection failed!")
        return
    
    # Get open orders
    orders = broker.get_open_orders()
    
    if not orders:
        print("📝 No open orders")
    else:
        print(f"📝 Open Orders: {len(orders)}\n")
        
        for order in orders:
            print(f"Order ID: {order.order_id}")
            print(f"   Symbol: {order.symbol}")
            print(f"   Side: {order.side.value}")
            print(f"   Type: {order.order_type.value}")
            print(f"   Quantity: {order.quantity}")
            if order.price:
                print(f"   Price: ₹{order.price:,.2f}")
            print(f"   Status: {order.status.value}")
            print()
    
    broker.disconnect()


def main():
    """Run trading examples."""
    setup_logging()
    
    print("\n" + "="*70)
    print(" " * 20 + "Zerodha Trading Examples")
    print("="*70)
    
    # Check for saved session
    session = load_session()
    if not session or "access_token" not in session:
        print("\n❌ No saved session found!")
        print("   Please run zerodha_authentication.py first to authenticate.")
        return
    
    print(f"\n✅ Loaded session for user: {session.get('user_id', 'Unknown')}")
    
    print("\nChoose an example:")
    print("\n1. Get Market Quotes")
    print("2. Place Market Order (DEMO)")
    print("3. View Current Positions")
    print("4. Account Summary")
    print("5. View Open Orders")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-5): ").strip()
    
    try:
        if choice == "1":
            example_1_get_quotes()
        elif choice == "2":
            example_2_place_market_order()
        elif choice == "3":
            example_3_view_positions()
        elif choice == "4":
            example_4_account_summary()
        elif choice == "5":
            example_5_open_orders()
        elif choice == "0":
            print("\n👋 Goodbye!")
        else:
            print("\n❌ Invalid choice!")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
    
    print()


if __name__ == "__main__":
    main()
