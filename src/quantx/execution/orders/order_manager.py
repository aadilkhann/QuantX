"""
Order Management System (OMS).

Centralized system for managing order lifecycle, validation, routing, and fill processing.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from collections import defaultdict
import uuid
from loguru import logger

from quantx.execution.brokers.base import (
    IBroker, Order, Fill, OrderStatus, OrderSide, OrderType
)


class OrderValidator:
    """
    Validates orders before submission.
    
    Performs pre-trade checks to ensure orders are valid.
    """
    
    def __init__(self):
        """Initialize validator."""
        self.validation_rules: List[Callable[[Order], tuple[bool, str]]] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules."""
        self.add_rule(self._validate_quantity)
        self.add_rule(self._validate_prices)
        self.add_rule(self._validate_symbol)
    
    def add_rule(self, rule: Callable[[Order], tuple[bool, str]]):
        """
        Add a validation rule.
        
        Args:
            rule: Function that takes an order and returns (is_valid, error_message)
        """
        self.validation_rules.append(rule)
    
    def validate(self, order: Order) -> tuple[bool, Optional[str]]:
        """
        Validate an order against all rules.
        
        Args:
            order: Order to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for rule in self.validation_rules:
            is_valid, error = rule(order)
            if not is_valid:
                return False, error
        
        return True, None
    
    @staticmethod
    def _validate_quantity(order: Order) -> tuple[bool, str]:
        """Validate order quantity."""
        if order.quantity <= 0:
            return False, f"Invalid quantity: {order.quantity}"
        return True, ""
    
    @staticmethod
    def _validate_prices(order: Order) -> tuple[bool, str]:
        """Validate order prices."""
        if order.order_type == OrderType.LIMIT and order.price is None:
            return False, "Limit order requires price"
        
        if order.order_type == OrderType.LIMIT and order.price <= 0:
            return False, f"Invalid limit price: {order.price}"
        
        if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
            if order.stop_price is None:
                return False, "Stop order requires stop price"
            if order.stop_price <= 0:
                return False, f"Invalid stop price: {order.stop_price}"
        
        return True, ""
    
    @staticmethod
    def _validate_symbol(order: Order) -> tuple[bool, str]:
        """Validate symbol."""
        if not order.symbol or len(order.symbol) == 0:
            return False, "Symbol is required"
        return True, ""


class OrderManager:
    """
    Central Order Management System.
    
    Manages order lifecycle, validation, routing, and fill processing.
    
    Features:
    - Order validation
    - Order queue management
    - Routing to brokers
    - Fill processing
    - Order tracking
    - Trade logging
    
    Example:
        >>> oms = OrderManager(broker)
        >>> order_id = oms.submit_order(order)
        >>> oms.cancel_order(order_id)
    """
    
    def __init__(
        self,
        broker: IBroker,
        enable_validation: bool = True,
        log_trades: bool = True
    ):
        """
        Initialize Order Manager.
        
        Args:
            broker: Broker to route orders to
            enable_validation: Enable order validation
            log_trades: Enable trade logging
        """
        self.broker = broker
        self.enable_validation = enable_validation
        self.log_trades = log_trades
        
        # Validator
        self.validator = OrderValidator()
        
        # Order tracking
        self.orders: Dict[str, Order] = {}
        self.fills: List[Fill] = []
        self.pending_orders: List[str] = []
        
        # Event callbacks
        self.on_order_submitted: List[Callable[[Order], None]] = []
        self.on_order_filled: List[Callable[[Order], None]] = []
        self.on_order_cancelled: List[Callable[[Order], None]] = []
        self.on_order_rejected: List[Callable[[Order, str], None]] = []
        self.on_fill_received: List[Callable[[Fill], None]] = []
        
        # Statistics
        self.stats = {
            "orders_submitted": 0,
            "orders_filled": 0,
            "orders_cancelled": 0,
            "orders_rejected": 0,
            "total_fills": 0
        }
        
        logger.info(f"Initialized Order Manager with {broker.name} broker")
    
    def submit_order(self, order: Order) -> Optional[str]:
        """
        Submit an order for execution.
        
        Args:
            order: Order to submit
            
        Returns:
            Order ID if successful, None if rejected
        """
        # Generate order ID if not provided
        if not order.order_id:
            order.order_id = f"oms_{uuid.uuid4().hex[:12]}"
        
        # Validate order
        if self.enable_validation:
            is_valid, error = self.validator.validate(order)
            if not is_valid:
                logger.error(f"Order validation failed: {error}")
                order.status = OrderStatus.REJECTED
                self.orders[order.order_id] = order
                self.stats["orders_rejected"] += 1
                self._trigger_callbacks(self.on_order_rejected, order, error)
                return None
        
        try:
            # Submit to broker
            broker_order_id = self.broker.place_order(order)
            
            if broker_order_id:
                # Track order
                self.orders[order.order_id] = order
                if order.is_open:
                    self.pending_orders.append(order.order_id)
                
                # Update stats
                self.stats["orders_submitted"] += 1
                
                # Trigger callbacks
                self._trigger_callbacks(self.on_order_submitted, order)
                
                logger.info(f"Order submitted: {order.order_id} - {order.side.value} {order.quantity} {order.symbol}")
                return order.order_id
            else:
                order.status = OrderStatus.REJECTED
                self.orders[order.order_id] = order
                self.stats["orders_rejected"] += 1
                self._trigger_callbacks(self.on_order_rejected, order, "Broker rejected order")
                return None
        
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            order.status = OrderStatus.REJECTED
            self.orders[order.order_id] = order
            self.stats["orders_rejected"] += 1
            self._trigger_callbacks(self.on_order_rejected, order, str(e))
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful
        """
        if order_id not in self.orders:
            logger.error(f"Order not found: {order_id}")
            return False
        
        order = self.orders[order_id]
        
        if not order.is_open:
            logger.warning(f"Cannot cancel order in status: {order.status}")
            return False
        
        try:
            # Cancel with broker
            success = self.broker.cancel_order(order_id)
            
            if success:
                # Update order
                order.status = OrderStatus.CANCELLED
                
                # Remove from pending
                if order_id in self.pending_orders:
                    self.pending_orders.remove(order_id)
                
                # Update stats
                self.stats["orders_cancelled"] += 1
                
                # Trigger callbacks
                self._trigger_callbacks(self.on_order_cancelled, order)
                
                logger.info(f"Order cancelled: {order_id}")
                return True
            else:
                logger.error(f"Broker failed to cancel order: {order_id}")
                return False
        
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def process_fill(self, fill: Fill):
        """
        Process a fill/execution.
        
        Args:
            fill: Fill to process
        """
        # Store fill
        self.fills.append(fill)
        self.stats["total_fills"] += 1
        
        # Update order if we're tracking it
        if fill.order_id in self.orders:
            order = self.orders[fill.order_id]
            
            # Update fill quantities
            order.filled_quantity += fill.quantity
            
            # Update average fill price
            if order.filled_quantity > 0:
                total_value = order.average_fill_price * (order.filled_quantity - fill.quantity)
                total_value += fill.price * fill.quantity
                order.average_fill_price = total_value / order.filled_quantity
            
            # Update status
            if order.filled_quantity >= order.quantity:
                order.status = OrderStatus.FILLED
                order.filled_at = fill.timestamp
                
                # Remove from pending
                if fill.order_id in self.pending_orders:
                    self.pending_orders.remove(fill.order_id)
                
                # Update stats
                self.stats["orders_filled"] += 1
                
                # Trigger callbacks
                self._trigger_callbacks(self.on_order_filled, order)
                
                logger.info(f"Order filled: {fill.order_id} - {fill.quantity} @ ${fill.price:.2f}")
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
                logger.info(f"Partial fill: {fill.order_id} - {fill.quantity} @ ${fill.price:.2f}")
        
        # Trigger fill callbacks
        self._trigger_callbacks(self.on_fill_received, fill)
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)
    
    def get_open_orders(self) -> List[Order]:
        """Get all open orders."""
        return [
            self.orders[order_id]
            for order_id in self.pending_orders
            if order_id in self.orders
        ]
    
    def get_filled_orders(self) -> List[Order]:
        """Get all filled orders."""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.FILLED
        ]
    
    def get_fills(self, order_id: Optional[str] = None) -> List[Fill]:
        """
        Get fills.
        
        Args:
            order_id: Optional order ID to filter by
            
        Returns:
            List of fills
        """
        if order_id:
            return [fill for fill in self.fills if fill.order_id == order_id]
        return self.fills
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get OMS statistics."""
        return {
            **self.stats,
            "open_orders": len(self.pending_orders),
            "total_orders": len(self.orders),
            "fill_rate": (
                self.stats["orders_filled"] / self.stats["orders_submitted"]
                if self.stats["orders_submitted"] > 0 else 0
            )
        }
    
    def register_callback(
        self,
        event: str,
        callback: Callable
    ):
        """
        Register a callback for an event.
        
        Args:
            event: Event name (order_submitted, order_filled, order_cancelled, order_rejected, fill_received)
            callback: Callback function
        """
        callbacks_map = {
            "order_submitted": self.on_order_submitted,
            "order_filled": self.on_order_filled,
            "order_cancelled": self.on_order_cancelled,
            "order_rejected": self.on_order_rejected,
            "fill_received": self.on_fill_received
        }
        
        if event in callbacks_map:
            callbacks_map[event].append(callback)
            logger.info(f"Registered callback for event: {event}")
        else:
            logger.warning(f"Unknown event: {event}")
    
    def _trigger_callbacks(self, callbacks: List[Callable], *args):
        """Trigger callbacks with error handling."""
        for callback in callbacks:
            try:
                callback(*args)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    def reset(self):
        """Reset OMS state."""
        self.orders.clear()
        self.fills.clear()
        self.pending_orders.clear()
        
        # Reset stats
        for key in self.stats:
            self.stats[key] = 0
        
        logger.info("Reset Order Manager")


class MultiOrderManager:
    """
    Manages orders across multiple brokers.
    
    Allows routing orders to different brokers based on rules or manual selection.
    """
    
    def __init__(self):
        """Initialize multi-broker order manager."""
        self.managers: Dict[str, OrderManager] = {}
        self.default_broker: Optional[str] = None
        logger.info("Initialized Multi-Broker Order Manager")
    
    def add_broker(
        self,
        name: str,
        broker: IBroker,
        set_as_default: bool = False
    ):
        """
        Add a broker.
        
        Args:
            name: Broker name
            broker: Broker instance
            set_as_default: Set as default broker
        """
        self.managers[name] = OrderManager(broker)
        
        if set_as_default or self.default_broker is None:
            self.default_broker = name
        
        logger.info(f"Added broker: {name}")
    
    def submit_order(
        self,
        order: Order,
        broker_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Submit order to a specific broker.
        
        Args:
            order: Order to submit
            broker_name: Broker name (uses default if not specified)
            
        Returns:
            Order ID if successful
        """
        if broker_name is None:
            broker_name = self.default_broker
        
        if broker_name not in self.managers:
            logger.error(f"Unknown broker: {broker_name}")
            return None
        
        return self.managers[broker_name].submit_order(order)
    
    def get_manager(self, broker_name: str) -> Optional[OrderManager]:
        """Get order manager for a broker."""
        return self.managers.get(broker_name)
    
    def get_all_open_orders(self) -> Dict[str, List[Order]]:
        """Get open orders from all brokers."""
        return {
            name: manager.get_open_orders()
            for name, manager in self.managers.items()
        }
    
    def get_combined_statistics(self) -> Dict[str, Any]:
        """Get combined statistics from all brokers."""
        combined = defaultdict(int)
        
        for manager in self.managers.values():
            stats = manager.get_statistics()
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    combined[key] += value
        
        return dict(combined)
