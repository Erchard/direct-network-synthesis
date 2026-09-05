"""Deterministic ReLU feature baseline with a closed-form ridge readout."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from dns.features.preprocessing import Standardizer
from dns.features.relu import deterministic_relu_projection, relu
from dns.synthesis.linear_algebra import as_2d_float, as_target_matrix, solve_primal_ridge


@dataclass
class DeterministicReLUBaseline:
    """Fixed seeded ReLU features followed by a closed-form ridge solve."""

    hidden_units: int = 64
    alpha: float = 1.0
    seed: int = 0
    include_original: bool = True

    def fit(self, X: np.ndarray, y: np.ndarray) -> DeterministicReLUBaseline:
        X = as_2d_float(X)
        y_matrix, was_1d = as_target_matrix(y)
        if X.shape[0] != y_matrix.shape[0]:
            raise ValueError("X and y must contain the same number of samples.")

        self.standardizer_ = Standardizer().fit(X)
        self.feature_weights_, self.feature_bias_ = deterministic_relu_projection(
            n_features=X.shape[1],
            hidden_units=self.hidden_units,
            seed=self.seed,
        )
        features = self._features(X)
        self.readout_weights_ = solve_primal_ridge(features, y_matrix, alpha=self.alpha)
        self.target_was_1d_ = was_1d
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        X = as_2d_float(X)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}.")

        features = self._features(X)
        design = np.column_stack([np.ones(features.shape[0]), features])
        predictions = design @ self.readout_weights_
        return predictions.ravel() if self.target_was_1d_ else predictions

    @property
    def uses_iterative_parameter_optimization(self) -> bool:
        return False

    def _features(self, X: np.ndarray) -> np.ndarray:
        standardized = self.standardizer_.transform(X)
        hidden = relu(standardized @ self.feature_weights_ + self.feature_bias_)
        if self.include_original:
            return np.column_stack([standardized, hidden])
        return hidden

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "readout_weights_"):
            raise RuntimeError("Model must be fitted before prediction.")
