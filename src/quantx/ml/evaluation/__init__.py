"""
QuantX ML Evaluation Module

Comprehensive model evaluation and validation.

Usage:
    from quantx.ml.evaluation import (
        evaluate_model,
        print_metrics_report,
        walk_forward_validate,
        CrossValidator
    )
"""

from quantx.ml.evaluation.metrics import (
    calculate_classification_metrics,
    calculate_regression_metrics,
    calculate_trading_metrics,
    calculate_information_coefficient,
    evaluate_model,
    print_metrics_report,
    compare_models
)

from quantx.ml.evaluation.validation import (
    TimeSeriesSplitter,
    WalkForwardValidation,
    RollingWindowValidation,
    PurgedKFold,
    CrossValidator,
    walk_forward_validate,
    rolling_window_validate,
    purged_kfold_validate
)

__all__ = [
    # Metrics
    "calculate_classification_metrics",
    "calculate_regression_metrics",
    "calculate_trading_metrics",
    "calculate_information_coefficient",
    "evaluate_model",
    "print_metrics_report",
    "compare_models",
    
    # Validation
    "TimeSeriesSplitter",
    "WalkForwardValidation",
    "RollingWindowValidation",
    "PurgedKFold",
    "CrossValidator",
    "walk_forward_validate",
    "rolling_window_validate",
    "purged_kfold_validate",
]
