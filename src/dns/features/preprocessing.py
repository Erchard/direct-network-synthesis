"""Preprocessing helpers that fit only on training data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from dns.synthesis.linear_algebra import as_2d_float


@dataclass
class Standardizer:
    """Mean/scale standardization with train-only fitted statistics."""

    eps: float = 1e-12

    def fit(self, X: np.ndarray) -> "Standardizer":
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
    train_end = int(round(n_samples * train_fraction))
    validation_end = train_end + int(round(n_samples * validation_fraction))

    train = indices[:train_end]
    validation = indices[train_end:validation_end]
    test = indices[validation_end:]
    if len(train) == 0 or len(validation) == 0 or len(test) == 0:
        raise ValueError("Split fractions produced an empty partition.")
    return train, validation, test
