"""
Strategy Registry for QuantX

Provides plugin-based strategy registration and loading.
"""

from typing import Any, Dict, Type

from loguru import logger

from quantx.strategies.base import BaseStrategy


class StrategyRegistry:
    """
    Registry for strategy classes

    Allows strategies to be registered and instantiated by name.
    """

    _strategies: Dict[str, Type[BaseStrategy]] = {}

    @classmethod
    def register(cls, name: str):
        """
        Decorator to register a strategy class

        Args:
            name: Strategy name

        Returns:
            Decorator function

        Example:
            @StrategyRegistry.register("ma_crossover")
            class MACrossoverStrategy(RuleBasedStrategy):
                pass
        """

        def decorator(strategy_class: Type[BaseStrategy]):
            if name in cls._strategies:
                logger.warning("Strategy '{}' already registered, overwriting", name)

            cls._strategies[name] = strategy_class
            logger.info("Registered strategy: {}", name)
            return strategy_class

        return decorator

    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseStrategy:
        """
        Create strategy instance by name

        Args:
            name: Strategy name
            config: Strategy configuration

        Returns:
            Strategy instance

        Raises:
            ValueError: If strategy not registered
        """
        if name not in cls._strategies:
            available = list(cls._strategies.keys())
            raise ValueError(
                f"Strategy '{name}' not registered. Available strategies: {available}"
            )

        strategy_class = cls._strategies[name]
        logger.info("Creating strategy '{}' with config: {}", name, config)

        return strategy_class(name=name, config=config)

    @classmethod
    def list_strategies(cls) -> list[str]:
        """
        List all registered strategies

        Returns:
            List of strategy names
        """
        return list(cls._strategies.keys())

    @classmethod
    def get_strategy_class(cls, name: str) -> Type[BaseStrategy]:
        """
        Get strategy class by name

        Args:
            name: Strategy name

        Returns:
            Strategy class

        Raises:
            ValueError: If strategy not registered
        """
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not registered")

        return cls._strategies[name]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered strategies"""
        cls._strategies.clear()
        logger.info("Strategy registry cleared")
