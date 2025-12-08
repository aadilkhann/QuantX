"""
Example: Training Traditional ML Models

This example demonstrates:
1. Training XGBoost, LightGBM, and Random Forest models
2. Runtime model switching
3. Feature importance analysis
4. Model comparison
5. Model saving and loading
6. GPU vs CPU training (if available)

Run this to see ML models in action!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from quantx.data.providers.yahoo import YahooFinanceProvider
from quantx.ml.features import TechnicalFeatures, StatisticalFeatures, FeaturePipeline
from quantx.ml.models import XGBoostModel, LightGBMModel, RandomForestModel, create_model


def prepare_data(symbol: str = "AAPL", days: int = 730):
    """Prepare training data with features and labels"""
    print(f"\n📊 Fetching {days} days of {symbol} data...")
    
    # Fetch data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    data = provider.get_historical_data(symbol, start_date, end_date, "1d")
    
    print(f"✓ Loaded {len(data)} days of data")
    
    # Create features
    print("\n🔧 Engineering features...")
    pipeline = FeaturePipeline([
        TechnicalFeatures(
            ma_periods=[10, 20, 50],
            include_sma=True,
            include_rsi=True,
            include_macd=True,
            include_bollinger=True
        ),
        StatisticalFeatures(
            return_periods=[1, 5, 10],
            rolling_windows=[10, 20],
            include_returns=True,
            include_volatility=True
        )
    ])
    
    features = pipeline.transform(data)
    print(f"✓ Generated {len(features.columns)} features")
    
    # Create target: predict if price will go up tomorrow
    target = (data['close'].shift(-1) > data['close']).astype(int)
    target.name = "target"
    
    # Combine and drop NaN
    df = pd.concat([features, target], axis=1).dropna()
    
    X = df.drop('target', axis=1)
    y = df['target']
    
    print(f"\n✓ Final dataset: {len(X)} samples, {len(X.columns)} features")
    print(f"  Class distribution: {y.value_counts().to_dict()}")
    
    return X, y


def example_1_train_xgboost():
    """Example 1: Train XGBoost model"""
    print("=" * 70)
    print("EXAMPLE 1: Train XGBoost Model")
    print("=" * 70)
    
    # Prepare data
    X, y = prepare_data("AAPL", days=730)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False  # Don't shuffle time series!
    )
    
    print(f"\n📊 Train set: {len(X_train)} samples")
    print(f"📊 Test set: {len(X_test)} samples")
    
    # Create and train model
    print("\n🤖 Training XGBoost model...")
    model = XGBoostModel(
        name="xgb_price_predictor",
        task="classification",
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1
    )
    
    model.fit(X_train, y_train, verbose=False)
    
    # Evaluate
    print("\n📈 Evaluating model...")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"✓ Train accuracy: {train_score:.4f}")
    print(f"✓ Test accuracy: {test_score:.4f}")
    
    # Feature importance
    print("\n🔍 Top 10 important features:")
    importance = model.get_feature_importance()
    top_features = importance.nlargest(10)
    for i, (feature, score) in enumerate(top_features.items(), 1):
        print(f"  {i}. {feature}: {score:.2f}")
    
    return model, X_test, y_test


def example_2_compare_models():
    """Example 2: Compare different models"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Compare Models")
    print("=" * 70)
    
    # Prepare data
    X, y = prepare_data("GOOGL", days=500)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    # Define models to compare
    models = {
        "XGBoost": XGBoostModel(name="xgb", n_estimators=50),
        "LightGBM": LightGBMModel(name="lgb", n_estimators=50),
        "Random Forest": RandomForestModel(name="rf", n_estimators=50)
    }
    
    results = {}
    
    # Train and evaluate each model
    for name, model in models.items():
        print(f"\n🤖 Training {name}...")
        model.fit(X_train, y_train, verbose=False)
        
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        results[name] = {
            "train_acc": train_score,
            "test_acc": test_score,
            "model": model
        }
        
        print(f"  Train: {train_score:.4f}, Test: {test_score:.4f}")
    
    # Compare results
    print("\n" + "=" * 70)
    print("📊 MODEL COMPARISON")
    print("=" * 70)
    print(f"{'Model':<20} {'Train Acc':<12} {'Test Acc':<12} {'Overfit':<10}")
    print("-" * 70)
    
    for name, res in results.items():
        overfit = res['train_acc'] - res['test_acc']
        print(f"{name:<20} {res['train_acc']:<12.4f} {res['test_acc']:<12.4f} {overfit:<10.4f}")
    
    # Find best model
    best_model_name = max(results, key=lambda x: results[x]['test_acc'])
    print(f"\n🏆 Best model: {best_model_name}")
    
    return results


def example_3_model_factory():
    """Example 3: Use model factory for runtime model selection"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Model Factory (Runtime Selection)")
    print("=" * 70)
    
    # Prepare data
    X, y = prepare_data("MSFT", days=365)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    # Runtime model selection
    model_types = ["xgboost", "lightgbm", "random_forest"]
    
    print("\n💡 Creating models using factory pattern...")
    
    for model_type in model_types:
        print(f"\n🔧 Creating {model_type} model...")
        
        # Create model using factory
        model = create_model(
            model_type,
            name=f"{model_type}_factory",
            n_estimators=30
        )
        
        # Train
        model.fit(X_train, y_train, verbose=False)
        
        # Evaluate
        test_score = model.score(X_test, y_test)
        print(f"  ✓ Test accuracy: {test_score:.4f}")
    
    print("\n💡 Models can be switched at runtime with zero code changes!")


def example_4_save_load_model():
    """Example 4: Save and load models"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Save and Load Models")
    print("=" * 70)
    
    # Prepare data
    X, y = prepare_data("TSLA", days=365)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    # Train model
    print("\n🤖 Training model...")
    model = XGBoostModel(name="tsla_predictor", n_estimators=50)
    model.fit(X_train, y_train, verbose=False)
    
    original_score = model.score(X_test, y_test)
    print(f"✓ Original model test accuracy: {original_score:.4f}")
    
    # Save model
    model_path = Path("./models/tsla_predictor.joblib")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Saving model to {model_path}...")
    model.save(model_path)
    print("✓ Model saved")
    
    # Load model
    print(f"\n📂 Loading model from {model_path}...")
    loaded_model = XGBoostModel.load(model_path)
    print("✓ Model loaded")
    
    # Verify loaded model works
    loaded_score = loaded_model.score(X_test, y_test)
    print(f"✓ Loaded model test accuracy: {loaded_score:.4f}")
    
    # Verify scores match
    assert abs(original_score - loaded_score) < 1e-6, "Scores don't match!"
    print("\n✅ Model persistence verified!")


def example_5_predictions_and_probabilities():
    """Example 5: Get predictions and probabilities"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Predictions and Probabilities")
    print("=" * 70)
    
    # Prepare data
    X, y = prepare_data("NVDA", days=365)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    # Train model
    print("\n🤖 Training model...")
    model = XGBoostModel(name="nvda_predictor", n_estimators=50)
    model.fit(X_train, y_train, verbose=False)
    
    # Get predictions
    print("\n🔮 Making predictions...")
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    
    print(f"✓ Generated {len(predictions)} predictions")
    
    # Show sample predictions
    print("\n📊 Sample predictions (last 10):")
    print(f"{'Actual':<10} {'Predicted':<10} {'Prob(Down)':<12} {'Prob(Up)':<12}")
    print("-" * 50)
    
    for i in range(max(0, len(predictions) - 10), len(predictions)):
        actual = y_test.iloc[i]
        pred = predictions[i]
        prob_down = probabilities[i][0]
        prob_up = probabilities[i][1]
        
        print(f"{actual:<10} {pred:<10} {prob_down:<12.4f} {prob_up:<12.4f}")
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, predictions)
    print(f"\n✓ Overall accuracy: {accuracy:.4f}")


def main():
    """Run all examples"""
    print("\n")
    print("🚀 " * 35)
    print("QuantX ML Model Training Examples")
    print("🚀 " * 35)
    
    try:
        example_1_train_xgboost()
        example_2_compare_models()
        example_3_model_factory()
        example_4_save_load_model()
        example_5_predictions_and_probabilities()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        print("""
Key Takeaways:
1. ✅ Multiple ML models available (XGBoost, LightGBM, RF)
2. ✅ Easy to train and evaluate
3. ✅ Model comparison made simple
4. ✅ Factory pattern for runtime model selection
5. ✅ Save/load models for persistence
6. ✅ Get predictions and probabilities
7. ✅ Feature importance analysis
8. ✅ All models have consistent interface

🎯 Ready to build ML-powered trading strategies!
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
