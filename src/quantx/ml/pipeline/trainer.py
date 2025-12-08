"""
End-to-End Training Pipeline

This module provides a complete ML training pipeline that orchestrates:
- Data preparation
- Feature engineering
- Model training
- Evaluation
- Model saving

Everything is configurable at runtime!
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Union, List, Tuple
from pathlib import Path
from datetime import datetime
from loguru import logger
from sklearn.model_selection import train_test_split

from quantx.ml.config import get_ml_config
from quantx.ml.features import FeaturePipeline
from quantx.ml.models import create_model
from quantx.ml.evaluation import evaluate_model, print_metrics_report, walk_forward_validate


# ============================================================================
# Data Preparation
# ============================================================================

class DataPreparator:
    """
    Prepare data for ML training
    
    Handles:
    - Train/val/test splitting
    - Target creation
    - Missing value handling
    - Data validation
    """
    
    def __init__(
        self,
        train_split: float = 0.7,
        val_split: float = 0.15,
        test_split: float = 0.15,
        shuffle: bool = False,
        random_state: int = 42
    ):
        """
        Initialize data preparator
        
        Args:
            train_split: Training set proportion
            val_split: Validation set proportion
            test_split: Test set proportion
            shuffle: Whether to shuffle data (False for time series!)
            random_state: Random seed
        """
        self.train_split = train_split
        self.val_split = val_split
        self.test_split = test_split
        self.shuffle = shuffle
        self.random_state = random_state
        
        # Validate splits
        total = train_split + val_split + test_split
        if not np.isclose(total, 1.0):
            raise ValueError(f"Splits must sum to 1.0, got {total}")
    
    def prepare(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        drop_na: bool = True
    ) -> Dict[str, Union[pd.DataFrame, pd.Series]]:
        """
        Prepare data for training
        
        Args:
            X: Features
            y: Target
            drop_na: Whether to drop NaN values
            
        Returns:
            Dictionary with train/val/test splits
        """
        logger.info(f"Preparing data: {len(X)} samples, {len(X.columns)} features")
        
        # Drop NaN if requested
        if drop_na:
            combined = pd.concat([X, y], axis=1)
            combined = combined.dropna()
            X = combined.drop(y.name, axis=1)
            y = combined[y.name]
            logger.info(f"After dropping NaN: {len(X)} samples")
        
        # Calculate split indices
        n = len(X)
        train_end = int(n * self.train_split)
        val_end = int(n * (self.train_split + self.val_split))
        
        # Split data
        if self.shuffle:
            # Shuffle split (not recommended for time series!)
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y,
                test_size=(1 - self.train_split),
                random_state=self.random_state
            )
            
            val_ratio = self.val_split / (self.val_split + self.test_split)
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp,
                test_size=(1 - val_ratio),
                random_state=self.random_state
            )
        else:
            # Time series split (preserves order)
            X_train = X.iloc[:train_end]
            X_val = X.iloc[train_end:val_end]
            X_test = X.iloc[val_end:]
            
            y_train = y.iloc[:train_end]
            y_val = y.iloc[train_end:val_end]
            y_test = y.iloc[val_end:]
        
        logger.info(
            f"Split sizes - Train: {len(X_train)}, "
            f"Val: {len(X_val)}, Test: {len(X_test)}"
        )
        
        return {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test
        }


# ============================================================================
# Model Trainer
# ============================================================================

class ModelTrainer:
    """
    End-to-end model training pipeline
    
    Example:
        trainer = ModelTrainer(
            model_type="xgboost",
            feature_pipeline=pipeline
        )
        
        results = trainer.train(data, target)
    """
    
    def __init__(
        self,
        model_type: str = "xgboost",
        model_params: Optional[Dict[str, Any]] = None,
        feature_pipeline: Optional[FeaturePipeline] = None,
        data_preparator: Optional[DataPreparator] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize model trainer
        
        Args:
            model_type: Type of model to train
            model_params: Model parameters
            feature_pipeline: Feature engineering pipeline
            data_preparator: Data preparation utility
            config: Training configuration
        """
        self.model_type = model_type
        self.model_params = model_params or {}
        self.feature_pipeline = feature_pipeline
        self.data_preparator = data_preparator or DataPreparator()
        
        # Get ML config
        self.ml_config = get_ml_config()
        self.config = config or {}
        
        # Model and results
        self.model = None
        self.results = {}
    
    def train(
        self,
        data: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        returns_column: Optional[str] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Train model end-to-end
        
        Args:
            data: Input DataFrame with features and target
            target_column: Name of target column
            feature_columns: List of feature columns (if None, uses all except target)
            returns_column: Name of returns column (for trading metrics)
            verbose: Whether to print progress
            
        Returns:
            Dictionary with training results
        """
        logger.info("=" * 70)
        logger.info("Starting Model Training Pipeline")
        logger.info("=" * 70)
        
        # Extract features and target
        if feature_columns is None:
            feature_columns = [col for col in data.columns if col != target_column]
        
        X = data[feature_columns]
        y = data[target_column]
        
        # Get returns if provided
        returns = data[returns_column] if returns_column else None
        
        # Prepare data
        logger.info("\n📊 Step 1: Data Preparation")
        splits = self.data_preparator.prepare(X, y)
        
        # Create model
        logger.info(f"\n🤖 Step 2: Creating {self.model_type} model")
        self.model = create_model(
            self.model_type,
            name=f"{self.model_type}_model",
            **self.model_params
        )
        
        # Train model
        logger.info("\n🔧 Step 3: Training model")
        self.model.fit(
            splits['X_train'],
            splits['y_train'],
            verbose=verbose
        )
        
        # Evaluate on all sets
        logger.info("\n📈 Step 4: Evaluation")
        
        task = self.config.get('task', 'classification')
        
        # Training set
        y_train_pred = self.model.predict(splits['X_train'])
        y_train_proba = None
        if task == 'classification':
            try:
                y_train_proba = self.model.predict_proba(splits['X_train'])
            except:
                pass
        
        train_returns = returns.iloc[:len(splits['y_train'])] if returns is not None else None
        train_metrics = evaluate_model(
            splits['y_train'].values,
            y_train_pred,
            y_train_proba,
            task=task,
            returns=train_returns.values if train_returns is not None else None
        )
        
        # Validation set
        y_val_pred = self.model.predict(splits['X_val'])
        y_val_proba = None
        if task == 'classification':
            try:
                y_val_proba = self.model.predict_proba(splits['X_val'])
            except:
                pass
        
        val_start = len(splits['y_train'])
        val_end = val_start + len(splits['y_val'])
        val_returns = returns.iloc[val_start:val_end] if returns is not None else None
        val_metrics = evaluate_model(
            splits['y_val'].values,
            y_val_pred,
            y_val_proba,
            task=task,
            returns=val_returns.values if val_returns is not None else None
        )
        
        # Test set
        y_test_pred = self.model.predict(splits['X_test'])
        y_test_proba = None
        if task == 'classification':
            try:
                y_test_proba = self.model.predict_proba(splits['X_test'])
            except:
                pass
        
        test_start = val_end
        test_returns = returns.iloc[test_start:] if returns is not None else None
        test_metrics = evaluate_model(
            splits['y_test'].values,
            y_test_pred,
            y_test_proba,
            task=task,
            returns=test_returns.values if test_returns is not None else None
        )
        
        # Store results
        self.results = {
            'model': self.model,
            'train_metrics': train_metrics,
            'val_metrics': val_metrics,
            'test_metrics': test_metrics,
            'splits': splits,
            'predictions': {
                'train': y_train_pred,
                'val': y_val_pred,
                'test': y_test_pred
            }
        }
        
        # Print results
        if verbose:
            print_metrics_report(train_metrics, "Training Set")
            print_metrics_report(val_metrics, "Validation Set")
            print_metrics_report(test_metrics, "Test Set")
        
        logger.info("\n✅ Training pipeline complete!")
        
        return self.results
    
    def save_model(self, path: Union[str, Path]) -> None:
        """Save trained model"""
        if self.model is None:
            raise ValueError("No model to save. Train first!")
        
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def get_feature_importance(self) -> Optional[pd.Series]:
        """Get feature importance from trained model"""
        if self.model is None:
            raise ValueError("No model trained yet")
        
        try:
            return self.model.get_feature_importance()
        except AttributeError:
            logger.warning(f"{self.model_type} does not support feature importance")
            return None


# ============================================================================
# Convenience Function
# ============================================================================

def train_model(
    data: pd.DataFrame,
    target_column: str,
    model_type: str = "xgboost",
    model_params: Optional[Dict[str, Any]] = None,
    feature_pipeline: Optional[FeaturePipeline] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for quick model training
    
    Args:
        data: Input DataFrame
        target_column: Target column name
        model_type: Model type
        model_params: Model parameters
        feature_pipeline: Feature pipeline
        **kwargs: Additional training parameters
        
    Returns:
        Training results
    """
    trainer = ModelTrainer(
        model_type=model_type,
        model_params=model_params,
        feature_pipeline=feature_pipeline
    )
    
    return trainer.train(data, target_column, **kwargs)
