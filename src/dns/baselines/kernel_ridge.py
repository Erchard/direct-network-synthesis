"""Generic closed-form kernel ridge regression."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from dns.synthesis.linear_algebra import as_2d_float, as_target_matrix, stable_solve

KernelFn = Callable[[np.ndarray, np.ndarray | None], np.ndarray]


@dataclass
class KernelRidgeRegressor:
    """Kernel ridge regression solved in the dual."""

    kernel: KernelFn
    alpha: float = 1.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "KernelRidgeRegressor":
        X = as_2d_float(X)
        y_matrix, was_1d = as_target_matrix(y)
        if X.shape[0] != y_matrix.shape[0]:
            raise ValueError("X and y must contain the same number of samples.")

        gram = self.kernel(X, X)
        if gram.shape != (X.shape[0], X.shape[0]):
            raise ValueError("Kernel must return an n_train by n_train Gram matrix.")

        regularized = gram + self.alpha * np.eye(X.shape[0])
        self.dual_coef_ = stable_solve(regularized, y_matrix)
        self.X_fit_ = X
        self.target_was_1d_ = was_1d
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        X = as_2d_float(X)
        gram = self.kernel(X, self.X_fit_)
        predictions = gram @ self.dual_coef_
        return predictions.ravel() if self.target_was_1d_ else predictions

    @property
    def uses_iterative_parameter_optimization(self) -> bool:
        return False

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "dual_coef_"):
            raise RuntimeError("Model must be fitted before prediction.")
