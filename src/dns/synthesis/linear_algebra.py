"""Shared linear algebra primitives for closed-form experiments."""

from __future__ import annotations

import numpy as np


def as_2d_float(X: np.ndarray) -> np.ndarray:
    array = np.asarray(X, dtype=float)
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    if array.ndim != 2:
        raise ValueError("Expected a 2D array.")
    return array


def as_target_matrix(y: np.ndarray) -> tuple[np.ndarray, bool]:
    array = np.asarray(y, dtype=float)
    was_1d = array.ndim == 1
    if was_1d:
        array = array.reshape(-1, 1)
    if array.ndim != 2:
        raise ValueError("Expected a 1D or 2D target array.")
    return array, was_1d


def stable_solve(lhs: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Solve a linear system, falling back to least squares for singular matrices."""

    try:
        return np.linalg.solve(lhs, rhs)
    except np.linalg.LinAlgError:
        solution, *_ = np.linalg.lstsq(lhs, rhs, rcond=None)
        return solution


def solve_primal_ridge(
    features: np.ndarray,
    targets: np.ndarray,
    *,
    alpha: float,
    fit_intercept: bool = True,
) -> np.ndarray:
    """Solve ridge regression in primal form."""

    if alpha < 0.0:
        raise ValueError("alpha must be non-negative.")

    features = as_2d_float(features)
    targets, _ = as_target_matrix(targets)
    if features.shape[0] != targets.shape[0]:
        raise ValueError("features and targets must contain the same number of samples.")

    design = np.column_stack([np.ones(features.shape[0]), features]) if fit_intercept else features
    penalty = alpha * np.eye(design.shape[1])
    if fit_intercept:
        penalty[0, 0] = 0.0
    lhs = design.T @ design + penalty
    rhs = design.T @ targets
    return stable_solve(lhs, rhs)
