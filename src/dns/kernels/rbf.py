"""Radial basis function kernels."""

from __future__ import annotations

import numpy as np

from dns.kernels.common import pairwise_squared_distances
from dns.synthesis.linear_algebra import as_2d_float


def median_heuristic_gamma(X: np.ndarray, *, eps: float = 1e-12) -> float:
    """Estimate RBF gamma from training data pairwise distances only."""

    X = as_2d_float(X)
    distances = pairwise_squared_distances(X)
    upper = distances[np.triu_indices_from(distances, k=1)]
    positive = upper[upper > eps]
    if positive.size == 0:
        return 1.0
    median_squared_distance = float(np.median(positive))
    return 1.0 / max(2.0 * median_squared_distance, eps)


def rbf_kernel(X: np.ndarray, Y: np.ndarray | None = None, *, gamma: float) -> np.ndarray:
    """Return an RBF kernel matrix."""

    if gamma <= 0.0:
        raise ValueError("gamma must be positive.")
    distances = pairwise_squared_distances(X, Y)
    return np.exp(-gamma * distances)
