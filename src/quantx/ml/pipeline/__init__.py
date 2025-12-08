"""
QuantX ML Pipeline Module

End-to-end training pipelines.

Usage:
    from quantx.ml.pipeline import ModelTrainer, train_model
    
    trainer = ModelTrainer(model_type="xgboost")
    results = trainer.train(data, "target")
"""

from quantx.ml.pipeline.trainer import (
    DataPreparator,
    ModelTrainer,
    train_model
)

__all__ = [
    "DataPreparator",
    "ModelTrainer",
    "train_model",
]
