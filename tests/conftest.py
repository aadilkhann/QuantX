"""
Pytest configuration and shared fixtures for QuantX tests.
"""

import pytest
from datetime import datetime
from typing import Dict, List
from unittest.mock import Mock, MagicMock

from quantx.core.events import EventBus, Event, EventType
from quantx.execution.brokers.base import Order, OrderType, OrderSide, OrderStatus, Fill


# ============================================================================
# EVENT BUS FIXTURES
# ============================================================================

@pytest.fixture
def event_bus():
    """Create a fresh EventBus for testing."""
    bus = EventBus()
    bus.start()
    yield bus
    bus.stop()


@pytest.fixture
def mock_event_bus():
    """Create a mock EventBus."""
    mock = MagicMock(spec=EventBus)
    mock.publish = Mock()
    mock.subscribe = Mock()
    mock.unsubscribe = Mock()
    return mock


# ============================================================================
# BROKER FIXTURES
# ============================================================================

@pytest.fixture
def mock_broker():
    """Create a mock broker for testing."""
    from tests.fixtures.mock_broker import MockBroker
    return MockBroker()


@pytest.fixture
def broker_config():
    """Sample broker configuration."""
    return {
        "broker_id": "test_broker",
        "api_key": "test_key",
        "api_secret": "test_secret",
        "access_token": "test_token"
    }


# ============================================================================
# ORDER FIXTURES
# ============================================================================

@pytest.fixture
def sample_market_order():
    """Create a sample market order."""
    return Order(
        symbol="NSE:INFY",
        quantity=10,
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_limit_order():
    """Create a sample limit order."""
    return Order(
        symbol="NSE:TCS",
        quantity=5,
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        price=3500.0,
        timestamp=datetime.now()
    )


# ============================================================================
# POSITION FIXTURES
# ============================================================================

@pytest.fixture
def sample_positions():
    """Sample positions data."""
    return {
        "NSE:INFY": {
            "symbol": "NSE:INFY",
            "quantity": 10,
            "average_price": 1450.0,
            "current_price": 1460.0,
            "pnl": 100.0
        },
        "NSE:TCS": {
            "symbol": "NSE:TCS",
            "quantity": 5,
            "average_price": 3500.0,
            "current_price": 3520.0,
            "pnl": 100.0
        }
    }


# ============================================================================
# MARKET DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_tick_data():
    """Sample tick data."""
    return {
        "instrument_token": 408065,
        "symbol": "NSE:INFY",
        "last_price": 1450.50,
        "volume": 1000000,
        "buy_quantity": 50000,
        "sell_quantity": 45000,
        "timestamp": datetime.now()
    }


@pytest.fixture
def sample_market_data_event(sample_tick_data):
    """Sample market data event."""
    return Event(
        priority=1,
        event_type=EventType.TICK,
        timestamp=datetime.now(),
        data=sample_tick_data,
        source="test"
    )


# ============================================================================
# STRATEGY FIXTURES
# ============================================================================

@pytest.fixture
def mock_strategy():
    """Create a mock strategy."""
    from quantx.strategies.base import RuleBasedStrategy
    
    class TestStrategy(RuleBasedStrategy):
        def __init__(self, name="test_strategy"):
            super().__init__(name, {})
        
        def on_data(self, event):
            pass
        
        def on_fill(self, event):
            pass
    
    return TestStrategy()


# ============================================================================
# ACCOUNT FIXTURES
# ============================================================================

@pytest.fixture
def sample_account():
    """Sample account data."""
    return {
        "equity": 100000.0,
        "cash": 50000.0,
        "margin_used": 30000.0,
        "margin_available": 20000.0
    }


# ============================================================================
# CONFIGURATION
# ============================================================================

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "initial_capital": 100000.0,
        "max_position_size": 10000.0,
        "max_daily_loss": 5000.0,
        "enable_risk_checks": True
    }


# ============================================================================
# TIME FIXTURES
# ============================================================================

@pytest.fixture
def fixed_datetime():
    """Fixed datetime for consistent testing."""
    return datetime(2025, 1, 1, 9, 15, 0)


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "broker: marks tests that require broker connection"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Add markers automatically
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "broker" in item.nodeid:
            item.add_marker(pytest.mark.broker)
