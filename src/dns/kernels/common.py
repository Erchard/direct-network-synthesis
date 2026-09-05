"""Common kernel helpers."""

from __future__ import annotations

import numpy as np

from dns.synthesis.linear_algebra import as_2d_float


def pairwise_squared_distances(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Return squared Euclidean distances for all pairs in X and Y."""

    X = as_2d_float(X)
    Y = X if Y is None else as_2d_float(Y)
    x_norm = np.sum(X * X, axis=1)[:, None]
    y_norm = np.sum(Y * Y, axis=1)[None, :]
    distances = x_norm + y_norm - 2.0 * (X @ Y.T)
    return np.maximum(distances, 0.0)


def linear_kernel(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Return the linear kernel matrix X @ Y.T."""

    X = as_2d_float(X)
    Y = X if Y is None else as_2d_float(Y)
    return X @ Y.T
