"""Preprocessing helpers that fit only on training data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from dns.synthesis.linear_algebra import as_2d_float


@dataclass
class Standardizer:
    """Mean/scale standardization with train-only fitted statistics."""

    eps: float = 1e-12

    def fit(self, X: np.ndarray) -> Standardizer:
        X = as_2d_float(X)
        self.mean_ = X.mean(axis=0)
        scale = X.std(axis=0)
        self.scale_ = np.where(scale <= self.eps, 1.0, scale)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        X = as_2d_float(X)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}.")
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "mean_"):
            raise RuntimeError("Standardizer must be fitted before transform.")


def train_validation_test_split(
    n_samples: int,
    *,
    seed: int,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return deterministic disjoint train, validation, and test indices."""

    if n_samples <= 2:
        raise ValueError("At least three samples are required.")
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1.")
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1.")
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("Train and validation fractions must leave a test split.")

    rng = np.random.default_rng(seed)
    indices = rng.permutation(n_samples)
    train_end = round(n_samples * train_fraction)
    validation_end = train_end + round(n_samples * validation_fraction)

    train = indices[:train_end]
    validation = indices[train_end:validation_end]
    test = indices[validation_end:]
    if len(train) == 0 or len(validation) == 0 or len(test) == 0:
        raise ValueError("Split fractions produced an empty partition.")
    return train, validation, test


def stratified_train_validation_test_split(
    labels: np.ndarray,
    *,
    seed: int,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return deterministic stratified train, validation, and test indices."""

    labels = np.asarray(labels)
    if labels.ndim != 1:
        raise ValueError("labels must be a 1D array.")
    if labels.size <= 2:
        raise ValueError("At least three samples are required.")
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1.")
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1.")
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("Train and validation fractions must leave a test split.")

    rng = np.random.default_rng(seed)
    train_parts: list[np.ndarray] = []
    validation_parts: list[np.ndarray] = []
    test_parts: list[np.ndarray] = []

    for label in np.unique(labels):
        class_indices = np.flatnonzero(labels == label)
        if class_indices.size < 3:
            raise ValueError("Each class must contain at least three samples.")

        shuffled = class_indices[rng.permutation(class_indices.size)]
        train_count = round(class_indices.size * train_fraction)
        validation_count = round(class_indices.size * validation_fraction)
        train_count = min(max(train_count, 1), class_indices.size - 2)
        validation_count = min(max(validation_count, 1), class_indices.size - train_count - 1)

        train_end = train_count
        validation_end = train_end + validation_count
        train_parts.append(shuffled[:train_end])
        validation_parts.append(shuffled[train_end:validation_end])
        test_parts.append(shuffled[validation_end:])

    train = np.concatenate(train_parts)
    validation = np.concatenate(validation_parts)
    test = np.concatenate(test_parts)
    return (
        train[rng.permutation(train.size)],
        validation[rng.permutation(validation.size)],
        test[rng.permutation(test.size)],
    )
