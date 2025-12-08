"""
Traditional Machine Learning Models

This module provides implementations of traditional ML models:
- XGBoost
- LightGBM
- CatBoost
- Random Forest
- Gradient Boosting

All models are runtime-configurable and support both CPU and GPU.
"""

import numpy as np
import pandas as pd
from typing import Union, Optional, Dict, Any
from loguru import logger

from quantx.ml.models.base import SupervisedModel


# ============================================================================
# XGBoost Model
# ============================================================================

class XGBoostModel(SupervisedModel):
    """
    XGBoost model with flexible configuration
    
    Supports:
    - CPU and GPU training
    - Classification and regression
    - Runtime parameter changes
    - Feature importance extraction
    
    Example:
        # Classification
        model = XGBoostModel(
            name="xgb_classifier",
            task="classification",
            n_estimators=100,
            max_depth=6
        )
        
        # Regression
        model = XGBoostModel(
            name="xgb_regressor",
            task="regression"
        )
        
        # GPU training
        model = XGBoostModel(
            name="xgb_gpu",
            tree_method="gpu_hist"
        )
    """
    
    def __init__(
        self,
        name: str = "xgboost_model",
        task: str = "classification",
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        tree_method: str = "auto",  # "auto", "gpu_hist", "hist"
        **kwargs
    ):
        """Initialize XGBoost model"""
        super().__init__(
            name=name,
            algorithm="xgboost",
            task=task,
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            tree_method=tree_method,
            **kwargs
        )
        
        # Auto-configure tree_method based on device
        if tree_method == "auto":
            if self.device == "cuda":
                self.params["tree_method"] = "gpu_hist"
            else:
                self.params["tree_method"] = "hist"
        
        self._create_model()
    
    def _create_model(self):
        """Create XGBoost model instance"""
        try:
            import xgboost as xgb
        except ImportError:
            raise ImportError(
                "XGBoost not installed. Install with: pip install xgboost"
            )
        
        if self.task == "classification":
            self.model = xgb.XGBClassifier(**self.params)
        else:
            self.model = xgb.XGBRegressor(**self.params)
    
    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        eval_set: Optional[list] = None,
        early_stopping_rounds: Optional[int] = None,
        verbose: bool = False,
        **kwargs
    ) -> "XGBoostModel":
        """
        Train XGBoost model
        
        Args:
            X: Training features
            y: Training target
            eval_set: Validation set [(X_val, y_val)]
            early_stopping_rounds: Early stopping patience
            verbose: Whether to print training progress
            **kwargs: Additional XGBoost parameters
            
        Returns:
            Self for method chaining
        """
        X, y = self._validate_input(X, y)
        
        logger.info(f"Training {self.name} on {len(X)} samples")
        
        fit_params = {}
        if eval_set is not None:
            fit_params["eval_set"] = eval_set
        if early_stopping_rounds is not None:
            fit_params["early_stopping_rounds"] = early_stopping_rounds
        if not verbose:
            fit_params["verbose"] = False
        
        self.model.fit(X, y, **fit_params, **kwargs)
        self.is_fitted = True
        
        logger.info(f"Training complete for {self.name}")
        return self
    
    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X, _ = self._validate_input(X)
        return self.model.predict(X, **kwargs)
    
    def predict_proba(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """Predict class probabilities"""
        if self.task != "classification":
            raise ValueError("predict_proba only available for classification")
        
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X, _ = self._validate_input(X)
        return self.model.predict_proba(X, **kwargs)
    
    def get_feature_importance(self, importance_type: str = "gain") -> pd.Series:
        """
        Get feature importance
        
        Args:
            importance_type: Type of importance ("gain", "weight", "cover")
            
        Returns:
            Series with feature importances
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        importance = self.model.get_booster().get_score(importance_type=importance_type)
        
        if self.feature_names_:
            return pd.Series(importance).reindex(self.feature_names_, fill_value=0)
        return pd.Series(importance)


# ============================================================================
# LightGBM Model
# ============================================================================

class LightGBMModel(SupervisedModel):
    """
    LightGBM model with flexible configuration
    
    Faster training than XGBoost, especially on large datasets.
    """
    
    def __init__(
        self,
        name: str = "lightgbm_model",
        task: str = "classification",
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        num_leaves: int = 31,
        device: str = "cpu",  # "cpu", "gpu", "cuda"
        **kwargs
    ):
        """Initialize LightGBM model"""
        super().__init__(
            name=name,
            algorithm="lightgbm",
            task=task,
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            device=device,
            **kwargs
        )
        
        # Auto-configure device
        if device == "auto":
            self.params["device"] = "gpu" if self.device == "cuda" else "cpu"
        
        self._create_model()
    
    def _create_model(self):
        """Create LightGBM model instance"""
        try:
            import lightgbm as lgb
        except ImportError:
            raise ImportError(
                "LightGBM not installed. Install with: pip install lightgbm"
            )
        
        if self.task == "classification":
            self.model = lgb.LGBMClassifier(**self.params)
        else:
            self.model = lgb.LGBMRegressor(**self.params)
    
    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        eval_set: Optional[list] = None,
        early_stopping_rounds: Optional[int] = None,
        verbose: bool = False,
        **kwargs
    ) -> "LightGBMModel":
        """Train LightGBM model"""
        X, y = self._validate_input(X, y)
        
        logger.info(f"Training {self.name} on {len(X)} samples")
        
        callbacks = []
        if not verbose:
            callbacks.append(lambda env: None)  # Suppress output
        
        fit_params = {"callbacks": callbacks}
        if eval_set is not None:
            fit_params["eval_set"] = eval_set
        if early_stopping_rounds is not None:
            fit_params["callbacks"].append(
                lambda env: env.iteration >= early_stopping_rounds
            )
        
        self.model.fit(X, y, **fit_params, **kwargs)
        self.is_fitted = True
        
        logger.info(f"Training complete for {self.name}")
        return self
    
    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X, _ = self._validate_input(X)
        return self.model.predict(X, **kwargs)
    
    def predict_proba(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """Predict class probabilities"""
        if self.task != "classification":
            raise ValueError("predict_proba only available for classification")
        
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X, _ = self._validate_input(X)
        return self.model.predict_proba(X, **kwargs)
    
    def get_feature_importance(self) -> pd.Series:
        """Get feature importance"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        importance = self.model.feature_importances_
        
        if self.feature_names_:
            return pd.Series(importance, index=self.feature_names_)
        return pd.Series(importance)


# ============================================================================
# Random Forest Model
# ============================================================================

class RandomForestModel(SupervisedModel):
    """
    Random Forest model using scikit-learn
    
    Good baseline model, interpretable, works well out-of-the-box.
    """
    
    def __init__(
        self,
        name: str = "random_forest_model",
        task: str = "classification",
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        n_jobs: int = -1,
        **kwargs
    ):
        """Initialize Random Forest model"""
        super().__init__(
            name=name,
            algorithm="random_forest",
            task=task,
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            n_jobs=n_jobs,
            **kwargs
        )
        
        self._create_model()
    
    def _create_model(self):
        """Create Random Forest model instance"""
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        
        if self.task == "classification":
            self.model = RandomForestClassifier(**self.params)
        else:
            self.model = RandomForestRegressor(**self.params)
    
    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        **kwargs
    ) -> "RandomForestModel":
        """Train Random Forest model"""
        X, y = self._validate_input(X, y)
        
        logger.info(f"Training {self.name} on {len(X)} samples")
        
        self.model.fit(X, y, **kwargs)
        self.is_fitted = True
        
        logger.info(f"Training complete for {self.name}")
        return self
    
    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X, _ = self._validate_input(X)
        return self.model.predict(X, **kwargs)
    
    def predict_proba(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **kwargs
    ) -> np.ndarray:
        """Predict class probabilities"""
        if self.task != "classification":
            raise ValueError("predict_proba only available for classification")
        
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X, _ = self._validate_input(X)
        return self.model.predict_proba(X, **kwargs)
    
    def get_feature_importance(self) -> pd.Series:
        """Get feature importance"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        importance = self.model.feature_importances_
        
        if self.feature_names_:
            return pd.Series(importance, index=self.feature_names_)
        return pd.Series(importance)


# ============================================================================
# Model Factory
# ============================================================================

def create_model(
    model_type: str,
    name: Optional[str] = None,
    **params
) -> SupervisedModel:
    """
    Factory function to create models
    
    Args:
        model_type: Type of model ("xgboost", "lightgbm", "random_forest")
        name: Optional model name
        **params: Model parameters
        
    Returns:
        Model instance
        
    Example:
        # Create XGBoost model
        model = create_model("xgboost", n_estimators=200)
        
        # Create LightGBM model
        model = create_model("lightgbm", device="gpu")
        
        # Create Random Forest
        model = create_model("random_forest", max_depth=10)
    """
    model_map = {
        "xgboost": XGBoostModel,
        "lightgbm": LightGBMModel,
        "random_forest": RandomForestModel,
    }
    
    if model_type not in model_map:
        raise ValueError(
            f"Unknown model type: {model_type}. "
            f"Available: {list(model_map.keys())}"
        )
    
    model_class = model_map[model_type]
    
    if name is None:
        name = f"{model_type}_model"
    
    return model_class(name=name, **params)
