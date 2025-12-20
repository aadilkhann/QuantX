"""
Zerodha WebSocket Streaming Example.

Demonstrates real-time data streaming from Zerodha using WebSocket.
"""

import sys
from pathlib import Path
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from loguru import logger

from quantx.core.events import EventBus, Event, EventType
from quantx.data.streaming import ZerodhaWebSocket, LiveDataProvider


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


def example_1_basic_websocket():
    """Example 1: Basic WebSocket streaming."""
    print("\n" + "="*70)
    print("Example 1: Basic WebSocket Streaming")
    print("="*70 + "\n")
    
    session = load_session()
    if not session or "access_token" not in session:
        print("❌ Please authenticate first! Run zerodha_authentication.py")
        return
    
    # Create WebSocket client
    ws = ZerodhaWebSocket(
        api_key=session["api_key"],
        access_token=session["access_token"]
    )
    
    # Tick counter
    tick_count = [0]
    
    # Define tick callback
    def on_tick(ticks):
        tick_count[0] += len(ticks)
        for tick in ticks:
            print(f"📊 Tick: Token={tick['instrument_token']} "
                  f"LTP=₹{tick.get('last_price', 0):,.2f} "
                  f"Volume={tick.get('volume', 0):,}")
    
    # Register callback
    ws.on_ticks(on_tick)
    
    # Connect callback
    def on_connect(response):
        print(f"✅ Connected to WebSocket!")
        print("Ready to receive ticks...")
    
    ws.on_connect(on_connect)
    
    # Connect
    print("🔌 Connecting to WebSocket...")
    ws.connect(threaded=True)
    
    # Wait for connection
    time.sleep(2)
    
    # Subscribe to instruments
    # NSE:INFY = 408065, NSE:TCS = 2953217, NSE:RELIANCE = 738561
    instruments = [408065, 2953217, 738561]
    
    print(f"\n📡 Subscribing to {len(instruments)} instruments...")
    ws.subscribe(instruments, mode="quote")
    
    # Stream for 30 seconds
    print("\n⏳ Streaming for 30 seconds...\n")
    try:
        for i in range(30):
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                stats = ws.get_statistics()
                print(f"\n📊 Stats: {stats['ticks_received']} ticks received, "
                      f"Uptime: {stats['uptime_seconds']:.0f}s\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Close connection
        print(f"\n🛑 Closing connection...")
        ws.close()
        print(f"✅ Total ticks received: {tick_count[0]}")


def example_2_with_event_bus():
    """Example 2: WebSocket with EventBus integration."""
    print("\n" + "="*70)
    print("Example 2: WebSocket with EventBus")
    print("="*70 + "\n")
    
    session = load_session()
    if not session:
        print("❌ Please authenticate first!")
        return
    
    # Create event bus
    event_bus = EventBus()
    event_bus.start()
    
    # Create WebSocket with event bus
    ws = ZerodhaWebSocket(
        api_key=session["api_key"],
        access_token=session["access_token"],
        event_bus=event_bus
    )
    
    # Subscribe to tick events
    tick_count = [0]
    
    def handle_tick_event(event: Event):
        tick_count[0] += 1
        data = event.data
        if tick_count[0] % 10 == 0:  # Print every 10th tick
            print(f"📊 Tick Event: LTP=₹{data.get('last_price', 0):,.2f}")
    
    event_bus.subscribe(EventType.TICK, handle_tick_event)
    
    # Connect
    print("🔌 Connecting...")
    ws.connect(threaded=True)
    time.sleep(2)
    
    # Subscribe
    instruments = [408065]  # NSE:INFY
    print(f"📡 Subscribing to INFY...")
    ws.subscribe(instruments, mode="full")
    
    # Stream for 20 seconds
    print("\n⏳ Streaming for 20 seconds...\n")
    try:
        time.sleep(20)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    finally:
        ws.close()
        event_bus.stop()
        print(f"\n✅ Received {tick_count[0]} tick events")


def example_3_live_data_provider():
    """Example 3: Using LiveDataProvider."""
    print("\n" + "="*70)
    print("Example 3: Live Data Provider")
    print("="*70 + "\n")
    
    session = load_session()
    if not session:
        print("❌ Please authenticate first!")
        return
    
    # Create event bus
    event_bus = EventBus()
    event_bus.start()
    
    # Create instrument lookup (symbol -> token)
    # In production, this would come from broker.get_instruments()
    instrument_lookup = {
        "NSE:INFY": 408065,
        "NSE:TCS": 2953217,
        "NSE:RELIANCE": 738561
    }
    
    # Create live data provider
    provider = LiveDataProvider(
        api_key=session["api_key"],
        access_token=session["access_token"],
        event_bus=event_bus,
        instrument_lookup=instrument_lookup
    )
    
    # Handle tick events
    tick_count = [0]
    last_prices = {}
    
    def handle_tick(event: Event):
        tick_count[0] += 1
        data = event.data
        token = data.get('instrument_token')
        price = data.get('last_price', 0)
        
        last_prices[token] = price
        
        if tick_count[0] % 20 == 0:
            print(f"\n📊 Latest Prices:")
            for sym, tok in instrument_lookup.items():
                if tok in last_prices:
                    print(f"   {sym}: ₹{last_prices[tok]:,.2f}")
    
    event_bus.subscribe(EventType.TICK, handle_tick)
    
    # Connect and subscribe
    print("🔌 Connecting to live data...")
    provider.connect()
    time.sleep(2)
    
    symbols = ["NSE:INFY", "NSE:TCS", "NSE:RELIANCE"]
    print(f"📡 Subscribing to {len(symbols)} symbols...")
    provider.subscribe_symbols(symbols, mode="quote")
    
    # Stream
    print("\n⏳ Streaming for 30 seconds...\n")
    try:
        for i in range(30):
            time.sleep(1)
            if i == 15:
                # Change subscription mid-stream
                print("\n🔄 Changing subscription...")
                provider.unsubscribe_symbols(["NSE:TCS"])
                print("   Unsubscribed from TCS\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    
    finally:
        # Display stats
        stats = provider.get_statistics()
        print(f"\n📈 Final Statistics:")
        print(f"   Total Ticks: {stats['ticks_received']}")
        print(f"   Subscribed: {len(stats['subscribed_symbols'])} symbols")
        print(f"   Uptime: {stats['uptime_seconds']:.0f}s")
        
        provider.disconnect()
        event_bus.stop()


def example_4_market_depth():
    """Example 4: Full market depth streaming."""
    print("\n" + "="*70)
    print("Example 4: Market Depth (Full Mode)")
    print("="*70 + "\n")
    
    session = load_session()
    if not session:
        print("❌ Please authenticate first!")
        return
    
    ws = ZerodhaWebSocket(
        api_key=session["api_key"],
        access_token=session["access_token"]
    )
    
    def on_tick(ticks):
        for tick in ticks:
            if 'depth' in tick:
                depth = tick['depth']
                
                print(f"\n📊 {tick['instrument_token']} - "
                      f"LTP: ₹{tick.get('last_price', 0):,.2f}")
                
                # Buy depth
                print("  🟢 BUY:")
                for i, bid in enumerate(depth.get('buy', [])[:3], 1):
                    print(f"     {i}. ₹{bid['price']:,.2f} x {bid['quantity']:,} "
                          f"(Orders: {bid['orders']})")
                
                # Sell depth
                print("  🔴 SELL:")
                for i, ask in enumerate(depth.get('sell', [])[:3], 1):
                    print(f"     {i}. ₹{ask['price']:,.2f} x {ask['quantity']:,} "
                          f"(Orders: {ask['orders']})")
    
    ws.on_ticks(on_tick)
    
    print("🔌 Connecting...")
    ws.connect(threaded=True)
    time.sleep(2)
    
    instruments = [408065]  # NSE:INFY
    print("📡 Subscribing in FULL mode (market depth)...")
    ws.subscribe(instruments, mode="full")
    
    print("\n⏳ Streaming for 15 seconds...\n")
    try:
        time.sleep(15)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    finally:
        ws.close()


def main():
    """Run streaming examples."""
    setup_logging()
    
    print("\n" + "="*70)
    print(" " * 18 + "Zerodha WebSocket Streaming Examples")
    print("="*70)
    
    # Check for session
    session = load_session()
    if not session or "access_token" not in session:
        print("\n❌ No saved session found!")
        print("   Please run zerodha_authentication.py first to authenticate.")
        return
    
    print(f"\n✅ Session loaded for user: {session.get('user_id', 'Unknown')}")
    print("\n⚠️  Note: WebSocket streaming requires active market hours")
    print("   NSE: 9:15 AM - 3:30 PM IST")
    
    print("\nChoose an example:")
    print("\n1. Basic WebSocket Streaming")
    print("2. WebSocket with EventBus Integration")
    print("3. Live Data Provider (High-Level API)")
    print("4. Market Depth (Full Mode)")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-4): ").strip()
    
    try:
        if choice == "1":
            example_1_basic_websocket()
        elif choice == "2":
            example_2_with_event_bus()
        elif choice == "3":
            example_3_live_data_provider()
        elif choice == "4":
            example_4_market_depth()
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
