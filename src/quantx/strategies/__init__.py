"""Strategies module initialization"""

from quantx.strategies.base import (
    Action,
    AIPoweredStrategy,
    BaseStrategy,
    HybridStrategy,
    RuleBasedStrategy,
    Signal,
)
from quantx.strategies.registry import StrategyRegistry

# Import strategies to register them
from quantx.strategies.rule_based.ma_crossover import MACrossoverStrategy

__all__ = [
    "BaseStrategy",
    "RuleBasedStrategy",
    "AIPoweredStrategy",
    "HybridStrategy",
    "Signal",
    "Action",
    "StrategyRegistry",
    "MACrossoverStrategy",
]
