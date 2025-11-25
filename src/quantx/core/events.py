"""
Event System for QuantX

Implements an event-driven architecture with pub/sub pattern for loose coupling
between components.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import PriorityQueue, Empty
from threading import Thread, Event as ThreadEvent
from typing import Any, Callable, Dict, List, Optional
from loguru import logger


class EventType(Enum):
    """Types of events in the system"""

    # Market Data Events
    MARKET_DATA = "market_data"
    TICK = "tick"
    BAR = "bar"

    # Strategy Events
    SIGNAL = "signal"

    # Order Events
    ORDER = "order"
    ORDER_SUBMITTED = "order_submitted"
    ORDER_ACCEPTED = "order_accepted"
    ORDER_REJECTED = "order_rejected"
    ORDER_CANCELLED = "order_cancelled"

    # Fill Events
    FILL = "fill"
    PARTIAL_FILL = "partial_fill"

    # Position Events
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    POSITION_UPDATED = "position_updated"

    # Risk Events
    RISK_VIOLATION = "risk_violation"
    RISK_WARNING = "risk_warning"

    # System Events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"
    HEARTBEAT = "heartbeat"


@dataclass(order=True)
class Event:
    """
    Base event class for all events in the system

    Events are prioritized and processed in order. Lower priority values
    are processed first.
    """

    priority: int = field(compare=True)
    event_type: EventType = field(compare=False)
    timestamp: datetime = field(compare=False)
    data: Any = field(compare=False)
    source: str = field(compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        """Validate event after initialization"""
        if not isinstance(self.event_type, EventType):
            raise ValueError(f"event_type must be EventType, got {type(self.event_type)}")
        if not isinstance(self.timestamp, datetime):
            raise ValueError(f"timestamp must be datetime, got {type(self.timestamp)}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "priority": self.priority,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source,
            "metadata": self.metadata,
        }


class EventBus:
    """
    Event bus for pub/sub event routing

    Provides thread-safe event publishing and subscription with priority-based
    processing.
    """

    def __init__(self, max_queue_size: int = 10000) -> None:
        """
        Initialize event bus

        Args:
            max_queue_size: Maximum number of events in queue
        """
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._event_queue: PriorityQueue = PriorityQueue(maxsize=max_queue_size)
        self._running = False
        self._stop_event = ThreadEvent()
        self._thread: Optional[Thread] = None
        self._event_count = 0
        self._error_count = 0

        logger.info("EventBus initialized with max_queue_size={}", max_queue_size)

    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type

        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(handler)
        logger.debug(
            "Subscribed {} to {} (total subscribers: {})",
            handler.__name__,
            event_type.value,
            len(self._subscribers[event_type]),
        )

    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug("Unsubscribed {} from {}", handler.__name__, event_type.value)
            except ValueError:
                logger.warning(
                    "Handler {} not found in subscribers for {}", handler.__name__, event_type.value
                )

    def publish(self, event: Event) -> None:
        """
        Publish an event to the bus

        Args:
            event: Event to publish
        """
        try:
            self._event_queue.put(event, block=False)
            logger.trace("Published event: {} from {}", event.event_type.value, event.source)
        except Exception as e:
            logger.error("Failed to publish event: {}", e)
            raise

    def start(self) -> None:
        """Start processing events"""
        if self._running:
            logger.warning("EventBus already running")
            return

        self._running = True
        self._stop_event.clear()
        self._thread = Thread(target=self._process_events, daemon=True, name="EventBus")
        self._thread.start()
        logger.info("EventBus started")

    def stop(self, timeout: float = 5.0) -> None:
        """
        Stop processing events

        Args:
            timeout: Maximum time to wait for thread to stop
        """
        if not self._running:
            logger.warning("EventBus not running")
            return

        logger.info("Stopping EventBus...")
        self._running = False
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("EventBus thread did not stop within timeout")
            else:
                logger.info("EventBus stopped successfully")

        logger.info(
            "EventBus stats - Total events: {}, Errors: {}", self._event_count, self._error_count
        )

    def _process_events(self) -> None:
        """Process events from queue (runs in separate thread)"""
        logger.debug("Event processing thread started")

        while self._running:
            try:
                # Use timeout to allow checking _running flag
                event = self._event_queue.get(timeout=0.1)
                self._dispatch_event(event)
                self._event_count += 1
            except Empty:
                continue
            except Exception as e:
                logger.error("Error in event processing loop: {}", e)
                self._error_count += 1

        logger.debug("Event processing thread stopped")

    def _dispatch_event(self, event: Event) -> None:
        """
        Dispatch event to subscribers

        Args:
            event: Event to dispatch
        """
        if event.event_type not in self._subscribers:
            logger.trace("No subscribers for event type: {}", event.event_type.value)
            return

        subscribers = self._subscribers[event.event_type]
        logger.trace(
            "Dispatching {} to {} subscribers", event.event_type.value, len(subscribers)
        )

        for handler in subscribers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    "Error in event handler {} for {}: {}",
                    handler.__name__,
                    event.event_type.value,
                    e,
                )
                self._error_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "running": self._running,
            "total_events": self._event_count,
            "errors": self._error_count,
            "queue_size": self._event_queue.qsize(),
            "subscriber_count": {
                event_type.value: len(handlers) for event_type, handlers in self._subscribers.items()
            },
        }

    def clear_queue(self) -> int:
        """
        Clear all events from queue

        Returns:
            Number of events cleared
        """
        count = 0
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
                count += 1
            except Empty:
                break

        logger.info("Cleared {} events from queue", count)
        return count
