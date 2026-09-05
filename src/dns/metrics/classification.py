"""Classification metrics for DNS experiments."""

from __future__ import annotations

import numpy as np


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return the fraction of exactly matched labels."""

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape.")
    if y_true.size == 0:
        raise ValueError("accuracy_score requires at least one sample.")
    return float(np.mean(y_true == y_pred))
