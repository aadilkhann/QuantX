"""
Model Registry Module.

Provides model management, versioning, and deployment utilities.
"""

try:
    from quantx.ml.registry.mlflow_manager import (
        MLflowManager,
        ExperimentTracker,
        ModelRegistry,
        MLFLOW_AVAILABLE
    )
except ImportError:
    MLFLOW_AVAILABLE = False
    MLflowManager = None
    ExperimentTracker = None
    ModelRegistry = None

__all__ = [
    "MLflowManager",
    "ExperimentTracker",
    "ModelRegistry",
    "MLFLOW_AVAILABLE",
]
