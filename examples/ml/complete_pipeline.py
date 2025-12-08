"""
Example: Complete ML Training Pipeline

This example demonstrates the end-to-end ML workflow:
1. Data fetching
2. Feature engineering
3. Model training with pipeline
4. Comprehensive evaluation
5. Cross-validation
6. Model comparison
7. Model persistence

This is production-ready code!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from quantx.data.providers.yahoo import YahooFinanceProvider
from quantx.ml.features import TechnicalFeatures, StatisticalFeatures, FeaturePipeline
from quantx.ml.models import create_model
from quantx.ml.pipeline import ModelTrainer, DataPreparator
from quantx.ml.evaluation import (
    evaluate_model,
    print_metrics_report,
    walk_forward_validate,
    compare_models
)


def fetch_and_prepare_data(symbol: str = "AAPL", days: int = 730):
    """Fetch data and engineer features"""
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
            include_ema=True,
            include_rsi=True,
            include_macd=True,
            include_bollinger=True,
            include_atr=True
        ),
        StatisticalFeatures(
            return_periods=[1, 5, 10],
            rolling_windows=[10, 20, 50],
            include_returns=True,
            include_volatility=True,
            include_momentum=True
        )
    ])
    
    features = pipeline.transform(data)
    print(f"✓ Generated {len(features.columns)} features")
    
    # Create target: predict if price will go up tomorrow
    target = (data['close'].shift(-1) > data['close']).astype(int)
    target.name = "target"
    
    # Get returns for trading metrics
    returns = data['close'].pct_change().shift(-1)
    returns.name = "returns"
    
    # Combine
    df = pd.concat([features, target, returns], axis=1).dropna()
    
    print(f"\n✓ Final dataset: {len(df)} samples")
    print(f"  Class distribution: {df['target'].value_counts().to_dict()}")
    
    return df


def example_1_basic_pipeline():
    """Example 1: Basic training pipeline"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Training Pipeline")
    print("=" * 70)
    
    # Prepare data
    data = fetch_and_prepare_data("AAPL", days=730)
    
    # Create trainer
    trainer = ModelTrainer(
        model_type="xgboost",
        model_params={
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1
        },
        config={"task": "classification"}
    )
    
    # Train
    results = trainer.train(
        data=data,
        target_column="target",
        returns_column="returns",
        verbose=True
    )
    
    # Save model
    model_path = Path("./models/aapl_predictor.joblib")
    trainer.save_model(model_path)
    print(f"\n💾 Model saved to {model_path}")
    
    # Feature importance
    importance = trainer.get_feature_importance()
    if importance is not None:
        print("\n🔍 Top 10 Important Features:")
        for i, (feature, score) in enumerate(importance.nlargest(10).items(), 1):
            print(f"  {i}. {feature}: {score:.2f}")
    
    return results


def example_2_cross_validation():
    """Example 2: Walk-forward cross-validation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Walk-Forward Cross-Validation")
    print("=" * 70)
    
    # Prepare data
    data = fetch_and_prepare_data("GOOGL", days=500)
    
    # Prepare features and target
    feature_cols = [col for col in data.columns if col not in ['target', 'returns']]
    X = data[feature_cols]
    y = data['target']
    
    # Create model
    model = create_model("xgboost", n_estimators=50, max_depth=5)
    
    # Run walk-forward validation
    print("\n🔄 Running walk-forward validation...")
    cv_results = walk_forward_validate(
        model=model,
        X=X,
        y=y,
        n_splits=5
    )
    
    print(f"\n📊 Cross-Validation Results:")
    print(f"  Mean Score: {cv_results['mean_score']:.4f}")
    print(f"  Std Score: {cv_results['std_score']:.4f}")
    print(f"\n  Individual Folds:")
    for fold in cv_results['fold_results']:
        print(f"    Fold {fold['fold']}: {fold['score']:.4f}")


def example_3_model_comparison():
    """Example 3: Compare multiple models"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Model Comparison")
    print("=" * 70)
    
    # Prepare data
    data = fetch_and_prepare_data("MSFT", days=500)
    
    # Models to compare
    models_config = {
        "XGBoost": {
            "type": "xgboost",
            "params": {"n_estimators": 50, "max_depth": 5}
        },
        "LightGBM": {
            "type": "lightgbm",
            "params": {"n_estimators": 50, "max_depth": 5}
        },
        "Random Forest": {
            "type": "random_forest",
            "params": {"n_estimators": 50, "max_depth": 10}
        }
    }
    
    results = {}
    
    # Train each model
    for name, config in models_config.items():
        print(f"\n🤖 Training {name}...")
        
        trainer = ModelTrainer(
            model_type=config["type"],
            model_params=config["params"],
            config={"task": "classification"}
        )
        
        result = trainer.train(
            data=data,
            target_column="target",
            returns_column="returns",
            verbose=False
        )
        
        results[name] = result['test_metrics']
        
        print(f"  Test Accuracy: {result['test_metrics']['accuracy']:.4f}")
    
    # Compare models
    print("\n" + "=" * 70)
    print("📊 MODEL COMPARISON")
    print("=" * 70)
    
    comparison_df = compare_models(results, metric_name="accuracy")
    print(comparison_df[['Model', 'accuracy', 'precision', 'recall', 'f1_score']])
    
    # Find best model
    best_model = comparison_df.iloc[0]['Model']
    best_acc = comparison_df.iloc[0]['accuracy']
    print(f"\n🏆 Best Model: {best_model} (Accuracy: {best_acc:.4f})")


def example_4_custom_data_split():
    """Example 4: Custom data splitting"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Data Splitting")
    print("=" * 70)
    
    # Prepare data
    data = fetch_and_prepare_data("TSLA", days=365)
    
    # Custom data preparator
    preparator = DataPreparator(
        train_split=0.6,  # 60% training
        val_split=0.2,    # 20% validation
        test_split=0.2,   # 20% test
        shuffle=False     # Don't shuffle time series!
    )
    
    # Create trainer with custom preparator
    trainer = ModelTrainer(
        model_type="xgboost",
        model_params={"n_estimators": 50},
        data_preparator=preparator,
        config={"task": "classification"}
    )
    
    # Train
    results = trainer.train(
        data=data,
        target_column="target",
        returns_column="returns",
        verbose=True
    )
    
    print(f"\n✓ Custom split complete!")


def example_5_production_workflow():
    """Example 5: Complete production workflow"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Production Workflow")
    print("=" * 70)
    
    # 1. Fetch data
    print("\n📊 Step 1: Data Collection")
    data = fetch_and_prepare_data("NVDA", days=730)
    
    # 2. Train model
    print("\n🤖 Step 2: Model Training")
    trainer = ModelTrainer(
        model_type="xgboost",
        model_params={
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1
        },
        config={"task": "classification"}
    )
    
    results = trainer.train(
        data=data,
        target_column="target",
        returns_column="returns",
        verbose=False
    )
    
    # 3. Evaluate
    print("\n📈 Step 3: Evaluation")
    print_metrics_report(results['test_metrics'], "Test Set Performance")
    
    # 4. Save model
    print("\n💾 Step 4: Model Persistence")
    model_dir = Path("./models/production")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = model_dir / f"nvda_predictor_{timestamp}.joblib"
    
    trainer.save_model(model_path)
    print(f"✓ Model saved: {model_path}")
    
    # 5. Feature importance
    print("\n🔍 Step 5: Model Interpretation")
    importance = trainer.get_feature_importance()
    if importance is not None:
        print("Top 5 Features:")
        for i, (feature, score) in enumerate(importance.nlargest(5).items(), 1):
            print(f"  {i}. {feature}: {score:.2f}")
    
    print("\n✅ Production workflow complete!")
    print(f"\n📦 Deliverables:")
    print(f"  - Trained model: {model_path}")
    print(f"  - Test accuracy: {results['test_metrics']['accuracy']:.4f}")
    print(f"  - Ready for deployment!")


def main():
    """Run all examples"""
    print("\n")
    print("🚀 " * 35)
    print("QuantX Complete ML Pipeline Examples")
    print("🚀 " * 35)
    
    try:
        example_1_basic_pipeline()
        example_2_cross_validation()
        example_3_model_comparison()
        example_4_custom_data_split()
        example_5_production_workflow()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        print("""
Key Takeaways:
1. ✅ End-to-end training pipeline
2. ✅ Automatic data splitting
3. ✅ Comprehensive evaluation
4. ✅ Walk-forward cross-validation
5. ✅ Model comparison
6. ✅ Custom data splitting
7. ✅ Production-ready workflow
8. ✅ Model persistence
9. ✅ Feature importance
10. ✅ Trading-specific metrics

🎯 Ready to build production ML trading systems!
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
