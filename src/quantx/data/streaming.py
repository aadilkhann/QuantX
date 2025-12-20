"""
Zerodha WebSocket Data Streaming.

Provides real-time tick data streaming from Zerodha Kite Connect API
using WebSocket connection.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from threading import Thread, Event as ThreadEvent
import time

from loguru import logger

from quantx.core.events import Event, EventBus, EventType


class ZerodhaWebSocket:
    """
    Zerodha WebSocket client for real-time tick data.
    
    Connects to Kite Connect WebSocket API and streams live market data
    (ticks, quotes, OHLC) for subscribed instruments.
    
    Tick Modes:
    - 'ltp': Last traded price only
    - 'quote': LTP + bid/ask + volume
    - 'full': Complete market depth
    
    Example:
        >>> ws = ZerodhaWebSocket(api_key, access_token)
        >>> ws.on_ticks = lambda ticks: print(ticks)
        >>> ws.connect()
        >>> ws.subscribe([256265], mode='quote')  # Subscribe to NSE:RELIANCE
        >>> # ... streaming happens ...
        >>> ws.close()
    
    Note:
        Requires kiteconnect package with WebSocket support
    """
    
    # Tick modes
    MODE_LTP = "ltp"
    MODE_QUOTE = "quote"
    MODE_FULL = "full"
    
    def __init__(
        self,
        api_key: str,
        access_token: str,
        event_bus: Optional[EventBus] = None,
        auto_reconnect: bool = True,
        max_reconnect_attempts: int = 5,
        reconnect_delay: int = 5
    ):
        """
        Initialize WebSocket client.
        
        Args:
            api_key: Kite Connect API key
            access_token: Valid access token
            event_bus: Optional EventBus for publishing market data events
            auto_reconnect: Enable automatic reconnection
            max_reconnect_attempts: Max reconnection attempts
            reconnect_delay: Delay between reconnection attempts (seconds)
        """
        self.api_key = api_key
        self.access_token = access_token
        self.event_bus = event_bus
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        
        # KiteTicker instance (lazy loaded)
        self._ticker = None
        
        # Connection state
        self._connected = False
        self._reconnect_count = 0
        
        # Subscriptions
        self._subscribed_tokens: List[int] = []
        self._subscription_mode: str = self.MODE_QUOTE
        
        # Callbacks
        self._tick_callbacks: List[Callable] = []
        self._connect_callbacks: List[Callable] = []
        self._error_callbacks: List[Callable] = []
        self._close_callbacks: List[Callable] = []
        
        # Statistics
        self.ticks_received = 0
        self.connection_time: Optional[datetime] = None
        self.last_tick_time: Optional[datetime] = None
        
        logger.info("ZerodhaWebSocket initialized")
    
    def _get_ticker(self):
        """Get or create KiteTicker instance."""
        if self._ticker is None:
            try:
                from kiteconnect import KiteTicker
                self._ticker = KiteTicker(self.api_key, self.access_token)
                
                # Set up callbacks
                self._ticker.on_ticks = self._on_ticks
                self._ticker.on_connect = self._on_connect
                self._ticker.on_close = self._on_close
                self._ticker.on_error = self._on_error
                self._ticker.on_reconnect = self._on_reconnect
                self._ticker.on_noreconnect = self._on_noreconnect
                
                logger.debug("KiteTicker instance created")
                
            except ImportError:
                raise ImportError(
                    "kiteconnect package not installed or doesn't support WebSocket. "
                    "Install with: pip install kiteconnect"
                )
        
        return self._ticker
    
    def connect(self, threaded: bool = True) -> None:
        """
        Connect to WebSocket.
        
        Args:
            threaded: Run in separate thread (non-blocking)
        """
        ticker = self._get_ticker()
        
        logger.info("Connecting to Zerodha WebSocket...")
        
        if threaded:
            ticker.connect(threaded=True)
        else:
            ticker.connect(threaded=False)
    
    def close(self) -> None:
        """Close WebSocket connection."""
        if self._ticker:
            logger.info("Closing WebSocket connection...")
            self._ticker.close()
            self._connected = False
    
    def subscribe(self, tokens: List[int], mode: str = MODE_QUOTE) -> None:
        """
        Subscribe to instruments.
        
        Args:
            tokens: List of instrument tokens to subscribe
            mode: Tick mode ('ltp', 'quote', 'full')
        """
        if not self._ticker:
            logger.warning("Not connected, cannot subscribe")
            return
        
        # Save subscriptions for reconnection
        self._subscribed_tokens.extend([t for t in tokens if t not in self._subscribed_tokens])
        self._subscription_mode = mode
        
        # Subscribe
        self._ticker.subscribe(tokens)
        
        # Set mode
        if mode == self.MODE_LTP:
            self._ticker.set_mode(self._ticker.MODE_LTP, tokens)
        elif mode == self.MODE_QUOTE:
            self._ticker.set_mode(self._ticker.MODE_QUOTE, tokens)
        elif mode == self.MODE_FULL:
            self._ticker.set_mode(self._ticker.MODE_FULL, tokens)
        
        logger.info(f"Subscribed to {len(tokens)} instruments in {mode} mode")
    
    def unsubscribe(self, tokens: List[int]) -> None:
        """
        Unsubscribe from instruments.
        
        Args:
            tokens: List of instrument tokens to unsubscribe
        """
        if not self._ticker:
            return
        
        self._ticker.unsubscribe(tokens)
        
        # Remove from saved subscriptions
        self._subscribed_tokens = [t for t in self._subscribed_tokens if t not in tokens]
        
        logger.info(f"Unsubscribed from {len(tokens)} instruments")
    
    def resubscribe(self) -> None:
        """Resubscribe to all saved subscriptions (used after reconnect)."""
        if self._subscribed_tokens:
            logger.info(f"Resubscribing to {len(self._subscribed_tokens)} instruments")
            self.subscribe(self._subscribed_tokens, self._subscription_mode)
    
    # Callback registration
    
    def on_ticks(self, callback: Callable) -> None:
        """Register tick callback."""
        self._tick_callbacks.append(callback)
    
    def on_connect(self, callback: Callable) -> None:
        """Register connect callback."""
        self._connect_callbacks.append(callback)
    
    def on_error(self, callback: Callable) -> None:
        """Register error callback."""
        self._error_callbacks.append(callback)
    
    def on_close(self, callback: Callable) -> None:
        """Register close callback."""
        self._close_callbacks.append(callback)
    
    # Internal callbacks (from KiteTicker)
    
    def _on_ticks(self, ws, ticks: List[Dict]) -> None:
        """Handle incoming ticks."""
        self.ticks_received += len(ticks)
        self.last_tick_time = datetime.now()
        
        logger.trace(f"Received {len(ticks)} ticks")
        
        # Call registered callbacks
        for callback in self._tick_callbacks:
            try:
                callback(ticks)
            except Exception as e:
                logger.error(f"Error in tick callback: {e}")
        
        # Publish to event bus if configured
        if self.event_bus:
            for tick in ticks:
                self._publish_tick_event(tick)
    
    def _on_connect(self, ws, response) -> None:
        """Handle connection."""
        self._connected = True
        self._reconnect_count = 0
        self.connection_time = datetime.now()
        
        logger.info(f"✅ Connected to WebSocket")
        
        # Resubscribe to saved subscriptions
        self.resubscribe()
        
        # Call registered callbacks
        for callback in self._connect_callbacks:
            try:
                callback(response)
            except Exception as e:
                logger.error(f"Error in connect callback: {e}")
        
        # Publish system event
        if self.event_bus:
            self.event_bus.publish(Event(
                priority=0,
                event_type=EventType.SYSTEM_START,
                timestamp=datetime.now(),
                data={"component": "websocket", "status": "connected"},
                source="zerodha_websocket"
            ))
    
    def _on_close(self, ws, code, reason) -> None:
        """Handle connection close."""
        self._connected = False
        
        logger.warning(f"WebSocket closed: {code} - {reason}")
        
        # Call registered callbacks
        for callback in self._close_callbacks:
            try:
                callback(code, reason)
            except Exception as e:
                logger.error(f"Error in close callback: {e}")
        
        # Publish system event
        if self.event_bus:
            self.event_bus.publish(Event(
                priority=0,
                event_type=EventType.SYSTEM_STOP,
                timestamp=datetime.now(),
                data={"component": "websocket", "code": code, "reason": reason},
                source="zerodha_websocket"
            ))
    
    def _on_error(self, ws, code, reason) -> None:
        """Handle error."""
        logger.error(f"WebSocket error: {code} - {reason}")
        
        # Call registered callbacks
        for callback in self._error_callbacks:
            try:
                callback(code, reason)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
        
        # Publish error event
        if self.event_bus:
            self.event_bus.publish(Event(
                priority=0,
                event_type=EventType.SYSTEM_ERROR,
                timestamp=datetime.now(),
                data={"component": "websocket", "code": code, "reason": reason},
                source="zerodha_websocket"
            ))
    
    def _on_reconnect(self, ws, attempts_count) -> None:
        """Handle reconnection attempt."""
        self._reconnect_count = attempts_count
        logger.info(f"Reconnecting... (attempt {attempts_count})")
    
    def _on_noreconnect(self, ws) -> None:
        """Handle reconnection failure."""
        logger.error("Max reconnection attempts reached, giving up")
        self._connected = False
    
    def _publish_tick_event(self, tick: Dict) -> None:
        """
        Publish tick as market data event.
        
        Args:
            tick: Tick data from Kite WebSocket
        """
        # Convert Kite tick to QuantX event
        event = Event(
            priority=1,
            event_type=EventType.TICK,
            timestamp=tick.get('exchange_timestamp') or tick.get('timestamp') or datetime.now(),
            data={
                'instrument_token': tick.get('instrument_token'),
                'symbol': tick.get('tradable', True),  # Will be enriched with symbol lookup
                'last_price': tick.get('last_price'),
                'volume': tick.get('volume'),
                'buy_quantity': tick.get('buy_quantity'),
                'sell_quantity': tick.get('sell_quantity'),
                'change': tick.get('change'),
                'last_trade_time': tick.get('last_trade_time'),
                'oi': tick.get('oi'),  # Open interest (for F&O)
                'ohlc': tick.get('ohlc'),
                'depth': tick.get('depth'),  # Market depth (for full mode)
                'raw_tick': tick
            },
            source="zerodha_websocket"
        )
        
        self.event_bus.publish(event)
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket statistics."""
        uptime = None
        if self.connection_time:
            uptime = (datetime.now() - self.connection_time).total_seconds()
        
        return {
            'connected': self._connected,
            'ticks_received': self.ticks_received,
            'subscribed_instruments': len(self._subscribed_tokens),
            'connection_time': self.connection_time.isoformat() if self.connection_time else None,
            'uptime_seconds': uptime,
            'last_tick_time': self.last_tick_time.isoformat() if self.last_tick_time else None,
            'reconnect_count': self._reconnect_count
        }


class LiveDataProvider:
    """
    Live data provider for real-time market data.
    
    Manages WebSocket connection and provides a clean interface
    for subscribing to live market data.
    
    Example:
        >>> provider = LiveDataProvider(broker, event_bus)
        >>> provider.connect()
        >>> provider.subscribe_symbols(["NSE:INFY", "NSE:TCS"])
        >>> # Data flows automatically via event bus
    """
    
    def __init__(
        self,
        api_key: str,
        access_token: str,
        event_bus: EventBus,
        instrument_lookup: Optional[Dict[str, int]] = None
    ):
        """
        Initialize live data provider.
        
        Args:
            api_key: Zerodha API key
            access_token: Valid access token
            event_bus: EventBus for publishing data
            instrument_lookup: Optional dict mapping symbols to instrument tokens
        """
        self.api_key = api_key
        self.access_token = access_token
        self.event_bus = event_bus
        self.instrument_lookup = instrument_lookup or {}
        
        # WebSocket client
        self.websocket = ZerodhaWebSocket(
            api_key=api_key,
            access_token=access_token,
            event_bus=event_bus
        )
        
        # Subscribed symbols
        self._subscribed_symbols: List[str] = []
        
        logger.info("LiveDataProvider initialized")
    
    def connect(self) -> None:
        """Connect to live data stream."""
        self.websocket.connect(threaded=True)
        logger.info("Connected to live data stream")
    
    def disconnect(self) -> None:
        """Disconnect from live data stream."""
        self.websocket.close()
        logger.info("Disconnected from live data stream")
    
    def subscribe_symbols(self, symbols: List[str], mode: str = "quote") -> None:
        """
        Subscribe to symbols for live data.
        
        Args:
            symbols: List of symbols (e.g., ["NSE:INFY", "NSE:TCS"])
            mode: Data mode ('ltp', 'quote', 'full')
        """
        # Convert symbols to instrument tokens
        tokens = []
        for symbol in symbols:
            token = self.instrument_lookup.get(symbol)
            if token:
                tokens.append(token)
                self._subscribed_symbols.append(symbol)
            else:
                logger.warning(f"Instrument token not found for {symbol}")
        
        if tokens:
            self.websocket.subscribe(tokens, mode=mode)
            logger.info(f"Subscribed to {len(tokens)} symbols")
    
    def unsubscribe_symbols(self, symbols: List[str]) -> None:
        """
        Unsubscribe from symbols.
        
        Args:
            symbols: List of symbols to unsubscribe
        """
        tokens = []
        for symbol in symbols:
            token = self.instrument_lookup.get(symbol)
            if token:
                tokens.append(token)
                if symbol in self._subscribed_symbols:
                    self._subscribed_symbols.remove(symbol)
        
        if tokens:
            self.websocket.unsubscribe(tokens)
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.websocket.is_connected()
    
    def get_subscribed_symbols(self) -> List[str]:
        """Get list of subscribed symbols."""
        return self._subscribed_symbols.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        stats = self.websocket.get_statistics()
        stats['subscribed_symbols'] = self._subscribed_symbols
        return stats
