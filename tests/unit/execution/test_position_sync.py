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
        # Set up matching positions - pass just quantities
        strategy_positions = {
            "NSE:INFY": 10  # Float quantity, not dictionary
        }
        mock_broker.set_position("NSE:INFY", quantity=10, average_price=1450.0)
        
        sync = PositionSynchronizer(mock_broker)
        report = sync.sync_positions(strategy_positions)
        
        assert not report.has_discrepancies
        assert len(report.discrepancies) == 0
    
    def test_missing_broker_position(self, mock_broker):
        """Test detection of position missing from broker."""
        strategy_positions = {
            "NSE:INFY": 10  # Float quantity
        }
        # Broker has no positions
        
        sync = PositionSynchronizer(mock_broker, auto_reconcile=False)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 1
        assert report.discrepancies[0].type == DiscrepancyType.MISSING_BROKER
    
    def test_missing_strategy_position(self, mock_broker):
        """Test detection of position missing from strategy."""
        strategy_positions = {}
        mock_broker.set_position("NSE:INFY", quantity=10)
        
        sync = PositionSynchronizer(mock_broker, auto_reconcile=False)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 1
        assert report.discrepancies[0].type == DiscrepancyType.MISSING_LOCAL
    
    def test_quantity_mismatch(self, mock_broker):
        """Test detection of quantity mismatch."""
        strategy_positions = {
            "NSE:INFY": 10  # Float quantity
        }
        mock_broker.set_position("NSE:INFY", quantity=5, average_price=1450.0)
        
        sync = PositionSynchronizer(mock_broker, auto_reconcile=False)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 1
        assert report.discrepancies[0].type == DiscrepancyType.QUANTITY_MISMATCH
        assert report.discrepancies[0].symbol == "NSE:INFY"


class TestPositionSynchronizerReconciliation:
    """Test position reconciliation logic."""
    
    def test_reconciliation_report_generation(self, mock_broker):
        """Test reconciliation report contains all necessary info."""
        strategy_positions = {
            "NSE:INFY": 10,  # Float quantities
            "NSE:TCS": 5
        }
        mock_broker.set_position("NSE:INFY", quantity=5, average_price=1450.0)
        # TCS missing from broker
        
        sync = PositionSynchronizer(mock_broker, auto_reconcile=False)
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
            "NSE:INFY": 10,  # Float quantities
            "NSE:TCS": 5,
            "NSE:RELIANCE": 8
        }
        
        mock_broker.set_position("NSE:INFY", quantity=10, average_price=1450.0)  # OK
        mock_broker.set_position("NSE:TCS", quantity=3, average_price=3500.0)   # Quantity mismatch
        # RELIANCE missing from broker
        mock_broker.set_position("NSE:WIPRO", quantity=2, average_price=450.0)   # Extra in broker
        
        sync = PositionSynchronizer(mock_broker, auto_reconcile=False)
        report = sync.sync_positions(strategy_positions)
        
        assert report.has_discrepancies
        assert len(report.discrepancies) == 3  # TCS mismatch, RELIANCE missing, WIPRO extra
        
        # Check each discrepancy type is present
        types = [d.type for d in report.discrepancies]
        assert DiscrepancyType.QUANTITY_MISMATCH in types
        assert DiscrepancyType.MISSING_BROKER in types
        assert DiscrepancyType.MISSING_LOCAL in types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
