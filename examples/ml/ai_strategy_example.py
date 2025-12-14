"""
AI Strategy Example - Demonstrates AI-powered trading strategies.

This example shows how to:
1. Train an ML model
2. Use it in an AI-powered strategy
3. Backtest the strategy
4. Compare with rule-based strategies
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from quantx.data.providers.yahoo import YahooFinanceProvider
from quantx.ml.features import TechnicalFeatures, StatisticalFeatures, FeaturePipeline
from quantx.ml.models import XGBoostModel
from quantx.ml.pipeline import DataPreparator, ModelTrainer
from quantx.strategies.ai_powered import MLClassifierStrategy, SignalStrengthStrategy
from quantx.backtesting import BacktestEngine, Portfolio


def example_1_train_and_use_model():
    """Example 1: Train a model and use it in a strategy."""
    logger.info("=" * 80)
    logger.info("Example 1: Train ML Model and Use in Strategy")
    logger.info("=" * 80)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    
    logger.info("Fetching AAPL data...")
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    # Create features
    logger.info("Engineering features...")
    pipeline = FeaturePipeline([
        TechnicalFeatures(ma_periods=[10, 20, 50], include_rsi=True, include_macd=True),
        StatisticalFeatures(return_periods=[1, 5, 10])
    ])
    
    features = pipeline.transform(data)
    
    # Create target (1 if next day return > 0, else 0)
    features['target'] = (data['close'].pct_change().shift(-1) > 0).astype(int)
    features = features.dropna()
    
    # Split data
    train_size = int(len(features) * 0.7)
    train_data = features.iloc[:train_size]
    test_data = features.iloc[train_size:]
    
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']
    X_test = test_data.drop('target', axis=1)
    y_test = test_data['target']
    
    # Train model
    logger.info("Training XGBoost model...")
    model = XGBoostModel(
        name="aapl_classifier",
        task="classification",
        n_estimators=100,
        max_depth=5
    )
    
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    
    # Evaluate
    from quantx.ml.evaluation import calculate_classification_metrics
    predictions = model.predict(X_test)
    metrics = calculate_classification_metrics(y_test, predictions)
    
    logger.info(f"Model Performance:")
    logger.info(f"  Accuracy: {metrics['accuracy']:.3f}")
    logger.info(f"  Precision: {metrics['precision']:.3f}")
    logger.info(f"  Recall: {metrics['recall']:.3f}")
    
    # Save model
    model_path = project_root / "data" / "models" / "aapl_xgboost.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))
    logger.info(f"Model saved to {model_path}")
    
    # Create strategy
    logger.info("\nCreating AI-powered strategy...")
    strategy = MLClassifierStrategy(
        name="XGB_Classifier",
        symbols=["AAPL"],
        model_path=str(model_path),
        prediction_threshold=0.6,
        position_size=10000,
        feature_config={
            "technical": {
                "enabled": True,
                "ma_periods": [10, 20, 50],
                "include_rsi": True,
                "include_macd": True
            },
            "statistical": {
                "enabled": True,
                "return_periods": [1, 5, 10]
            }
        }
    )
    
    strategy.on_start()
    logger.info("Strategy initialized successfully!")
    
    return strategy, model


def example_2_signal_strength_strategy():
    """Example 2: Use SignalStrengthStrategy with confidence-based position sizing."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: Signal Strength Strategy (Confidence-Based Sizing)")
    logger.info("=" * 80)
    
    model_path = project_root / "data" / "models" / "aapl_xgboost.pkl"
    
    if not model_path.exists():
        logger.warning("Model not found. Run Example 1 first!")
        return None
    
    # Create strategy with confidence tiers
    strategy = SignalStrengthStrategy(
        name="Confidence_Trader",
        symbols=["AAPL"],
        model_path=str(model_path),
        prediction_threshold=0.6,
        min_confidence=0.65,
        base_position_size=10000,
        confidence_tiers={
            0.95: 3.0,  # Very high confidence: 3x position
            0.85: 2.0,  # High confidence: 2x position
            0.75: 1.5,  # Medium-high: 1.5x position
            0.65: 1.0,  # Medium: 1x position
        },
        feature_config={
            "technical": {
                "enabled": True,
                "ma_periods": [10, 20, 50],
                "include_rsi": True,
                "include_macd": True
            },
            "statistical": {
                "enabled": True,
                "return_periods": [1, 5, 10]
            }
        }
    )
    
    strategy.on_start()
    logger.info("Signal Strength Strategy initialized!")
    logger.info(f"Confidence tiers: {strategy.confidence_tiers}")
    
    return strategy


def example_3_ensemble_strategy():
    """Example 3: Use ensemble of models for more robust predictions."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Ensemble Strategy (Multiple Models)")
    logger.info("=" * 80)
    
    # Train multiple models
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    # Create features
    pipeline = FeaturePipeline([
        TechnicalFeatures(ma_periods=[10, 20, 50], include_rsi=True),
        StatisticalFeatures(return_periods=[1, 5, 10])
    ])
    
    features = pipeline.transform(data)
    features['target'] = (data['close'].pct_change().shift(-1) > 0).astype(int)
    features = features.dropna()
    
    train_size = int(len(features) * 0.7)
    X_train = features.iloc[:train_size].drop('target', axis=1)
    y_train = features.iloc[:train_size]['target']
    
    # Train XGBoost
    logger.info("Training XGBoost...")
    xgb_model = XGBoostModel(name="xgb", n_estimators=100)
    xgb_model.fit(X_train, y_train, verbose=False)
    xgb_path = project_root / "data" / "models" / "ensemble_xgb.pkl"
    xgb_path.parent.mkdir(parents=True, exist_ok=True)
    xgb_model.save(str(xgb_path))
    
    # Train LightGBM
    logger.info("Training LightGBM...")
    from quantx.ml.models import LightGBMModel
    lgb_model = LightGBMModel(name="lgb", n_estimators=100)
    lgb_model.fit(X_train, y_train, verbose=False)
    lgb_path = project_root / "data" / "models" / "ensemble_lgb.pkl"
    lgb_model.save(str(lgb_path))
    
    # Train Random Forest
    logger.info("Training Random Forest...")
    from quantx.ml.models import RandomForestModel
    rf_model = RandomForestModel(name="rf", n_estimators=100)
    rf_model.fit(X_train, y_train)
    rf_path = project_root / "data" / "models" / "ensemble_rf.pkl"
    rf_model.save(str(rf_path))
    
    # Create ensemble strategy
    logger.info("\nCreating ensemble strategy...")
    strategy = SignalStrengthStrategy(
        name="Ensemble_Strategy",
        symbols=["AAPL"],
        model_path=str(xgb_path),
        use_ensemble=True,
        ensemble_models=[str(lgb_path), str(rf_path)],
        prediction_threshold=0.6,
        base_position_size=10000,
        feature_config={
            "technical": {"enabled": True, "ma_periods": [10, 20, 50], "include_rsi": True},
            "statistical": {"enabled": True, "return_periods": [1, 5, 10]}
        }
    )
    
    strategy.on_start()
    logger.info(f"Ensemble strategy with {len(strategy.ensemble_models) + 1} models initialized!")
    
    return strategy


def example_4_backtest_ai_strategy():
    """Example 4: Backtest AI strategy and compare with buy-and-hold."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 4: Backtest AI Strategy")
    logger.info("=" * 80)
    
    model_path = project_root / "data" / "models" / "aapl_xgboost.pkl"
    
    if not model_path.exists():
        logger.warning("Model not found. Run Example 1 first!")
        return
    
    # Create AI strategy
    ai_strategy = MLClassifierStrategy(
        name="AI_Strategy",
        symbols=["AAPL"],
        model_path=str(model_path),
        prediction_threshold=0.6,
        position_size=10000,
        feature_config={
            "technical": {"enabled": True, "ma_periods": [10, 20, 50], "include_rsi": True, "include_macd": True},
            "statistical": {"enabled": True, "return_periods": [1, 5, 10]}
        }
    )
    
    # Fetch data for backtest
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year backtest
    
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    logger.info(f"Backtesting from {start_date.date()} to {end_date.date()}")
    logger.info(f"Data points: {len(data)}")
    
    # Note: Full backtest integration would require BacktestEngine
    # For now, we'll simulate signal generation
    logger.info("\nSimulating signal generation...")
    ai_strategy.on_start()
    
    # Process each day
    signals = []
    for i in range(60, len(data)):  # Start after enough data for features
        window_data = data.iloc[:i+1]
        ai_strategy.on_data(window_data)
        
        # Get prediction stats
        if "AAPL" in ai_strategy.prediction_history:
            stats = ai_strategy.get_prediction_stats("AAPL")
            if stats:
                signals.append(stats['last_probability'])
    
    logger.info(f"Generated {len(signals)} predictions")
    if signals:
        logger.info(f"Average prediction probability: {np.mean(signals):.3f}")
        logger.info(f"Prediction std: {np.std(signals):.3f}")


def example_5_compare_strategies():
    """Example 5: Compare AI strategy with rule-based strategy."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 5: Compare AI vs Rule-Based Strategy")
    logger.info("=" * 80)
    
    # This would require full backtesting engine
    # Showing concept
    
    logger.info("AI Strategy Benefits:")
    logger.info("  ✓ Learns from data patterns")
    logger.info("  ✓ Adapts to market conditions")
    logger.info("  ✓ Can capture complex non-linear relationships")
    logger.info("  ✓ Confidence-based position sizing")
    
    logger.info("\nRule-Based Strategy Benefits:")
    logger.info("  ✓ Interpretable and explainable")
    logger.info("  ✓ No training required")
    logger.info("  ✓ Consistent behavior")
    logger.info("  ✓ Lower computational requirements")
    
    logger.info("\nBest Practice: Use hybrid approach!")
    logger.info("  - AI for predictions")
    logger.info("  - Rules for risk management")
    logger.info("  - Ensemble for robustness")


def main():
    """Run all examples."""
    logger.info("AI-Powered Strategy Examples")
    logger.info("=" * 80)
    
    try:
        # Example 1: Train and use model
        strategy1, model = example_1_train_and_use_model()
        
        # Example 2: Signal strength strategy
        strategy2 = example_2_signal_strength_strategy()
        
        # Example 3: Ensemble strategy
        strategy3 = example_3_ensemble_strategy()
        
        # Example 4: Backtest
        example_4_backtest_ai_strategy()
        
        # Example 5: Comparison
        example_5_compare_strategies()
        
        logger.info("\n" + "=" * 80)
        logger.info("All examples completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
