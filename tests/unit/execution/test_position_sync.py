"""
Unit tests for PositionSynchronizer.

Tests position reconciliation between strategy and broker.
"""

import pytest
from datetime import datetime
from quantx.execution import PositionSynchronizer
from quantx.execution.position_sync import DiscrepancyType


class TestPositionSynchronizerBasic:
    """Test basic position synchronization."""
    
    def test_no_discrepancies(self, mock_broker):
        """Test when positions are already in sync."""
        # Set up matching positions
        strategy_positions = {
            "NSE:INFY": {"quantity": 10, "average_price": 1450.0}
        }
        mock_broker.set_position("NSE:INFY", quantity=10, average_price=1450.0)
        
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions(strategy_positions)
        
        assert not report.has_discrepancies
        assert len(report.discrepancies) == 0
    
    def test_missing_broker_position(self, mock_broker):
        """Test detection of position missing from broker."""
        strategy_positions = {
            "NSE:INFY": {"quantity": 10, "average_price": 1450.0}
        }
        # Broker has no positions
        
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 1
        assert report.discrepancies[0].discrepancy_type == DiscrepancyType.MISSING_BROKER_POSITION
    
    def test_missing_strategy_position(self, mock_broker):
        """Test detection of position missing from strategy."""
        strategy_positions = {}
        mock_broker.set_position("NSE:INFY", quantity=10)
        
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 1
        assert report.discrepancies[0].discrepancy_type == DiscrepancyType.MISSING_STRATEGY_POSITION
    
    def test_quantity_mismatch(self, mock_broker):
        """Test detection of quantity mismatch."""
        strategy_positions = {
            "NSE:INFY": {"quantity": 10, "average_price": 1450.0}
        }
        mock_broker.set_position("NSE:INFY", quantity=5, average_price=1450.0)
        
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 1
        assert report.discrepancies[0].discrepancy_type == DiscrepancyType.QUANTITY_MISMATCH
        assert report.discrepancies[0].symbol == "NSE:INFY"


class TestPositionSynchronizerReconciliation:
    """Test position reconciliation logic."""
    
    def test_reconciliation_report_generation(self, mock_broker):
        """Test reconciliation report contains all necessary info."""
        strategy_positions = {
            "NSE:INFY": {"quantity": 10, "average_price": 1450.0},
            "NSE:TCS": {"quantity": 5, "average_price": 3500.0}
        }
        mock_broker.set_position("NSE:INFY", quantity=5, average_price=1450.0)
        # TCS missing from broker
        
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions(strategy_positions)
        
        assert len(report.discrepancies) == 2
        assert report.timestamp is not None
        assert report.has_discrepancies
    
    def test_empty_positions(self, mock_broker):
        """Test sync with no positions on either side."""
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions({})
        
        assert not report.has_discrepancies
        assert len(report.discrepancies) == 0


class TestPositionSynchronizerMultipleDiscrepancies:
    """Test handling multiple discrepancies."""
    
    def test_multiple_symbols_with_issues(self, mock_broker):
        """Test multiple position discrepancies."""
        strategy_positions = {
            "NSE:INFY": {"quantity": 10, "average_price": 1450.0},
            "NSE:TCS": {"quantity": 5, "average_price": 3500.0},
            "NSE:RELIANCE": {"quantity": 8, "average_price": 2800.0}
        }
        
        mock_broker.set_position("NSE:INFY", quantity=10, average_price=1450.0)  # OK
        mock_broker.set_position("NSE:TCS", quantity=3, average_price=3500.0)   # Quantity mismatch
        # RELIANCE missing from broker
        mock_broker.set_position("NSE:WIPRO", quantity=2, average_price=450.0)   # Extra in broker
        
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 3  # TCS mismatch, RELIANCE missing, WIPRO extra
        
        # Check each discrepancy type is present
        types = [d.discrepancy_type for d in report.discrepancies]
        assert DiscrepancyType.QUANTITY_MISMATCH in types
        assert DiscrepancyType.MISSING_BROKER_POSITION in types
        assert DiscrepancyType.MISSING_STRATEGY_POSITION in types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
