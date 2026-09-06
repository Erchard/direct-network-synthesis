"""Shared linear algebra primitives for closed-form experiments."""

from __future__ import annotations

from collections.abc import Iterable

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


def solve_streaming_primal_ridge(
    feature_blocks: Iterable[np.ndarray],
    target_blocks: Iterable[np.ndarray],
    *,
    alpha: float,
    fit_intercept: bool = True,
) -> np.ndarray:
    """Solve ridge regression from one pass over matching feature/target blocks.

    The iterables are consumed once and only the feature-space normal equations
    are retained. Callers remain responsible for deterministic block order.
    """

    if alpha < 0.0:
        raise ValueError("alpha must be non-negative.")

    lhs: np.ndarray | None = None
    rhs: np.ndarray | None = None
    feature_count: int | None = None
    target_count: int | None = None
    block_count = 0

    for features_raw, targets_raw in zip(feature_blocks, target_blocks, strict=True):
        features = as_2d_float(features_raw)
        targets, _ = as_target_matrix(targets_raw)
        if features.shape[0] != targets.shape[0]:
            raise ValueError("features and targets must contain the same number of samples.")
        if features.shape[0] == 0:
            continue
        if feature_count is None:
            feature_count = features.shape[1]
            target_count = targets.shape[1]
            design_width = feature_count + int(fit_intercept)
            lhs = np.zeros((design_width, design_width), dtype=float)
            rhs = np.zeros((design_width, target_count), dtype=float)
        elif features.shape[1] != feature_count or targets.shape[1] != target_count:
            raise ValueError("All blocks must have consistent feature and target widths.")

        design = (
            np.column_stack([np.ones(features.shape[0]), features])
            if fit_intercept
            else features
        )
        lhs += design.T @ design
        rhs += design.T @ targets
        block_count += 1

    if block_count == 0 or lhs is None or rhs is None:
        raise ValueError("At least one non-empty feature block is required.")

    penalty = alpha * np.eye(lhs.shape[0])
    if fit_intercept:
        penalty[0, 0] = 0.0
    return stable_solve(0.5 * (lhs + lhs.T) + penalty, rhs)
