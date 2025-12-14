"""
MLflow Integration Example - Experiment tracking and model registry.

This example demonstrates:
1. Tracking training experiments
2. Logging parameters and metrics
3. Registering models
4. Loading models from registry
5. Comparing model versions
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
from quantx.ml.models import XGBoostModel, LightGBMModel, RandomForestModel

# Check if MLflow is available
try:
    from quantx.ml.registry import MLflowManager, ExperimentTracker, ModelRegistry, MLFLOW_AVAILABLE
    if not MLFLOW_AVAILABLE:
        raise ImportError("MLflow not available")
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available. Install with: pip install mlflow")


def example_1_track_experiment():
    """Example 1: Track a training experiment with MLflow."""
    if not MLFLOW_AVAILABLE:
        logger.warning("Skipping MLflow example - MLflow not available")
        return
    
    logger.info("=" * 80)
    logger.info("Example 1: Track Training Experiment")
    logger.info("=" * 80)
    
    # Setup MLflow
    mlflow_dir = project_root / "data" / "mlruns"
    mlflow_dir.mkdir(parents=True, exist_ok=True)
    
    manager = MLflowManager(
        tracking_uri=f"file://{mlflow_dir}",
        experiment_name="quantx_examples"
    )
    
    # Prepare data
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    pipeline = FeaturePipeline([
        TechnicalFeatures(ma_periods=[10, 20, 50], include_rsi=True, include_macd=True),
        StatisticalFeatures(return_periods=[1, 5, 10])
    ])
    
    features = pipeline.transform(data)
    features['target'] = (data['close'].pct_change().shift(-1) > 0).astype(int)
    features = features.dropna()
    
    train_size = int(len(features) * 0.7)
    X_train = features.iloc[:train_size].drop('target', axis=1)
    y_train = features.iloc[:train_size]['target']
    X_test = features.iloc[train_size:].drop('target', axis=1)
    y_test = features.iloc[train_size:]['target']
    
    # Train with MLflow tracking
    logger.info("Training XGBoost with MLflow tracking...")
    
    with manager.start_run(run_name="xgboost_v1") as run:
        # Log parameters
        params = {
            "model_type": "xgboost",
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "num_features": len(X_train.columns)
        }
        manager.log_params(params)
        
        # Train model
        model = XGBoostModel(
            name="xgb_v1",
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1
        )
        model.fit(X_train, y_train, verbose=False)
        
        # Evaluate
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        predictions = model.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions),
            "recall": recall_score(y_test, predictions),
            "f1_score": f1_score(y_test, predictions)
        }
        manager.log_metrics(metrics)
        
        # Log model
        manager.log_model(model.model, "model")
        
        logger.info(f"Run ID: {run.info.run_id}")
        logger.info(f"Metrics: {metrics}")
    
    logger.info(f"\nMLflow UI: mlflow ui --backend-store-uri {mlflow_dir}")
    logger.info("Then open http://localhost:5000")


def example_2_register_model():
    """Example 2: Register a model in MLflow model registry."""
    if not MLFLOW_AVAILABLE:
        logger.warning("Skipping model registry example - MLflow not available")
        return
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: Register Model in Registry")
    logger.info("=" * 80)
    
    mlflow_dir = project_root / "data" / "mlruns"
    
    tracker = ExperimentTracker(
        experiment_name="quantx_models",
        tracking_uri=f"file://{mlflow_dir}"
    )
    
    # Prepare data (simplified)
    provider = YahooFinanceProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = provider.get_historical_data("AAPL", start_date, end_date)
    
    pipeline = FeaturePipeline([
        TechnicalFeatures(ma_periods=[10, 20], include_rsi=True),
        StatisticalFeatures(return_periods=[1, 5])
    ])
    
    features = pipeline.transform(data)
    features['target'] = (data['close'].pct_change().shift(-1) > 0).astype(int)
    features = features.dropna()
    
    train_size = int(len(features) * 0.8)
    X_train = features.iloc[:train_size].drop('target', axis=1)
    y_train = features.iloc[:train_size]['target']
    X_test = features.iloc[train_size:].drop('target', axis=1)
    y_test = features.iloc[train_size:]['target']
    
    # Train and register
    logger.info("Training and registering model...")
    
    model = XGBoostModel(name="xgb_prod", n_estimators=100)
    model.fit(X_train, y_train, verbose=False)
    
    predictions = model.predict(X_test)
    from sklearn.metrics import accuracy_score, f1_score
    
    run_id = tracker.track_training(
        model=model.model,
        params={"n_estimators": 100, "max_depth": 6},
        metrics={
            "accuracy": accuracy_score(y_test, predictions),
            "f1_score": f1_score(y_test, predictions)
        },
        run_name="xgb_production_candidate",
        register_model=True,
        model_name="AAPL_Direction_Classifier"
    )
    
    logger.info(f"Model registered! Run ID: {run_id}")
    logger.info("Model name: AAPL_Direction_Classifier")


def example_3_load_from_registry():
    """Example 3: Load a model from the registry."""
    if not MLFLOW_AVAILABLE:
        logger.warning("Skipping load example - MLflow not available")
        return
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Load Model from Registry")
    logger.info("=" * 80)
    
    mlflow_dir = project_root / "data" / "mlruns"
    
    registry = ModelRegistry(tracking_uri=f"file://{mlflow_dir}")
    
    try:
        logger.info("Loading latest model...")
        model = registry.load_latest_model("AAPL_Direction_Classifier")
        logger.info("Model loaded successfully!")
        logger.info(f"Model type: {type(model)}")
        
    except Exception as e:
        logger.warning(f"Could not load model: {e}")
        logger.info("Make sure to run Example 2 first to register a model")


def example_4_compare_models():
    """Example 4: Train multiple models and compare in MLflow."""
    if not MLFLOW_AVAILABLE:
        logger.warning("Skipping comparison example - MLflow not available")
        return
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 4: Compare Multiple Models")
    logger.info("=" * 80)
    
    mlflow_dir = project_root / "data" / "mlruns"
    manager = MLflowManager(
        tracking_uri=f"file://{mlflow_dir}",
        experiment_name="model_comparison"
    )
    
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
    features['target'] = (data['close'].pct_change().shift(-1) > 0).astype(int)
    features = features.dropna()
    
    train_size = int(len(features) * 0.8)
    X_train = features.iloc[:train_size].drop('target', axis=1)
    y_train = features.iloc[:train_size]['target']
    X_test = features.iloc[train_size:].drop('target', axis=1)
    y_test = features.iloc[train_size:]['target']
    
    # Train multiple models
    models = [
        ("XGBoost", XGBoostModel(name="xgb", n_estimators=100)),
        ("LightGBM", LightGBMModel(name="lgb", n_estimators=100)),
        ("Random Forest", RandomForestModel(name="rf", n_estimators=100))
    ]
    
    results = []
    
    for model_name, model in models:
        logger.info(f"\nTraining {model_name}...")
        
        with manager.start_run(run_name=model_name.lower().replace(" ", "_")):
            # Train
            model.fit(X_train, y_train, verbose=False)
            
            # Evaluate
            predictions = model.predict(X_test)
            
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            metrics = {
                "accuracy": accuracy_score(y_test, predictions),
                "precision": precision_score(y_test, predictions),
                "recall": recall_score(y_test, predictions),
                "f1_score": f1_score(y_test, predictions)
            }
            
            # Log
            manager.log_params({"model_type": model_name, "n_estimators": 100})
            manager.log_metrics(metrics)
            manager.log_model(model.model, "model")
            
            results.append((model_name, metrics))
            logger.info(f"{model_name} - Accuracy: {metrics['accuracy']:.3f}, F1: {metrics['f1_score']:.3f}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Model Comparison Summary:")
    logger.info("=" * 80)
    for model_name, metrics in results:
        logger.info(f"{model_name:15s} - Accuracy: {metrics['accuracy']:.3f}, F1: {metrics['f1_score']:.3f}")
    
    best_model = max(results, key=lambda x: x[1]['f1_score'])
    logger.info(f"\nBest model: {best_model[0]} (F1: {best_model[1]['f1_score']:.3f})")


def example_5_production_workflow():
    """Example 5: Complete production workflow with MLflow."""
    if not MLFLOW_AVAILABLE:
        logger.warning("Skipping production workflow example - MLflow not available")
        return
    
    logger.info("\n" + "=" * 80)
    logger.info("Example 5: Production Workflow")
    logger.info("=" * 80)
    
    logger.info("\nProduction Workflow Steps:")
    logger.info("1. Train model with experiment tracking")
    logger.info("2. Register model in registry")
    logger.info("3. Transition to 'Staging' for testing")
    logger.info("4. Validate on staging data")
    logger.info("5. Promote to 'Production' if validation passes")
    logger.info("6. Load production model in trading strategy")
    logger.info("7. Monitor performance and retrain as needed")
    
    logger.info("\nExample code:")
    logger.info("""
    # 1. Train and register
    tracker = ExperimentTracker("trading_models")
    run_id = tracker.track_training(
        model=model,
        params=params,
        metrics=metrics,
        register_model=True,
        model_name="Production_Classifier"
    )
    
    # 2. Promote to staging
    registry = ModelRegistry()
    registry.manager.transition_model_stage(
        name="Production_Classifier",
        version=1,
        stage="Staging"
    )
    
    # 3. Validate in staging
    staging_model = registry.load_staging_model("Production_Classifier")
    # ... run validation ...
    
    # 4. Promote to production
    if validation_passed:
        registry.promote_to_production("Production_Classifier", version=1)
    
    # 5. Use in strategy
    production_model = registry.load_production_model("Production_Classifier")
    strategy = MLClassifierStrategy(model=production_model, ...)
    """)


def main():
    """Run all examples."""
    logger.info("MLflow Integration Examples")
    logger.info("=" * 80)
    
    if not MLFLOW_AVAILABLE:
        logger.error("MLflow is not available!")
        logger.error("Install with: pip install mlflow")
        return
    
    try:
        # Example 1: Track experiment
        example_1_track_experiment()
        
        # Example 2: Register model
        example_2_register_model()
        
        # Example 3: Load from registry
        example_3_load_from_registry()
        
        # Example 4: Compare models
        example_4_compare_models()
        
        # Example 5: Production workflow
        example_5_production_workflow()
        
        logger.info("\n" + "=" * 80)
        logger.info("All MLflow examples completed!")
        logger.info("=" * 80)
        logger.info("\nTo view results:")
        mlflow_dir = Path(__file__).parent.parent.parent / "data" / "mlruns"
        logger.info(f"  mlflow ui --backend-store-uri file://{mlflow_dir}")
        logger.info("  Then open http://localhost:5000")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
