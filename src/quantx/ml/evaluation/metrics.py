"""
Model Evaluation Metrics

This module provides comprehensive evaluation metrics for ML models.

Metrics Categories:
- Classification metrics
- Regression metrics
- Trading-specific metrics
- Time series metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Union
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
from loguru import logger


# ============================================================================
# Classification Metrics
# ============================================================================

def calculate_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Calculate comprehensive classification metrics
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Predicted probabilities (optional)
        
    Returns:
        Dictionary of metrics
    """
    metrics = {}
    
    # Basic metrics
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    metrics['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    metrics['f1_score'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    # ROC-AUC (if probabilities provided)
    if y_pred_proba is not None:
        try:
            if len(np.unique(y_true)) == 2:  # Binary classification
                metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba[:, 1])
            else:  # Multi-class
                metrics['roc_auc'] = roc_auc_score(
                    y_true, y_pred_proba, multi_class='ovr', average='weighted'
                )
        except Exception as e:
            logger.warning(f"Could not calculate ROC-AUC: {e}")
            metrics['roc_auc'] = np.nan
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics['confusion_matrix'] = cm.tolist()
    
    return metrics


# ============================================================================
# Regression Metrics
# ============================================================================

def calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Calculate comprehensive regression metrics
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary of metrics
    """
    metrics = {}
    
    # Basic metrics
    metrics['mse'] = mean_squared_error(y_true, y_pred)
    metrics['rmse'] = np.sqrt(metrics['mse'])
    metrics['mae'] = mean_absolute_error(y_true, y_pred)
    metrics['r2'] = r2_score(y_true, y_pred)
    
    # MAPE (Mean Absolute Percentage Error)
    # Avoid division by zero
    mask = y_true != 0
    if mask.sum() > 0:
        metrics['mape'] = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        metrics['mape'] = np.nan
    
    # Adjusted R²
    n = len(y_true)
    p = 1  # Assuming single feature for simplicity
    if n > p + 1:
        metrics['adjusted_r2'] = 1 - (1 - metrics['r2']) * (n - 1) / (n - p - 1)
    else:
        metrics['adjusted_r2'] = np.nan
    
    return metrics


# ============================================================================
# Trading-Specific Metrics
# ============================================================================

def calculate_trading_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    returns: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Calculate trading-specific metrics
    
    Args:
        y_true: True direction (1=up, 0=down)
        y_pred: Predicted direction
        returns: Actual returns (optional)
        
    Returns:
        Dictionary of trading metrics
    """
    metrics = {}
    
    # Directional accuracy
    metrics['directional_accuracy'] = accuracy_score(y_true, y_pred)
    
    # Precision for long signals (when we predict up)
    long_mask = y_pred == 1
    if long_mask.sum() > 0:
        metrics['long_precision'] = precision_score(
            y_true[long_mask], y_pred[long_mask], zero_division=0
        )
    else:
        metrics['long_precision'] = np.nan
    
    # Precision for short signals (when we predict down)
    short_mask = y_pred == 0
    if short_mask.sum() > 0:
        metrics['short_precision'] = precision_score(
            y_true[short_mask], y_pred[short_mask], zero_division=0
        )
    else:
        metrics['short_precision'] = np.nan
    
    # If returns provided, calculate strategy returns
    if returns is not None:
        # Strategy returns: go long when predict up, short when predict down
        strategy_returns = np.where(y_pred == 1, returns, -returns)
        
        metrics['strategy_return'] = np.sum(strategy_returns)
        metrics['strategy_sharpe'] = (
            np.mean(strategy_returns) / np.std(strategy_returns) * np.sqrt(252)
            if np.std(strategy_returns) > 0 else 0
        )
        
        # Win rate
        winning_trades = strategy_returns > 0
        metrics['win_rate'] = np.mean(winning_trades) if len(winning_trades) > 0 else 0
        
        # Profit factor
        gross_profit = np.sum(strategy_returns[strategy_returns > 0])
        gross_loss = abs(np.sum(strategy_returns[strategy_returns < 0]))
        metrics['profit_factor'] = (
            gross_profit / gross_loss if gross_loss > 0 else np.inf
        )
    
    return metrics


# ============================================================================
# Information Coefficient
# ============================================================================

def calculate_information_coefficient(
    predictions: np.ndarray,
    returns: np.ndarray
) -> float:
    """
    Calculate Information Coefficient (IC)
    
    Measures correlation between predictions and actual returns.
    
    Args:
        predictions: Model predictions
        returns: Actual returns
        
    Returns:
        Information coefficient
    """
    return np.corrcoef(predictions, returns)[0, 1]


# ============================================================================
# Comprehensive Evaluation
# ============================================================================

def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
    task: str = "classification",
    returns: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Comprehensive model evaluation
    
    Args:
        y_true: True labels/values
        y_pred: Predictions
        y_pred_proba: Prediction probabilities (for classification)
        task: Task type ("classification" or "regression")
        returns: Actual returns (for trading metrics)
        
    Returns:
        Dictionary of all metrics
    """
    metrics = {}
    
    if task == "classification":
        # Classification metrics
        class_metrics = calculate_classification_metrics(y_true, y_pred, y_pred_proba)
        metrics.update(class_metrics)
        
        # Trading metrics (if binary classification)
        if len(np.unique(y_true)) == 2:
            trading_metrics = calculate_trading_metrics(y_true, y_pred, returns)
            metrics.update(trading_metrics)
    
    elif task == "regression":
        # Regression metrics
        reg_metrics = calculate_regression_metrics(y_true, y_pred)
        metrics.update(reg_metrics)
        
        # Information coefficient (if returns provided)
        if returns is not None:
            metrics['information_coefficient'] = calculate_information_coefficient(
                y_pred, returns
            )
    
    return metrics


# ============================================================================
# Metrics Reporting
# ============================================================================

def print_metrics_report(metrics: Dict[str, Any], title: str = "Model Evaluation") -> None:
    """
    Print formatted metrics report
    
    Args:
        metrics: Dictionary of metrics
        title: Report title
    """
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)
    
    # Group metrics by category
    classification_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
    regression_metrics = ['mse', 'rmse', 'mae', 'r2', 'mape', 'adjusted_r2']
    trading_metrics = [
        'directional_accuracy', 'long_precision', 'short_precision',
        'strategy_return', 'strategy_sharpe', 'win_rate', 'profit_factor',
        'information_coefficient'
    ]
    
    # Print classification metrics
    class_found = False
    for metric in classification_metrics:
        if metric in metrics and not np.isnan(metrics[metric]):
            if not class_found:
                print("\n📊 Classification Metrics:")
                class_found = True
            print(f"  {metric.replace('_', ' ').title()}: {metrics[metric]:.4f}")
    
    # Print regression metrics
    reg_found = False
    for metric in regression_metrics:
        if metric in metrics and not np.isnan(metrics[metric]):
            if not reg_found:
                print("\n📈 Regression Metrics:")
                reg_found = True
            print(f"  {metric.upper()}: {metrics[metric]:.4f}")
    
    # Print trading metrics
    trading_found = False
    for metric in trading_metrics:
        if metric in metrics and not np.isnan(metrics[metric]):
            if not trading_found:
                print("\n💰 Trading Metrics:")
                trading_found = True
            
            value = metrics[metric]
            if metric in ['strategy_return', 'strategy_sharpe']:
                print(f"  {metric.replace('_', ' ').title()}: {value:.4f}")
            elif metric in ['win_rate', 'long_precision', 'short_precision', 'directional_accuracy']:
                print(f"  {metric.replace('_', ' ').title()}: {value:.2%}")
            else:
                print(f"  {metric.replace('_', ' ').title()}: {value:.4f}")
    
    # Print confusion matrix if available
    if 'confusion_matrix' in metrics:
        print("\n🔢 Confusion Matrix:")
        cm = np.array(metrics['confusion_matrix'])
        print(cm)
    
    print("=" * 70)


# ============================================================================
# Metrics Comparison
# ============================================================================

def compare_models(
    model_metrics: Dict[str, Dict[str, float]],
    metric_name: str = "accuracy"
) -> pd.DataFrame:
    """
    Compare multiple models based on metrics
    
    Args:
        model_metrics: Dictionary of {model_name: metrics_dict}
        metric_name: Primary metric for comparison
        
    Returns:
        DataFrame with model comparison
    """
    comparison = []
    
    for model_name, metrics in model_metrics.items():
        row = {"Model": model_name}
        row.update(metrics)
        comparison.append(row)
    
    df = pd.DataFrame(comparison)
    
    # Sort by primary metric (descending)
    if metric_name in df.columns:
        df = df.sort_values(metric_name, ascending=False)
    
    return df
