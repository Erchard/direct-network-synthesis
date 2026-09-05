"""DNS 0.4 initial direct feature synthesis prototype."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from dns.features.preprocessing import Standardizer
from dns.features.relu import relu
from dns.synthesis.linear_algebra import as_2d_float, as_target_matrix, solve_primal_ridge


@dataclass(frozen=True)
class DNS04Config:
    """Configuration for the DNS 0.4 prototype."""

    feature_count: int = 8
    alpha: float = 1.0
    include_original: bool = True


class DNS04Synthesizer:
    """SVD-based direct ReLU feature synthesis plus a closed-form readout.

    This is a deliberately modest starting point. It uses training-data geometry to build a
    fixed projection and then solves the readout by ridge regression. It does not update
    parameters with gradient descent.
    """

    def __init__(self, config: DNS04Config | None = None):
        self.config = config or DNS04Config()

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DNS04Synthesizer":
        X = as_2d_float(X)
        y_matrix, was_1d = as_target_matrix(y)
        if X.shape[0] != y_matrix.shape[0]:
            raise ValueError("X and y must contain the same number of samples.")
        if self.config.feature_count <= 0:
            raise ValueError("feature_count must be positive.")

        self.standardizer_ = Standardizer().fit(X)
        standardized = self.standardizer_.transform(X)
        _, _, vt = np.linalg.svd(standardized, full_matrices=False)
        count = min(self.config.feature_count, vt.shape[0])
        projection = vt[:count].T

        # Make SVD sign choices stable across equivalent decompositions.
        for column_index in range(projection.shape[1]):
            column = projection[:, column_index]
            pivot = int(np.argmax(np.abs(column)))
            if column[pivot] < 0.0:
                projection[:, column_index] *= -1.0

        self.projection_ = projection
        self.bias_ = np.zeros(count)
        features = self._features_from_standardized(standardized)
        self.readout_weights_ = solve_primal_ridge(features, y_matrix, alpha=self.config.alpha)
        self.target_was_1d_ = was_1d
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        X = as_2d_float(X)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}.")
        standardized = self.standardizer_.transform(X)
        features = self._features_from_standardized(standardized)
        design = np.column_stack([np.ones(features.shape[0]), features])
        predictions = design @ self.readout_weights_
        return predictions.ravel() if self.target_was_1d_ else predictions

    @property
    def synthesis_rule(self) -> str:
        return "train_only_standardization + svd_projection + closed_form_ridge_readout"

    @property
    def uses_iterative_parameter_optimization(self) -> bool:
        return False

    def _features_from_standardized(self, standardized: np.ndarray) -> np.ndarray:
        hidden = relu(standardized @ self.projection_ + self.bias_)
        if self.config.include_original:
            return np.column_stack([standardized, hidden])
        return hidden

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "readout_weights_"):
            raise RuntimeError("Model must be fitted before prediction.")
