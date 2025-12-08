"""
QuantX ML Models Module

Flexible, runtime-configurable ML models for trading.

Usage:
    from quantx.ml.models import (
        XGBoostModel,
        LightGBMModel,
        RandomForestModel,
        create_model
    )
    
    # Create model
    model = XGBoostModel(name="my_model", n_estimators=200)
    
    # Or use factory
    model = create_model("xgboost", n_estimators=200)
    
    # Train
    model.fit(X_train, y_train)
    
    # Predict
    predictions = model.predict(X_test)
"""

from quantx.ml.models.base import (
    BaseModel,
    SupervisedModel,
    TimeSeriesModel,
    ReinforcementLearningModel,
    ModelMetadata
)

from quantx.ml.models.traditional import (
    XGBoostModel,
    LightGBMModel,
    RandomForestModel,
    create_model
)

__all__ = [
    # Base classes
    "BaseModel",
    "SupervisedModel",
    "TimeSeriesModel",
    "ReinforcementLearningModel",
    "ModelMetadata",
    
    # Traditional ML models
    "XGBoostModel",
    "LightGBMModel",
    "RandomForestModel",
    
    # Factory
    "create_model",
]
