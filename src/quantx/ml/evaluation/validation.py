"""
Model Validation Framework

This module provides validation methods for time series models.

Methods:
- Walk-forward validation
- Time series cross-validation
- Purged K-Fold
- Embargo period handling
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Iterator, Optional
from dataclasses import dataclass
from loguru import logger


# ============================================================================
# Validation Split
# ============================================================================

@dataclass
class ValidationSplit:
    """Represents a train/validation split"""
    train_indices: np.ndarray
    val_indices: np.ndarray
    split_number: int


# ============================================================================
# Time Series Splitter Base
# ============================================================================

class TimeSeriesSplitter:
    """
    Base class for time series cross-validation
    
    Ensures no data leakage by respecting temporal order.
    """
    
    def __init__(self, n_splits: int = 5):
        """
        Initialize splitter
        
        Args:
            n_splits: Number of splits
        """
        self.n_splits = n_splits
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate train/validation splits
        
        Args:
            X: Features
            y: Target (optional)
            
        Yields:
            Tuples of (train_indices, val_indices)
        """
        raise NotImplementedError


# ============================================================================
# Walk-Forward Validation
# ============================================================================

class WalkForwardValidation(TimeSeriesSplitter):
    """
    Walk-forward validation for time series
    
    Expands training set at each step, using next period for validation.
    
    Example:
        Split 1: Train [0:100], Val [100:120]
        Split 2: Train [0:120], Val [120:140]
        Split 3: Train [0:140], Val [140:160]
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        val_size: Optional[int] = None,
        min_train_size: Optional[int] = None
    ):
        """
        Initialize walk-forward validation
        
        Args:
            n_splits: Number of splits
            val_size: Size of validation set (if None, auto-calculated)
            min_train_size: Minimum training set size
        """
        super().__init__(n_splits)
        self.val_size = val_size
        self.min_train_size = min_train_size
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """Generate walk-forward splits"""
        n_samples = len(X)
        
        # Calculate validation size
        if self.val_size is None:
            val_size = n_samples // (self.n_splits + 1)
        else:
            val_size = self.val_size
        
        # Calculate minimum training size
        if self.min_train_size is None:
            min_train_size = val_size
        else:
            min_train_size = self.min_train_size
        
        # Generate splits
        for i in range(self.n_splits):
            val_start = min_train_size + i * val_size
            val_end = val_start + val_size
            
            if val_end > n_samples:
                break
            
            train_indices = np.arange(0, val_start)
            val_indices = np.arange(val_start, val_end)
            
            logger.debug(
                f"Split {i+1}: Train size={len(train_indices)}, "
                f"Val size={len(val_indices)}"
            )
            
            yield train_indices, val_indices


# ============================================================================
# Rolling Window Validation
# ============================================================================

class RollingWindowValidation(TimeSeriesSplitter):
    """
    Rolling window validation
    
    Uses fixed-size training window that slides forward.
    
    Example:
        Split 1: Train [0:100], Val [100:120]
        Split 2: Train [20:120], Val [120:140]
        Split 3: Train [40:140], Val [140:160]
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        train_size: int = 100,
        val_size: int = 20,
        step_size: Optional[int] = None
    ):
        """
        Initialize rolling window validation
        
        Args:
            n_splits: Number of splits
            train_size: Size of training window
            val_size: Size of validation window
            step_size: Step size between splits (if None, uses val_size)
        """
        super().__init__(n_splits)
        self.train_size = train_size
        self.val_size = val_size
        self.step_size = step_size or val_size
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """Generate rolling window splits"""
        n_samples = len(X)
        
        for i in range(self.n_splits):
            train_start = i * self.step_size
            train_end = train_start + self.train_size
            val_start = train_end
            val_end = val_start + self.val_size
            
            if val_end > n_samples:
                break
            
            train_indices = np.arange(train_start, train_end)
            val_indices = np.arange(val_start, val_end)
            
            logger.debug(
                f"Split {i+1}: Train [{train_start}:{train_end}], "
                f"Val [{val_start}:{val_end}]"
            )
            
            yield train_indices, val_indices


# ============================================================================
# Purged K-Fold
# ============================================================================

class PurgedKFold(TimeSeriesSplitter):
    """
    Purged K-Fold for time series
    
    Removes samples around validation set to prevent data leakage
    from overlapping observations.
    
    Based on "Advances in Financial Machine Learning" by Marcos López de Prado.
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        purge_gap: int = 0,
        embargo_pct: float = 0.01
    ):
        """
        Initialize purged K-fold
        
        Args:
            n_splits: Number of splits
            purge_gap: Number of samples to purge before validation
            embargo_pct: Percentage of samples to embargo after validation
        """
        super().__init__(n_splits)
        self.purge_gap = purge_gap
        self.embargo_pct = embargo_pct
    
    def split(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None
    ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """Generate purged K-fold splits"""
        n_samples = len(X)
        indices = np.arange(n_samples)
        
        # Calculate fold size
        fold_size = n_samples // self.n_splits
        embargo_size = int(fold_size * self.embargo_pct)
        
        for i in range(self.n_splits):
            # Validation set
            val_start = i * fold_size
            val_end = min((i + 1) * fold_size, n_samples)
            val_indices = indices[val_start:val_end]
            
            # Training set (excluding validation)
            train_indices = np.concatenate([
                indices[:val_start],
                indices[val_end:]
            ])
            
            # Purge samples before validation
            if self.purge_gap > 0:
                purge_start = max(0, val_start - self.purge_gap)
                purge_mask = (train_indices < purge_start) | (train_indices >= val_end)
                train_indices = train_indices[purge_mask]
            
            # Embargo samples after validation
            if embargo_size > 0:
                embargo_end = min(val_end + embargo_size, n_samples)
                embargo_mask = (train_indices < val_start) | (train_indices >= embargo_end)
                train_indices = train_indices[embargo_mask]
            
            logger.debug(
                f"Split {i+1}: Train size={len(train_indices)}, "
                f"Val size={len(val_indices)}, "
                f"Purged={self.purge_gap}, Embargoed={embargo_size}"
            )
            
            yield train_indices, val_indices


# ============================================================================
# Validation Runner
# ============================================================================

class CrossValidator:
    """
    Run cross-validation with any splitter
    
    Example:
        validator = CrossValidator(
            splitter=WalkForwardValidation(n_splits=5)
        )
        
        results = validator.validate(model, X, y)
    """
    
    def __init__(self, splitter: TimeSeriesSplitter):
        """
        Initialize cross-validator
        
        Args:
            splitter: Time series splitter
        """
        self.splitter = splitter
    
    def validate(
        self,
        model,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        metric_fn: Optional[callable] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run cross-validation
        
        Args:
            model: Model to validate (must have fit/predict methods)
            X: Features
            y: Target
            metric_fn: Metric function (if None, uses model.score)
            verbose: Whether to print progress
            
        Returns:
            Dictionary with validation results
        """
        # Convert to numpy
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, (pd.Series, pd.DataFrame)):
            y = y.values
        
        scores = []
        fold_results = []
        
        for fold_num, (train_idx, val_idx) in enumerate(self.splitter.split(X, y), 1):
            if verbose:
                logger.info(f"Fold {fold_num}/{self.splitter.n_splits}")
            
            # Split data
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate
            if metric_fn is not None:
                y_pred = model.predict(X_val)
                score = metric_fn(y_val, y_pred)
            else:
                score = model.score(X_val, y_val)
            
            scores.append(score)
            fold_results.append({
                'fold': fold_num,
                'score': score,
                'train_size': len(train_idx),
                'val_size': len(val_idx)
            })
            
            if verbose:
                logger.info(f"  Score: {score:.4f}")
        
        results = {
            'scores': scores,
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'fold_results': fold_results
        }
        
        if verbose:
            logger.info(
                f"\nCross-validation complete: "
                f"{results['mean_score']:.4f} ± {results['std_score']:.4f}"
            )
        
        return results


# ============================================================================
# Convenience Functions
# ============================================================================

def walk_forward_validate(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    n_splits: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for walk-forward validation
    
    Args:
        model: Model to validate
        X: Features
        y: Target
        n_splits: Number of splits
        **kwargs: Additional arguments for WalkForwardValidation
        
    Returns:
        Validation results
    """
    splitter = WalkForwardValidation(n_splits=n_splits, **kwargs)
    validator = CrossValidator(splitter)
    return validator.validate(model, X, y)


def rolling_window_validate(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    n_splits: int = 5,
    train_size: int = 100,
    val_size: int = 20,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for rolling window validation
    
    Args:
        model: Model to validate
        X: Features
        y: Target
        n_splits: Number of splits
        train_size: Training window size
        val_size: Validation window size
        **kwargs: Additional arguments
        
    Returns:
        Validation results
    """
    splitter = RollingWindowValidation(
        n_splits=n_splits,
        train_size=train_size,
        val_size=val_size,
        **kwargs
    )
    validator = CrossValidator(splitter)
    return validator.validate(model, X, y)


def purged_kfold_validate(
    model,
    X: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    n_splits: int = 5,
    purge_gap: int = 0,
    embargo_pct: float = 0.01,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for purged K-fold validation
    
    Args:
        model: Model to validate
        X: Features
        y: Target
        n_splits: Number of splits
        purge_gap: Purge gap size
        embargo_pct: Embargo percentage
        **kwargs: Additional arguments
        
    Returns:
        Validation results
    """
    splitter = PurgedKFold(
        n_splits=n_splits,
        purge_gap=purge_gap,
        embargo_pct=embargo_pct
    )
    validator = CrossValidator(splitter)
    return validator.validate(model, X, y)
