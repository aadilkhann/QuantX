"""
Order Management and Risk Control Example.

This example demonstrates:
1. Order Management System (OMS) usage
2. Risk management and compliance checks
3. Integration of OMS with Risk Manager
4. Kill switch functionality
5. Order rate limiting
"""

import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from quantx.execution import (
    PaperBroker, Order, OrderType, OrderSide,
    OrderManager, RiskManager, RiskLimits, RiskLevel
)


def example_1_basic_oms():
    """Example 1: Basic Order Management System."""
    logger.info("=" * 80)
    logger.info("Example 1: Basic OMS")
    logger.info("=" * 80)
    
    # Create broker and OMS
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    broker.update_prices({"AAPL": 150.00})
    
    oms = OrderManager(broker)
    
    # Submit order through OMS
    logger.info("\nSubmitting order through OMS...")
    order = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100
    )
    
    order_id = oms.submit_order(order)
    logger.info(f"Order ID: {order_id}")
    
    # Check order status
    tracked_order = oms.get_order(order_id)
    logger.info(f"\nOrder Status: {tracked_order.status.value}")
    logger.info(f"Filled: {tracked_order.filled_quantity}/{tracked_order.quantity}")
    
    # Get statistics
    stats = oms.get_statistics()
    logger.info(f"\nOMS Statistics:")
    logger.info(f"  Orders Submitted: {stats['orders_submitted']}")
    logger.info(f"  Orders Filled: {stats['orders_filled']}")
    logger.info(f"  Fill Rate: {stats['fill_rate']:.1%}")
    
    return oms


def example_2_order_validation():
    """Example 2: Order validation and rejection."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: Order Validation")
    logger.info("=" * 80)
    
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    broker.update_prices({"AAPL": 150.00})
    
    oms = OrderManager(broker, enable_validation=True)
    
    # Try to submit invalid orders
    logger.info("\nTesting order validation...")
    
    # Invalid: Zero quantity
    logger.info("\n1. Zero quantity order (should be rejected):")
    invalid_order1 = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=0
    )
    result = oms.submit_order(invalid_order1)
    logger.info(f"   Result: {'Accepted' if result else 'Rejected ✓'}")
    
    # Invalid: Limit order without price
    logger.info("\n2. Limit order without price (should be rejected):")
    invalid_order2 = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=100,
        price=None  # Missing price
    )
    result = oms.submit_order(invalid_order2)
    logger.info(f"   Result: {'Accepted' if result else 'Rejected ✓'}")
    
    # Valid order
    logger.info("\n3. Valid market order (should be accepted):")
    valid_order = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100
    )
    result = oms.submit_order(valid_order)
    logger.info(f"   Result: {'Accepted ✓' if result else 'Rejected'}")
    
    # Statistics
    stats = oms.get_statistics()
    logger.info(f"\nValidation Statistics:")
    logger.info(f"  Total Orders: {stats['total_orders']}")
    logger.info(f"  Rejected: {stats['orders_rejected']}")
    logger.info(f"  Accepted: {stats['orders_submitted']}")


def example_3_risk_management():
    """Example 3: Risk management controls."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Risk Management")
    logger.info("=" * 80)
    
    # Create broker
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    broker.update_prices({"AAPL": 150.00, "GOOGL": 2800.00})
    
    # Create risk manager with custom limits
    limits = RiskLimits(
        max_position_size=10000,
        max_position_pct=0.10,  # 10% max per position
        max_daily_loss=1000,
        max_orders_per_second=5
    )
    risk_mgr = RiskManager(limits)
    
    # Get account and positions
    account = broker.get_account()
    positions = broker.get_positions()
    
    logger.info("\nRisk Limits:")
    logger.info(f"  Max Position Size: ${limits.max_position_size:,.2f}")
    logger.info(f"  Max Position %: {limits.max_position_pct:.1%}")
    logger.info(f"  Max Daily Loss: ${limits.max_daily_loss:,.2f}")
    
    # Test 1: Normal order (should pass)
    logger.info("\n1. Normal order (100 AAPL):")
    order1 = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100,
        price=150.00
    )
    is_safe, violations = risk_mgr.check_order(order1, account, positions)
    logger.info(f"   Safe: {is_safe}, Violations: {len(violations)}")
    
    # Test 2: Too large position (should fail)
    logger.info("\n2. Large order (1000 AAPL = $150k > $10k limit):")
    order2 = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=1000,
        price=150.00
    )
    is_safe, violations = risk_mgr.check_order(order2, account, positions)
    logger.info(f"   Safe: {is_safe}, Violations: {len(violations)}")
    for v in violations:
        logger.warning(f"   - {v}")
    
    # Test 3: Order rate limiting
    logger.info("\n3. Order rate limiting (submit 10 orders quickly):")
    import time
    passed = 0
    failed = 0
    for i in range(10):
        order = Order(
            order_id="",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10,
            price=150.00
        )
        is_safe, violations = risk_mgr.check_order(order, account, positions)
        if is_safe:
            passed += 1
        else:
            failed += 1
        time.sleep(0.05)  # 50ms between orders
    
    logger.info(f"   Passed: {passed}, Rate limited: {failed}")
    
    # Get risk metrics
    metrics = risk_mgr.get_risk_metrics()
    logger.info(f"\nRisk Metrics:")
    logger.info(f"  Recent Orders/sec: {metrics['recent_orders_per_second']}")
    logger.info(f"  Recent Orders/min: {metrics['recent_orders_per_minute']}")
    logger.info(f"  Total Violations: {metrics['total_violations']}")


def example_4_kill_switch():
    """Example 4: Kill switch functionality."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 4: Kill Switch")
    logger.info("=" * 80)
    
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    broker.update_prices({"AAPL": 150.00})
    
    risk_mgr = RiskManager(enable_kill_switch=True)
    account = broker.get_account()
    positions = broker.get_positions()
    
    # Normal order before kill switch
    logger.info("\n1. Normal trading (before kill switch):")
    order1 = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100,
        price=150.00
    )
    is_safe, violations = risk_mgr.check_order(order1, account, positions)
    logger.info(f"   Order check: {'PASSED' if is_safe else 'FAILED'}")
    
    # Trigger kill switch
    logger.info("\n2. Triggering kill switch...")
    risk_mgr.trigger_kill_switch("Daily loss limit exceeded")
    
    # Try to place order with kill switch active
    logger.info("\n3. Attempting order with kill switch active:")
    order2 = Order(
        order_id="",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100,
        price=150.00
    )
    is_safe, violations = risk_mgr.check_order(order2, account, positions)
    logger.info(f"   Order check: {'PASSED' if is_safe else 'BLOCKED ✓'}")
    for v in violations:
        logger.error(f"   - {v}")
    
    # Deactivate kill switch
    logger.info("\n4. Deactivating kill switch...")
    risk_mgr.deactivate_kill_switch()
    
    # Try again
    logger.info("\n5. Order after deactivation:")
    is_safe, violations = risk_mgr.check_order(order2, account, positions)
    logger.info(f"   Order check: {'PASSED ✓' if is_safe else 'FAILED'}")


def example_5_integrated_oms_risk():
    """Example 5: Integrated OMS with Risk Manager."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 5: Integrated OMS + Risk Management")
    logger.info("=" * 80)
    
    # Setup
    broker = PaperBroker(config={"initial_capital": 100000})
    broker.connect()
    broker.update_prices({"AAPL": 150.00, "GOOGL": 2800.00, "MSFT": 380.00})
    
    oms = OrderManager(broker, enable_validation=True)
    
    limits = RiskLimits(
        max_position_size=20000,
        max_daily_loss=2000
    )
    risk_mgr = RiskManager(limits)
    
    # Register callbacks
    def on_order_submitted(order):
        logger.info(f"✓ Order submitted: {order.symbol} {order.quantity}")
    
    def on_order_rejected(order, reason):
        logger.warning(f"✗ Order rejected: {order.symbol} - {reason}")
    
    def on_risk_violation(violation):
        logger.warning(f"⚠ Risk violation: {violation}")
    
    oms.register_callback("order_submitted", on_order_submitted)
    oms.register_callback("order_rejected", on_order_rejected)
    risk_mgr.register_callback("violation", on_risk_violation)
    
    # Submit orders with risk checks
    logger.info("\nSubmitting orders with risk checks...\n")
    
    orders_to_submit = [
        ("AAPL", 100, 150.00),
        ("GOOGL", 5, 2800.00),
        ("MSFT", 50, 380.00),
        ("AAPL", 200, 150.00),  # This might violate risk limits
    ]
    
    for symbol, qty, price in orders_to_submit:
        order = Order(
            order_id="",
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=qty,
            price=price
        )
        
        # Risk check
        account = broker.get_account()
        positions = broker.get_positions()
        is_safe, violations = risk_mgr.check_order(order, account, positions)
        
        if is_safe:
            # Submit if safe
            oms.submit_order(order)
        else:
            logger.error(f"Order blocked by risk manager: {symbol} {qty}")
            for v in violations:
                logger.error(f"  - {v}")
    
    # Final statistics
    logger.info("\nFinal Statistics:")
    oms_stats = oms.get_statistics()
    logger.info(f"OMS:")
    logger.info(f"  Submitted: {oms_stats['orders_submitted']}")
    logger.info(f"  Rejected: {oms_stats['orders_rejected']}")
    logger.info(f"  Filled: {oms_stats['orders_filled']}")
    
    risk_metrics = risk_mgr.get_risk_metrics()
    logger.info(f"\nRisk:")
    logger.info(f"  Violations: {risk_metrics['total_violations']}")
    logger.info(f"  Kill Switch: {'ACTIVE' if risk_metrics['kill_switch_active'] else 'Inactive'}")
    
    account = broker.get_account()
    logger.info(f"\nAccount:")
    logger.info(f"  Cash: ${account.cash:,.2f}")
    logger.info(f"  Equity: ${account.equity:,.2f}")
    logger.info(f"  Positions: {len(broker.get_positions())}")


def main():
    """Run all examples."""
    logger.info("Order Management and Risk Control Examples")
    logger.info("=" * 80)
    
    try:
        # Example 1: Basic OMS
        example_1_basic_oms()
        
        # Example 2: Order validation
        example_2_order_validation()
        
        # Example 3: Risk management
        example_3_risk_management()
        
        # Example 4: Kill switch
        example_4_kill_switch()
        
        # Example 5: Integrated OMS + Risk
        example_5_integrated_oms_risk()
        
        logger.info("\n" + "=" * 80)
        logger.info("All OMS and Risk examples completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
