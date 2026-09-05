"""ReLU feature utilities."""

from __future__ import annotations

import numpy as np


def relu(values: np.ndarray) -> np.ndarray:
    """Apply the rectified linear unit elementwise."""

    return np.maximum(values, 0.0)


def deterministic_relu_projection(
    *,
    n_features: int,
    hidden_units: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a fixed seeded projection for ReLU random-feature baselines."""

    if n_features <= 0:
        raise ValueError("n_features must be positive.")
    if hidden_units <= 0:
        raise ValueError("hidden_units must be positive.")

    rng = np.random.default_rng(seed)
    weights = rng.normal(loc=0.0, scale=1.0 / np.sqrt(n_features), size=(n_features, hidden_units))
    bias = np.linspace(-1.0, 1.0, hidden_units)
    return weights, bias
