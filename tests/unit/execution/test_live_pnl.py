"""
Unit tests for LivePnLTracker.

Tests real-time P&L tracking and calculation for live trading.
"""

import pytest
from datetime import datetime
from quantx.execution.live_pnl import LivePnLTracker
from quantx.execution.brokers.base import Fill, OrderSide, Position


class TestLivePnLTrackerBasic:
    """Test basic P&L tracking functionality."""
    
    def test_initialization(self):
        """Test tracker initializes with correct defaults."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        assert tracker.initial_capital == 100000.0
        assert tracker.realized_pnl == 0.0
        assert len(tracker.get_trades()) == 0
    
    def test_update_position_pnl(self):
        """Test updating unrealized P&L for a position."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        # Position bought at 1400, currently at 1500
        unrealized = tracker.update_position_pnl(
            symbol="NSE:INFY",
            quantity=10,
            average_price=1400.0,
            current_price=1500.0
        )
        
        # Profit should be (1500-1400)*10 = 1000
        assert unrealized == pytest.approx(1000.0, rel=0.01)
    
    def test_update_from_positions(self, mock_broker):
        """Test updating from list of positions."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        mock_broker.set_position("NSE:INFY", quantity=10, average_price=1400.0)
        positions = mock_broker.get_positions()
        
        # Manually update position prices
        for pos in positions:
            tracker.update_position_pnl(
                symbol=pos.symbol,
                quantity=pos.quantity,
                average_price=pos.average_price,
                current_price=1500.0  # Mock current price
            )
        
        unrealized = tracker.get_unrealized_pnl()
        assert unrealized == pytest.approx(1000.0, rel=0.01)


class TestLivePnLTrackerTrades:
    """Test trade recording and P&L calculation."""
    
    def test_record_trade_profit(self):
        """Test recording a profitable trade."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        trade_record = tracker.record_trade(
            symbol="NSE:INFY",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=1400.0,
            exit_price=1500.0,
            quantity=10,
            side="long",
            commission=20.0
        )
        
        # Profit: (1500-1400)*10 - 20 = 980
        assert trade_record.net_pnl == pytest.approx(980.0, rel=0.01)
        assert len(tracker.get_trades()) == 1
    
    def test_record_trade_loss(self):
        """Test recording a losing trade."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        trade_record = tracker.record_trade(
            symbol="NSE:INFY",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=1500.0,
            exit_price=1400.0,
            quantity=10,
            side="long",
            commission=20.0
        )
        
        # Loss: (1400-1500)*10 - 20 = -1020
        assert trade_record.net_pnl == pytest.approx(-1020.0, rel=0.01)
        assert trade_record.pnl < 0
    
    def test_get_trades(self):
        """Test retrieving trade history."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        # Record multiple trades
        for i in range(5):
            tracker.record_trade(
                symbol=f"STOCK{i}",
                entry_time=datetime.now(),
                exit_time=datetime.now(),
                entry_price=100.0,
                exit_price=105.0,
                quantity=10,
                side="long"
            )
        
        all_trades = tracker.get_trades()
        assert len(all_trades) == 5
        
        limited_trades = tracker.get_trades(limit=3)
        assert len(limited_trades) == 3


class TestLivePnLTrackerMetrics:
    """Test P&L calculations and metrics."""
    
    def test_get_total_pnl(self):
        """Test total P&L calculation."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        # Record a realized trade
        tracker.record_trade(
            symbol="NSE:INFY",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=1400.0,
            exit_price=1500.0,
            quantity=10,
            side="long"
        )
        
        # Add unrealized P&L
        tracker.update_position_pnl(
            symbol="NSE:TCS",
            quantity=5,
            average_price=3000.0,
            current_price=3100.0
        )
        
        total_pnl = tracker.get_total_pnl()
        # Realized: 1000 + Unrealized: 500 = 1500
        assert total_pnl == pytest.approx(1500.0, rel=0.01)
    
    def test_get_total_equity(self):
        """Test equity calculation."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        tracker.record_trade(
            symbol="NSE:INFY",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=1400.0,
            exit_price=1500.0,
            quantity=10,
            side="long"
        )
        
        equity = tracker.get_total_equity()
        # Initial 100000 + profit 1000 = 101000
        assert equity == pytest.approx(101000.0, rel=0.01)
    
    def test_get_snapshot(self):
        """Test getting P&L snapshot."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        tracker.record_trade(
            symbol="NSE:INFY",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=1400.0,
            exit_price=1500.0,
            quantity=10,
            side="long",
            commission=10.0
        )
        
        snapshot = tracker.get_snapshot()
        
        assert snapshot.realized_pnl == pytest.approx(990.0, rel=0.01)  # 1000 - 10 commission
        assert snapshot.total_pnl == pytest.approx(990.0, rel=0.01)
        assert snapshot.closed_trades == 1
    
    def test_get_performance_summary(self):
        """Test performance summary generation."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        # Record winning trade
        tracker.record_trade(
            symbol="NSE:INFY",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=1400.0,
            exit_price=1500.0,
            quantity=10,
            side="long"
        )
        
        # Record losing trade
        tracker.record_trade(
            symbol="NSE:TCS",
            entry_time=datetime.now(),
            exit_time=datetime.now(),
            entry_price=3500.0,
            exit_price=3400.0,
            quantity=5,
            side="long"
        )
        
        summary = tracker.get_performance_summary()
        
        assert "total_trades" in summary
        assert "winning_trades" in summary
        assert "losing_trades" in summary
        assert "win_rate" in summary
        assert summary["total_trades"] == 2
        assert summary["winning_trades"] == 1
        assert summary["losing_trades"] == 1


class TestLivePnLTrackerEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_tracker(self):
        """Test tracker with no trades."""
        tracker = LivePnLTracker(initial_capital=100000.0)
        
        assert tracker.get_unrealized_pnl() == 0.0
        assert tracker.get_total_pnl() == 0.0
        assert len(tracker.get_trades()) == 0
    
    def test_zero_initial_capital(self):
        """Test initialization with zero capital."""
        tracker = LivePnLTracker(initial_capital=0.0)
        
        assert tracker.initial_capital == 0.0
        assert tracker.get_total_equity() == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
