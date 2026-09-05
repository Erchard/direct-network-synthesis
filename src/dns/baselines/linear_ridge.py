"""Closed-form linear ridge regression baseline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from dns.synthesis.linear_algebra import as_2d_float, as_target_matrix, solve_primal_ridge


@dataclass
class LinearRidgeRegressor:
    """Linear ridge regression solved by one regularized linear system."""

    alpha: float = 1.0
    fit_intercept: bool = True

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRidgeRegressor":
        X = as_2d_float(X)
        y_matrix, was_1d = as_target_matrix(y)
        if X.shape[0] != y_matrix.shape[0]:
            raise ValueError("X and y must contain the same number of samples.")

        self.weights_ = solve_primal_ridge(
            X,
            y_matrix,
            alpha=self.alpha,
            fit_intercept=self.fit_intercept,
        )
        self.target_was_1d_ = was_1d
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        X = as_2d_float(X)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}.")

        if self.fit_intercept:
            X_design = np.column_stack([np.ones(X.shape[0]), X])
        else:
            X_design = X
        predictions = X_design @ self.weights_
        return predictions.ravel() if self.target_was_1d_ else predictions

    @property
    def uses_iterative_parameter_optimization(self) -> bool:
        return False

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "weights_"):
            raise RuntimeError("Model must be fitted before prediction.")
