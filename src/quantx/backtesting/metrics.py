"""
Performance Metrics Calculator

Calculates trading performance metrics like Sharpe ratio, drawdown, etc.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
from loguru import logger


class PerformanceMetrics:
    """
    Calculate trading performance metrics

    Provides comprehensive performance analysis for backtesting results.
    """

    @staticmethod
    def calculate_returns(equity_curve: List[Tuple[datetime, float]]) -> pd.Series:
        """
        Calculate returns from equity curve

        Args:
            equity_curve: List of (timestamp, value) tuples

        Returns:
            Series of returns
        """
        if not equity_curve:
            return pd.Series(dtype=float)

        df = pd.DataFrame(equity_curve, columns=["timestamp", "value"])
        df = df.set_index("timestamp")
        returns = df["value"].pct_change().dropna()
        return returns

    @staticmethod
    def total_return(equity_curve: List[Tuple[datetime, float]]) -> float:
        """Calculate total return"""
        if len(equity_curve) < 2:
            return 0.0

        initial_value = equity_curve[0][1]
        final_value = equity_curve[-1][1]
        return (final_value - initial_value) / initial_value

    @staticmethod
    def annual_return(equity_curve: List[Tuple[datetime, float]]) -> float:
        """Calculate annualized return"""
        if len(equity_curve) < 2:
            return 0.0

        total_ret = PerformanceMetrics.total_return(equity_curve)
        start_date = equity_curve[0][0]
        end_date = equity_curve[-1][0]
        days = (end_date - start_date).days

        if days == 0:
            return 0.0

        years = days / 365.25
        annual_ret = (1 + total_ret) ** (1 / years) - 1
        return annual_ret

    @staticmethod
    def sharpe_ratio(
        equity_curve: List[Tuple[datetime, float]], risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sharpe ratio

        Args:
            equity_curve: Equity curve
            risk_free_rate: Annual risk-free rate (default: 2%)

        Returns:
            Sharpe ratio
        """
        returns = PerformanceMetrics.calculate_returns(equity_curve)

        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # Convert annual risk-free rate to period rate
        periods_per_year = 252  # Trading days
        period_rf_rate = risk_free_rate / periods_per_year

        excess_returns = returns - period_rf_rate
        sharpe = np.sqrt(periods_per_year) * (excess_returns.mean() / returns.std())
        return sharpe

    @staticmethod
    def sortino_ratio(
        equity_curve: List[Tuple[datetime, float]], risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sortino ratio (uses downside deviation)

        Args:
            equity_curve: Equity curve
            risk_free_rate: Annual risk-free rate

        Returns:
            Sortino ratio
        """
        returns = PerformanceMetrics.calculate_returns(equity_curve)

        if len(returns) == 0:
            return 0.0

        periods_per_year = 252
        period_rf_rate = risk_free_rate / periods_per_year

        excess_returns = returns - period_rf_rate
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = np.sqrt(periods_per_year) * (
            excess_returns.mean() / downside_returns.std()
        )
        return sortino

    @staticmethod
    def max_drawdown(equity_curve: List[Tuple[datetime, float]]) -> float:
        """
        Calculate maximum drawdown

        Args:
            equity_curve: Equity curve

        Returns:
            Maximum drawdown as fraction
        """
        if len(equity_curve) < 2:
            return 0.0

        values = np.array([v for _, v in equity_curve])
        running_max = np.maximum.accumulate(values)
        drawdowns = (values - running_max) / running_max

        return abs(drawdowns.min())

    @staticmethod
    def calmar_ratio(equity_curve: List[Tuple[datetime, float]]) -> float:
        """
        Calculate Calmar ratio (annual return / max drawdown)

        Args:
            equity_curve: Equity curve

        Returns:
            Calmar ratio
        """
        annual_ret = PerformanceMetrics.annual_return(equity_curve)
        max_dd = PerformanceMetrics.max_drawdown(equity_curve)

        if max_dd == 0:
            return 0.0

        return annual_ret / max_dd

    @staticmethod
    def win_rate(trades: List) -> float:
        """
        Calculate win rate

        Args:
            trades: List of Trade objects

        Returns:
            Win rate as fraction
        """
        if not trades:
            return 0.0

        winning_trades = sum(1 for trade in trades if trade.pnl > 0)
        return winning_trades / len(trades)

    @staticmethod
    def profit_factor(trades: List) -> float:
        """
        Calculate profit factor (gross profit / gross loss)

        Args:
            trades: List of Trade objects

        Returns:
            Profit factor
        """
        if not trades:
            return 0.0

        gross_profit = sum(trade.pnl for trade in trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in trades if trade.pnl < 0))

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    @staticmethod
    def average_trade(trades: List) -> Dict[str, float]:
        """
        Calculate average trade statistics

        Args:
            trades: List of Trade objects

        Returns:
            Dictionary with average trade stats
        """
        if not trades:
            return {"avg_profit": 0.0, "avg_loss": 0.0, "avg_trade": 0.0}

        winning_trades = [t.pnl for t in trades if t.pnl > 0]
        losing_trades = [t.pnl for t in trades if t.pnl < 0]

        return {
            "avg_profit": np.mean(winning_trades) if winning_trades else 0.0,
            "avg_loss": np.mean(losing_trades) if losing_trades else 0.0,
            "avg_trade": np.mean([t.pnl for t in trades]),
        }

    @staticmethod
    def calculate_all_metrics(
        equity_curve: List[Tuple[datetime, float]],
        trades: List,
        initial_capital: float,
    ) -> Dict:
        """
        Calculate all performance metrics

        Args:
            equity_curve: Equity curve
            trades: List of trades
            initial_capital: Initial capital

        Returns:
            Dictionary of all metrics
        """
        logger.info("Calculating performance metrics...")

        metrics = {
            # Returns
            "total_return": PerformanceMetrics.total_return(equity_curve),
            "annual_return": PerformanceMetrics.annual_return(equity_curve),
            # Risk-adjusted returns
            "sharpe_ratio": PerformanceMetrics.sharpe_ratio(equity_curve),
            "sortino_ratio": PerformanceMetrics.sortino_ratio(equity_curve),
            "calmar_ratio": PerformanceMetrics.calmar_ratio(equity_curve),
            # Risk metrics
            "max_drawdown": PerformanceMetrics.max_drawdown(equity_curve),
            # Trade statistics
            "total_trades": len(trades),
            "win_rate": PerformanceMetrics.win_rate(trades),
            "profit_factor": PerformanceMetrics.profit_factor(trades),
        }

        # Average trade stats
        avg_stats = PerformanceMetrics.average_trade(trades)
        metrics.update(avg_stats)

        # Additional stats
        if len(equity_curve) >= 2:
            final_value = equity_curve[-1][1]
            metrics["final_value"] = final_value
            metrics["total_pnl"] = final_value - initial_capital

        logger.info("Performance metrics calculated")
        return metrics

    @staticmethod
    def print_metrics(metrics: Dict) -> None:
        """
        Print metrics in formatted way

        Args:
            metrics: Dictionary of metrics
        """
        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS")
        print("=" * 60)

        print("\nReturns:")
        print(f"  Total Return:        {metrics.get('total_return', 0):.2%}")
        print(f"  Annual Return:       {metrics.get('annual_return', 0):.2%}")
        print(f"  Total P&L:           ${metrics.get('total_pnl', 0):,.2f}")

        print("\nRisk-Adjusted Returns:")
        print(f"  Sharpe Ratio:        {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"  Sortino Ratio:       {metrics.get('sortino_ratio', 0):.2f}")
        print(f"  Calmar Ratio:        {metrics.get('calmar_ratio', 0):.2f}")

        print("\nRisk Metrics:")
        print(f"  Max Drawdown:        {metrics.get('max_drawdown', 0):.2%}")

        print("\nTrade Statistics:")
        print(f"  Total Trades:        {metrics.get('total_trades', 0)}")
        print(f"  Win Rate:            {metrics.get('win_rate', 0):.2%}")
        print(f"  Profit Factor:       {metrics.get('profit_factor', 0):.2f}")
        print(f"  Avg Profit:          ${metrics.get('avg_profit', 0):,.2f}")
        print(f"  Avg Loss:            ${metrics.get('avg_loss', 0):,.2f}")
        print(f"  Avg Trade:           ${metrics.get('avg_trade', 0):,.2f}")

        print("\n" + "=" * 60 + "\n")
