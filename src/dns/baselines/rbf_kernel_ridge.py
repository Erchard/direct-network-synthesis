"""RBF kernel ridge regression baseline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from dns.baselines.kernel_ridge import KernelRidgeRegressor
from dns.kernels.rbf import median_heuristic_gamma, rbf_kernel
from dns.synthesis.linear_algebra import as_2d_float


@dataclass
class RBFKernelRidgeRegressor:
    """Closed-form RBF kernel ridge regression.

    If gamma is not specified, it is computed from training data only by the median
    distance heuristic.
    """

    alpha: float = 1.0
    gamma: float | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> RBFKernelRidgeRegressor:
        X = as_2d_float(X)
        self.gamma_ = self.gamma if self.gamma is not None else median_heuristic_gamma(X)
        self.model_ = KernelRidgeRegressor(
            kernel=lambda A, B=None: rbf_kernel(A, B, gamma=self.gamma_),
            alpha=self.alpha,
        ).fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        return self.model_.predict(X)

    @property
    def uses_iterative_parameter_optimization(self) -> bool:
        return False

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "model_"):
            raise RuntimeError("Model must be fitted before prediction.")
