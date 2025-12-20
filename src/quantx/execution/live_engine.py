"""
Live Execution Engine for QuantX.

Provides event-driven live trading framework that connects strategies with
brokers, order management, and risk management systems.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from threading import Thread, Event as ThreadEvent
import time

from loguru import logger

from quantx.core.events import Event, EventBus, EventType
from quantx.execution.brokers.base import IBroker, Order, OrderType, OrderSide, OrderStatus
from quantx.execution.orders import OrderManager
from quantx.execution.risk import RiskManager
from quantx.strategies.base import BaseStrategy, Action


class EngineState(Enum):
    """Live execution engine states."""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    """Live execution engine configuration."""
    position_sync_interval: int = 60  # seconds
    heartbeat_interval: int = 10  # seconds
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 5  # seconds
    enable_logging: bool = True
    dry_run: bool = False  # If True, don't actually place orders


class LiveExecutionEngine:
    """
    Live execution engine.
    
    Event-driven engine that coordinates live trading between strategies,
    brokers, order management, and risk controls.
    
    Architecture:
        Strategy -> Signal -> OMS -> Risk Check -> Broker -> Fill -> Position Sync
    
    Example:
        >>> engine = LiveExecutionEngine(strategy, broker, oms, risk_manager)
        >>> engine.start()
        >>> # ... trading happens ...
        >>> engine.stop()
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        broker: IBroker,
        order_manager: OrderManager,
        risk_manager: RiskManager,
        event_bus: Optional[EventBus] = None,
        config: Optional[EngineConfig] = None
    ):
        """
        Initialize live execution engine.
        
        Args:
            strategy: Trading strategy instance
            broker: Broker instance
            order_manager: Order management system
            risk_manager: Risk manager
            event_bus: Event bus (creates new if None)
            config: Engine configuration
        """
        self.strategy = strategy
        self.broker = broker
        self.order_manager = order_manager
        self.risk_manager = risk_manager
        self.event_bus = event_bus or EventBus()
        self.config = config or EngineConfig()
        
        # State
        self.state = EngineState.CREATED
        self._stop_event = ThreadEvent()
        self._sync_thread: Optional[Thread] = None
        self._heartbeat_thread: Optional[Thread] = None
        
        # Statistics
        self.start_time: Optional[datetime] = None
        self.signals_received = 0
        self.orders_submitted = 0
        self.orders_filled = 0
        self.orders_rejected = 0
        
        # Callbacks
        self._status_callbacks: List[Callable] = []
        self._error_callbacks: List[Callable] = []
        
        # Setup
        self._setup_event_subscriptions()
        logger.info(f"LiveExecutionEngine initialized for strategy '{strategy.name}'")
    
    def _setup_event_subscriptions(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe(EventType.SIGNAL, self._on_signal)
        self.event_bus.subscribe(EventType.FILL, self._on_fill)
        self.event_bus.subscribe(EventType.ORDER_SUBMITTED, self._on_order_submitted)
        self.event_bus.subscribe(EventType.ORDER_REJECTED, self._on_order_rejected)
        self.event_bus.subscribe(EventType.MARKET_DATA, self._on_market_data)
        self.event_bus.subscribe(EventType.RISK_VIOLATION, self._on_risk_violation)
        
        logger.debug("Event subscriptions configured")
    
    def start(self) -> bool:
        """
        Start live trading.
        
        Returns:
            True if started successfully
        """
        if self.state in [EngineState.RUNNING, EngineState.STARTING]:
            logger.warning("Engine already running or starting")
            return False
        
        logger.info("Starting LiveExecutionEngine...")
        self.state = EngineState.STARTING
        
        try:
            # Connect to broker
            if not self.broker.is_connected():
                logger.info("Connecting to broker...")
                if not self.broker.connect():
                    raise Exception("Failed to connect to broker")
                logger.info("Connected to broker successfully")
            
            # Start event bus
            if not self.event_bus._running:
                self.event_bus.start()
            
            # Setup strategy
            self.strategy.set_event_bus(self.event_bus)
            self.strategy.on_start()
            
            # Initial position sync
            self._sync_positions()
            
            # Start background threads
            self._start_background_threads()
            
            # Update state
            self.state = EngineState.RUNNING
            self.start_time = datetime.now()
            self._stop_event.clear()
            
            # Publish system start event
            self.event_bus.publish(Event(
                priority=0,
                event_type=EventType.SYSTEM_START,
                timestamp=datetime.now(),
                data={"engine": "live_execution"},
                source="live_engine"
            ))
            
            logger.info("✅ LiveExecutionEngine started successfully")
            return True
            
        except Exception as e:
            self.state = EngineState.ERROR
            logger.error(f"Failed to start engine: {e}")
            self._notify_error(e)
            return False
    
    def stop(self, timeout: float = 30.0) -> None:
        """
        Stop live trading gracefully.
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        if self.state == EngineState.STOPPED:
            logger.warning("Engine already stopped")
            return
        
        logger.info("Stopping LiveExecutionEngine...")
        self.state = EngineState.STOPPING
        self._stop_event.set()
        
        try:
            # Stop strategy
            self.strategy.on_stop()
            
            # Cancel all open orders
            open_orders = self.broker.get_open_orders()
            for order in open_orders:
                logger.info(f"Cancelling open order: {order.order_id}")
                self.broker.cancel_order(order.order_id)
            
            # Stop background threads
            if self._sync_thread and self._sync_thread.is_alive():
                self._sync_thread.join(timeout=timeout/2)
            
            if self._heartbeat_thread and self._heartbeat_thread.is_alive():
                self._heartbeat_thread.join(timeout=timeout/2)
            
            # Stop event bus
            self.event_bus.stop(timeout=timeout/2)
            
            # Final position sync
            self._sync_positions()
            
            # Publish system stop event
            self.event_bus.publish(Event(
                priority=0,
                event_type=EventType.SYSTEM_STOP,
                timestamp=datetime.now(),
                data=self.get_statistics(),
                source="live_engine"
            ))
            
            self.state = EngineState.STOPPED
            logger.info("✅ LiveExecutionEngine stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.state = EngineState.ERROR
    
    def pause(self) -> None:
        """Pause live trading (stops signal processing but maintains positions)."""
        if self.state != EngineState.RUNNING:
            logger.warning("Engine not running, cannot pause")
            return
        
        logger.info("Pausing LiveExecutionEngine...")
        self.state = EngineState.PAUSED
        logger.info("Engine paused - signals will be ignored")
    
    def resume(self) -> None:
        """Resume live trading."""
        if self.state != EngineState.PAUSED:
            logger.warning("Engine not paused, cannot resume")
            return
        
        logger.info("Resuming LiveExecutionEngine...")
        self.state = EngineState.RUNNING
        logger.info("Engine resumed")
    
    def _start_background_threads(self) -> None:
        """Start background monitoring threads."""
        # Position synchronization thread
        self._sync_thread = Thread(
            target=self._position_sync_loop,
            daemon=True,
            name="PositionSync"
        )
        self._sync_thread.start()
        
        # Heartbeat thread
        self._heartbeat_thread = Thread(
            target=self._heartbeat_loop,
            daemon=True,
            name="Heartbeat"
        )
        self._heartbeat_thread.start()
        
        logger.debug("Background threads started")
    
    def _position_sync_loop(self) -> None:
        """Background thread for position synchronization."""
        logger.debug("Position sync thread started")
        
        while not self._stop_event.is_set():
            try:
                self._sync_positions()
                self._stop_event.wait(self.config.position_sync_interval)
            except Exception as e:
                logger.error(f"Error in position sync loop: {e}")
        
        logger.debug("Position sync thread stopped")
    
    def _heartbeat_loop(self) -> None:
        """Background thread for heartbeat."""
        logger.debug("Heartbeat thread started")
        
        while not self._stop_event.is_set():
            try:
                # Publish heartbeat event
                self.event_bus.publish(Event(
                    priority=5,
                    event_type=EventType.HEARTBEAT,
                    timestamp=datetime.now(),
                    data={
                        "state": self.state.value,
                        "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                    },
                    source="live_engine"
                ))
                
                # Check connection
                if self.state == EngineState.RUNNING and not self.broker.is_connected():
                    logger.warning("Broker connection lost, attempting to reconnect...")
                    self._handle_disconnect()
                
                self._stop_event.wait(self.config.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
        
        logger.debug("Heartbeat thread stopped")
    
    def _sync_positions(self) -> None:
        """Synchronize positions with broker."""
        try:
            broker_positions = self.broker.get_positions()
            
            # Update strategy positions
            for position in broker_positions:
                self.strategy._positions[position.symbol] = int(position.quantity)
            
            logger.debug(f"Positions synced: {len(broker_positions)} positions")
            
        except Exception as e:
            logger.error(f"Position sync failed: {e}")
    
    def _handle_disconnect(self) -> None:
        """Handle broker disconnection."""
        for attempt in range(self.config.max_reconnect_attempts):
            logger.info(f"Reconnection attempt {attempt + 1}/{self.config.max_reconnect_attempts}")
            
            try:
                if self.broker.connect():
                    logger.info("Reconnected successfully")
                    self._sync_positions()  # Resync after reconnect
                    return
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
            
            time.sleep(self.config.reconnect_delay)
        
        logger.error("Max reconnection attempts reached, stopping engine")
        self.stop()
    
    # Event Handlers
    
    def _on_signal(self, event: Event) -> None:
        """Handle strategy signal."""
        if self.state != EngineState.RUNNING:
            logger.debug("Ignoring signal - engine not running")
            return
        
        self.signals_received += 1
        signal_data = event.data
        
        logger.info(f"📊 Signal received: {signal_data['action']} {signal_data['symbol']} x{signal_data['quantity']}")
        
        # Convert signal to order
        order = self._signal_to_order(signal_data)
        
        if self.config.dry_run:
            logger.info(f"DRY RUN: Would place order {order}")
            return
        
        # Submit via OMS (which includes risk checks)
        try:
            order_id = self.order_manager.submit_order(order)
            logger.info(f"Order submitted via OMS: {order_id}")
        except Exception as e:
            logger.error(f"Failed to submit order: {e}")
            self.orders_rejected += 1
    
    def _on_fill(self, event: Event) -> None:
        """Handle order fill."""
        self.orders_filled += 1
        fill_data = event.data
        
        logger.info(f"✅ Fill received: {fill_data.get('symbol')} x{fill_data.get('quantity')} @ {fill_data.get('price')}")
        
        # Forward to strategy
        self.strategy.on_fill(event)
        
        # Trigger position sync
        self._sync_positions()
    
    def _on_order_submitted(self, event: Event) -> None:
        """Handle order submission."""
        self.orders_submitted += 1
        logger.debug(f"Order submitted: {event.data}")
    
    def _on_order_rejected(self, event: Event) -> None:
        """Handle order rejection."""
        self.orders_rejected += 1
        logger.warning(f"⚠️ Order rejected: {event.data}")
    
    def _on_market_data(self, event: Event) -> None:
        """Handle market data."""
        # Forward to strategy
        self.strategy.on_data(event)
    
    def _on_risk_violation(self, event: Event) -> None:
        """Handle risk violation."""
        violation = event.data
        logger.warning(f"🚨 Risk violation: {violation}")
        
        # If critical, pause engine
        if violation.get('severity') == 'critical':
            logger.error("Critical risk violation - pausing engine")
            self.pause()
    
    def _signal_to_order(self, signal_data: Dict[str, Any]) -> Order:
        """
        Convert strategy signal to broker order.
        
        Args:
            signal_data: Signal data dictionary
            
        Returns:
            Order object
        """
        action = Action(signal_data['action']) if isinstance(signal_data['action'], str) else signal_data['action']
        
        return Order(
            order_id="",  # Will be assigned by broker
            symbol=signal_data['symbol'],
            side=OrderSide.BUY if action == Action.BUY else OrderSide.SELL,
            order_type=OrderType.LIMIT if signal_data.get('price') else OrderType.MARKET,
            quantity=float(signal_data['quantity']),
            price=signal_data.get('price'),
            metadata={
                'strategy': signal_data.get('strategy'),
                'signal_timestamp': signal_data.get('timestamp')
            }
        )
    
    # Status and Monitoring
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current engine status.
        
        Returns:
            Status dictionary
        """
        return {
            'state': self.state.value,
            'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'broker_connected': self.broker.is_connected(),
            'strategy': self.strategy.name,
            'event_bus_stats': self.event_bus.get_stats()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get trading statistics.
        
        Returns:
            Statistics dictionary
        """
        account = self.broker.get_account()
        positions = self.broker.get_positions()
        
        return {
            'engine': {
                'state': self.state.value,
                'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                'signals_received': self.signals_received,
                'orders_submitted': self.orders_submitted,
                'orders_filled': self.orders_filled,
                'orders_rejected': self.orders_rejected
            },
            'account': {
                'equity': account.equity,
                'cash': account.cash,
                'unrealized_pnl': account.unrealized_pnl,
                'realized_pnl': account.realized_pnl,
                'total_pnl': account.total_pnl,
                'return_pct': account.return_pct
            },
            'positions': {
                'count': len(positions),
                'symbols': [p.symbol for p in positions]
            },
            'oms': self.order_manager.get_statistics(),
            'risk': self.risk_manager.get_status()
        }
    
    def register_status_callback(self, callback: Callable) -> None:
        """Register callback for status updates."""
        self._status_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable) -> None:
        """Register callback for errors."""
        self._error_callbacks.append(callback)
    
    def _notify_status(self, status: Dict[str, Any]) -> None:
        """Notify status callbacks."""
        for callback in self._status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def _notify_error(self, error: Exception) -> None:
        """Notify error callbacks."""
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
