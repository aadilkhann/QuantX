"""
Deep Learning Training Example - LSTM and GRU models.

This example demonstrates:
1. Training LSTM models for price prediction
2. Training GRU models for direction classification
3. Sequence preparation
4. Model evaluation
5. Using trained models in strategies
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

# Check if PyTorch is available
try:
    from quantx.ml.models import LSTMModel, GRUModel
    DEEP_LEARNING_AVAILABLE = True
except (ImportError, AttributeError):
    DEEP_LEARNING_AVAILABLE = False
    logger.warning("PyTorch not available. Deep learning examples will be skipped.")
    logger.warning("Install with: pip install torch torchvision")


def example_1_lstm_price_prediction():
    """Example 1: Train LSTM for next-day price prediction."""
    if not DEEP_LEARNING_AVAILABLE:
        logger.warning("Skipping LSTM example - PyTorch not available")
        return None
    
    logger.info("=" * 80)
    logger.info("Example 1: LSTM for Price Prediction")
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
        TechnicalFeatures(ma_periods=[10, 20], include_rsi=True, include_macd=True),
        StatisticalFeatures(return_periods=[1, 5])
    ])
    
    features = pipeline.transform(data)
    
    # Create target (next day return)
    features['target'] = data['close'].pct_change().shift(-1)
    features = features.dropna()
    
    # Split data
    train_size = int(len(features) * 0.7)
    val_size = int(len(features) * 0.15)
    
    train_data = features.iloc[:train_size]
    val_data = features.iloc[train_size:train_size + val_size]
    test_data = features.iloc[train_size + val_size:]
    
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']
    X_val = val_data.drop('target', axis=1)
    y_val = val_data['target']
    X_test = test_data.drop('target', axis=1)
    y_test = test_data['target']
    
    # Train LSTM
    logger.info("Training LSTM model...")
    logger.info(f"  Training samples: {len(X_train)}")
    logger.info(f"  Validation samples: {len(X_val)}")
    logger.info(f"  Test samples: {len(X_test)}")
    
    model = LSTMModel(
        sequence_length=20,
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
        learning_rate=0.001,
        batch_size=32,
        epochs=50,
        early_stopping_patience=10
    )
    
    model.fit(X_train, y_train, X_val, y_val)
    
    # Evaluate
    logger.info("\nEvaluating model...")
    predictions = model.predict(X_test)
    
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    mse = mean_squared_error(y_test[len(y_test) - len(predictions):], predictions)
    mae = mean_absolute_error(y_test[len(y_test) - len(predictions):], predictions)
    r2 = r2_score(y_test[len(y_test) - len(predictions):], predictions)
    
    logger.info(f"Test Performance:")
    logger.info(f"  MSE: {mse:.6f}")
    logger.info(f"  MAE: {mae:.6f}")
    logger.info(f"  R²: {r2:.4f}")
    
    # Save model
    model_path = project_root / "data" / "models" / "lstm_price_predictor.pt"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))
    logger.info(f"\nModel saved to {model_path}")
    
    # Plot training history
    if model.train_losses:
        logger.info(f"\nTraining History:")
        logger.info(f"  Final train loss: {model.train_losses[-1]:.6f}")
        if model.val_losses:
            logger.info(f"  Final val loss: {model.val_losses[-1]:.6f}")
            logger.info(f"  Best val loss: {min(model.val_losses):.6f}")
    
    return model


def example_2_gru_direction_classification():
    """Example 2: Train GRU for direction classification."""
    if not DEEP_LEARNING_AVAILABLE:
        logger.warning("Skipping GRU example - PyTorch not available")
        return None
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: GRU for Direction Classification")
    logger.info("=" * 80)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    # Create features
    pipeline = FeaturePipeline([
        TechnicalFeatures(ma_periods=[10, 20], include_rsi=True),
        StatisticalFeatures(return_periods=[1, 5])
    ])
    
    features = pipeline.transform(data)
    
    # Create target (1 if next day up, 0 if down)
    features['target'] = (data['close'].pct_change().shift(-1) > 0).astype(float)
    features = features.dropna()
    
    # Split data
    train_size = int(len(features) * 0.7)
    val_size = int(len(features) * 0.15)
    
    X_train = features.iloc[:train_size].drop('target', axis=1)
    y_train = features.iloc[:train_size]['target']
    X_val = features.iloc[train_size:train_size + val_size].drop('target', axis=1)
    y_val = features.iloc[train_size:train_size + val_size]['target']
    X_test = features.iloc[train_size + val_size:].drop('target', axis=1)
    y_test = features.iloc[train_size + val_size:]['target']
    
    # Train GRU
    logger.info("Training GRU model...")
    model = GRUModel(
        sequence_length=20,
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
        learning_rate=0.001,
        batch_size=32,
        epochs=50,
        early_stopping_patience=10
    )
    
    model.fit(X_train, y_train, X_val, y_val)
    
    # Evaluate
    predictions = model.predict(X_test)
    predictions_binary = (predictions > 0.5).astype(int)
    y_test_subset = y_test.values[len(y_test) - len(predictions):]
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    accuracy = accuracy_score(y_test_subset, predictions_binary)
    precision = precision_score(y_test_subset, predictions_binary)
    recall = recall_score(y_test_subset, predictions_binary)
    f1 = f1_score(y_test_subset, predictions_binary)
    
    logger.info(f"\nTest Performance:")
    logger.info(f"  Accuracy: {accuracy:.3f}")
    logger.info(f"  Precision: {precision:.3f}")
    logger.info(f"  Recall: {recall:.3f}")
    logger.info(f"  F1 Score: {f1:.3f}")
    
    # Save model
    model_path = project_root / "data" / "models" / "gru_direction_classifier.pt"
    model.save(str(model_path))
    logger.info(f"\nModel saved to {model_path}")
    
    return model


def example_3_bidirectional_lstm():
    """Example 3: Bidirectional LSTM for better context."""
    if not DEEP_LEARNING_AVAILABLE:
        logger.warning("Skipping bidirectional LSTM example - PyTorch not available")
        return None
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Bidirectional LSTM")
    logger.info("=" * 80)
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    # Create features
    pipeline = FeaturePipeline([
        TechnicalFeatures(ma_periods=[10, 20], include_rsi=True, include_macd=True),
        StatisticalFeatures(return_periods=[1, 5])
    ])
    
    features = pipeline.transform(data)
    features['target'] = data['close'].pct_change().shift(-1)
    features = features.dropna()
    
    # Split
    train_size = int(len(features) * 0.8)
    X_train = features.iloc[:train_size].drop('target', axis=1)
    y_train = features.iloc[:train_size]['target']
    X_test = features.iloc[train_size:].drop('target', axis=1)
    y_test = features.iloc[train_size:]['target']
    
    # Train bidirectional LSTM
    logger.info("Training Bidirectional LSTM...")
    model = LSTMModel(
        sequence_length=20,
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
        bidirectional=True,  # Key difference
        learning_rate=0.001,
        batch_size=32,
        epochs=30
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    y_test_subset = y_test.values[len(y_test) - len(predictions):]
    
    from sklearn.metrics import mean_squared_error, r2_score
    mse = mean_squared_error(y_test_subset, predictions)
    r2 = r2_score(y_test_subset, predictions)
    
    logger.info(f"\nBidirectional LSTM Performance:")
    logger.info(f"  MSE: {mse:.6f}")
    logger.info(f"  R²: {r2:.4f}")
    logger.info(f"  Hidden size (effective): {model.hidden_size * 2} (bidirectional)")
    
    return model


def example_4_compare_lstm_vs_gru():
    """Example 4: Compare LSTM vs GRU performance."""
    if not DEEP_LEARNING_AVAILABLE:
        logger.warning("Skipping comparison example - PyTorch not available")
        return
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 4: LSTM vs GRU Comparison")
    logger.info("=" * 80)
    
    # Prepare data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    pipeline = FeaturePipeline([
        TechnicalFeatures(ma_periods=[10, 20], include_rsi=True),
        StatisticalFeatures(return_periods=[1, 5])
    ])
    
    features = pipeline.transform(data)
    features['target'] = data['close'].pct_change().shift(-1)
    features = features.dropna()
    
    train_size = int(len(features) * 0.8)
    X_train = features.iloc[:train_size].drop('target', axis=1)
    y_train = features.iloc[:train_size]['target']
    X_test = features.iloc[train_size:].drop('target', axis=1)
    y_test = features.iloc[train_size:]['target']
    
    # Train LSTM
    logger.info("Training LSTM...")
    import time
    start_time = time.time()
    lstm = LSTMModel(sequence_length=20, hidden_size=64, epochs=20)
    lstm.fit(X_train, y_train)
    lstm_time = time.time() - start_time
    lstm_preds = lstm.predict(X_test)
    
    # Train GRU
    logger.info("Training GRU...")
    start_time = time.time()
    gru = GRUModel(sequence_length=20, hidden_size=64, epochs=20)
    gru.fit(X_train, y_train)
    gru_time = time.time() - start_time
    gru_preds = gru.predict(X_test)
    
    # Compare
    from sklearn.metrics import mean_squared_error
    y_test_subset = y_test.values[len(y_test) - len(lstm_preds):]
    
    lstm_mse = mean_squared_error(y_test_subset, lstm_preds)
    gru_mse = mean_squared_error(y_test_subset, gru_preds)
    
    logger.info(f"\nComparison Results:")
    logger.info(f"  LSTM:")
    logger.info(f"    MSE: {lstm_mse:.6f}")
    logger.info(f"    Training time: {lstm_time:.2f}s")
    logger.info(f"  GRU:")
    logger.info(f"    MSE: {gru_mse:.6f}")
    logger.info(f"    Training time: {gru_time:.2f}s")
    logger.info(f"  Speed improvement: {((lstm_time - gru_time) / lstm_time * 100):.1f}%")


def example_5_using_deep_learning_in_strategy():
    """Example 5: Use trained deep learning model in a strategy."""
    if not DEEP_LEARNING_AVAILABLE:
        logger.warning("Skipping strategy example - PyTorch not available")
        return
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 5: Using Deep Learning Model in Strategy")
    logger.info("=" * 80)
    
    model_path = project_root / "data" / "models" / "lstm_price_predictor.pt"
    
    if not model_path.exists():
        logger.warning("LSTM model not found. Run Example 1 first!")
        return
    
    logger.info("Loading trained LSTM model...")
    model = LSTMModel.load(str(model_path))
    logger.info("Model loaded successfully!")
    
    logger.info("\nTo use in a strategy:")
    logger.info("  1. Load the model in strategy __init__")
    logger.info("  2. Prepare features in on_data()")
    logger.info("  3. Get predictions from model")
    logger.info("  4. Generate trading signals based on predictions")
    
    logger.info("\nExample code:")
    logger.info("""
    class LSTMStrategy(AIPoweredStrategy):
        def __init__(self, model_path, **kwargs):
            super().__init__(**kwargs)
            self.model = LSTMModel.load(model_path)
        
        def on_data(self, data):
            features = self.prepare_features(data)
            prediction = self.model.predict(features)
            
            if prediction > 0.01:  # Predicted positive return
                self.buy(...)
            elif prediction < -0.01:  # Predicted negative return
                self.sell(...)
    """)


def main():
    """Run all examples."""
    logger.info("Deep Learning Training Examples")
    logger.info("=" * 80)
    
    if not DEEP_LEARNING_AVAILABLE:
        logger.error("PyTorch is not available!")
        logger.error("Install with: pip install torch torchvision")
        logger.error("Or: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
        return
    
    try:
        # Example 1: LSTM for price prediction
        lstm_model = example_1_lstm_price_prediction()
        
        # Example 2: GRU for direction classification
        gru_model = example_2_gru_direction_classification()
        
        # Example 3: Bidirectional LSTM
        bilstm_model = example_3_bidirectional_lstm()
        
        # Example 4: Compare LSTM vs GRU
        example_4_compare_lstm_vs_gru()
        
        # Example 5: Using in strategy
        example_5_using_deep_learning_in_strategy()
        
        logger.info("\n" + "=" * 80)
        logger.info("All deep learning examples completed!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
