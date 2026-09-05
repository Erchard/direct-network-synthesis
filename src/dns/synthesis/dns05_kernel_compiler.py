"""DNS 0.5 kernel compiler prototypes."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import numpy as np

from dns.features.preprocessing import Standardizer
from dns.features.relu import relu
from dns.kernels.common import linear_kernel
from dns.kernels.rbf import median_heuristic_gamma, rbf_kernel
from dns.synthesis.linear_algebra import as_2d_float, solve_primal_ridge

CompiledKernel = Callable[[np.ndarray, np.ndarray | None], np.ndarray]


@dataclass(frozen=True)
class KernelSpec:
    """A weighted kernel component for the original DNS 0.5 combiner prototype."""

    name: str
    weight: float = 1.0
    params: dict[str, float] = field(default_factory=dict)


class DNS05KernelCompiler:
    """Compile a deterministic weighted kernel from declarative kernel specs."""

    def __init__(self, specs: Sequence[KernelSpec]):
        if not specs:
            raise ValueError("At least one kernel spec is required.")
        self.specs = tuple(specs)

    def compile(self, X_reference: np.ndarray | None = None) -> CompiledKernel:
        """Return a kernel callable with train-only defaults resolved."""

        resolved_specs = self._resolve_specs(X_reference)

        def kernel(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
            X_checked = as_2d_float(X)
            Y_checked = None if Y is None else as_2d_float(Y)
            total: np.ndarray | None = None
            for spec in resolved_specs:
                component = self._evaluate_component(spec, X_checked, Y_checked)
                weighted = spec.weight * component
                total = weighted if total is None else total + weighted
            if total is None:
                raise RuntimeError("No kernel components were evaluated.")
            return total

        return kernel

    def kernel_matrix(
        self,
        X: np.ndarray,
        Y: np.ndarray | None = None,
        *,
        X_reference: np.ndarray | None = None,
    ) -> np.ndarray:
        """Compile and immediately evaluate a kernel matrix."""

        return self.compile(X_reference=X_reference)(X, Y)

    def _resolve_specs(self, X_reference: np.ndarray | None) -> tuple[KernelSpec, ...]:
        resolved = []
        for spec in self.specs:
            name = spec.name.lower()
            params = dict(spec.params)
            if name == "rbf" and "gamma" not in params:
                if X_reference is None:
                    raise ValueError("RBF specs without gamma require X_reference.")
                params["gamma"] = median_heuristic_gamma(X_reference)
            if name not in {"linear", "rbf"}:
                raise ValueError(f"Unsupported kernel component: {spec.name!r}.")
            resolved.append(KernelSpec(name=name, weight=float(spec.weight), params=params))
        return tuple(resolved)

    @staticmethod
    def _evaluate_component(
        spec: KernelSpec,
        X: np.ndarray,
        Y: np.ndarray | None,
    ) -> np.ndarray:
        if spec.name == "linear":
            return linear_kernel(X, Y)
        if spec.name == "rbf":
            return rbf_kernel(X, Y, gamma=float(spec.params["gamma"]))
        raise ValueError(f"Unsupported kernel component: {spec.name!r}.")


@dataclass(frozen=True)
class DNS05FeatureCompilerConfig:
    """Configuration for residual closed-form RBF geometry compilation."""

    total_feature_count: int = 192
    block_count: int = 3
    projection_alpha: float = 1e-6
    readout_alpha: float = 1.0
    quantile_min: float = 0.1
    quantile_max: float = 0.9
    quantile_count: int = 5
    eigensolver_eps: float = 1e-10

    def __post_init__(self) -> None:
        if self.total_feature_count <= 0:
            raise ValueError("total_feature_count must be positive.")
        if self.block_count <= 0:
            raise ValueError("block_count must be positive.")
        if self.block_count > self.total_feature_count:
            raise ValueError("block_count cannot exceed total_feature_count.")
        if self.projection_alpha < 0.0:
            raise ValueError("projection_alpha must be non-negative.")
        if self.readout_alpha < 0.0:
            raise ValueError("readout_alpha must be non-negative.")
        if not 0.0 < self.quantile_min < self.quantile_max < 1.0:
            raise ValueError("Quantile bounds must satisfy 0 < min < max < 1.")
        if self.quantile_count <= 0:
            raise ValueError("quantile_count must be positive.")
        if self.eigensolver_eps <= 0.0:
            raise ValueError("eigensolver_eps must be positive.")


@dataclass(frozen=True)
class DNS05BlockDiagnostics:
    """Measured contribution of one compiled residual block."""

    block_index: int
    feature_count: int
    target_rank: int
    positive_residual_rank: int
    realized_rank: int
    cumulative_rank: int
    spectral_energy_captured: float
    reconstruction_error: float


@dataclass(frozen=True)
class _CompiledResidualBlock:
    feature_indices: np.ndarray
    projection_weights: np.ndarray


class DNS05CompiledFeatureClassifier:
    """Compile an RBF kernel geometry into deterministic residual feature blocks.

    The model first constructs a train-only RBF oracle geometry, then repeatedly projects the
    positive spectral component of the remaining residual kernel into deterministic
    PCA/quantile ReLU features. The final class readout is a single closed-form ridge solve.
    """

    def __init__(
        self,
        *,
        gamma: float | None = None,
        config: DNS05FeatureCompilerConfig | None = None,
    ):
        if gamma is not None and gamma <= 0.0:
            raise ValueError("gamma must be positive.")
        self.gamma = gamma
        self.config = config or DNS05FeatureCompilerConfig()

    def fit(self, X: np.ndarray, y: np.ndarray) -> DNS05CompiledFeatureClassifier:
        X = as_2d_float(X)
        labels = np.asarray(y)
        if labels.ndim != 1:
            raise ValueError("DNS05CompiledFeatureClassifier expects 1D class labels.")
        if X.shape[0] != labels.shape[0]:
            raise ValueError("X and y must contain the same number of samples.")

        self.classes_ = np.unique(labels)
        if self.classes_.size < 2:
            raise ValueError("At least two classes are required.")

        self.feature_map_ = _PCAQuantileReLUFeatureMap(
            feature_count=self.config.total_feature_count,
            quantile_min=self.config.quantile_min,
            quantile_max=self.config.quantile_max,
            quantile_count=self.config.quantile_count,
        ).fit(X)
        X_standardized = self.feature_map_.transform_standardized(X)
        self.gamma_ = self.gamma if self.gamma is not None else median_heuristic_gamma(
            X_standardized
        )
        oracle_kernel = rbf_kernel(X_standardized, gamma=self.gamma_)
        oracle_norm = max(
            float(np.linalg.norm(oracle_kernel, ord="fro")),
            self.config.eigensolver_eps,
        )

        block_partitions = _interleaved_feature_partitions(
            total_feature_count=self.config.total_feature_count,
            block_count=self.config.block_count,
        )
        residual = oracle_kernel.copy()
        cumulative_kernel = np.zeros_like(oracle_kernel)
        cumulative_embedding = np.empty((X.shape[0], 0), dtype=float)
        train_embeddings: list[np.ndarray] = []
        blocks: list[_CompiledResidualBlock] = []
        diagnostics: list[DNS05BlockDiagnostics] = []

        for block_index, feature_indices in enumerate(block_partitions):
            target, eigenvalues, positive_rank, spectral_energy = _positive_spectral_embedding(
                residual,
                rank=feature_indices.size,
                eps=self.config.eigensolver_eps,
            )
            phi_train = self.feature_map_.transform_columns(X, feature_indices)
            projection_weights = solve_primal_ridge(
                phi_train,
                target,
                alpha=self.config.projection_alpha,
                fit_intercept=False,
            )
            block_embedding = phi_train @ projection_weights
            train_embeddings.append(block_embedding)
            blocks.append(
                _CompiledResidualBlock(
                    feature_indices=feature_indices,
                    projection_weights=projection_weights,
                )
            )

            cumulative_kernel = cumulative_kernel + block_embedding @ block_embedding.T
            residual = _symmetrize(oracle_kernel - cumulative_kernel)
            cumulative_embedding = np.column_stack([cumulative_embedding, block_embedding])
            diagnostics.append(
                DNS05BlockDiagnostics(
                    block_index=block_index,
                    feature_count=int(feature_indices.size),
                    target_rank=int(eigenvalues.size),
                    positive_residual_rank=int(positive_rank),
                    realized_rank=int(np.linalg.matrix_rank(block_embedding)),
                    cumulative_rank=int(np.linalg.matrix_rank(cumulative_embedding)),
                    spectral_energy_captured=float(spectral_energy),
                    reconstruction_error=float(np.linalg.norm(residual, ord="fro") / oracle_norm),
                )
            )

        train_embedding = np.column_stack(train_embeddings)
        targets = _one_hot(labels, self.classes_)
        self.readout_weights_ = solve_primal_ridge(
            train_embedding,
            targets,
            alpha=self.config.readout_alpha,
            fit_intercept=True,
        )
        self.blocks_ = tuple(blocks)
        self.block_diagnostics_ = tuple(diagnostics)
        self.train_embedding_ = train_embedding
        self.kernel_reconstruction_error_ = diagnostics[-1].reconstruction_error
        self.compiled_rank_ = int(np.linalg.matrix_rank(train_embedding))
        self.feature_budget_ = self.config.total_feature_count
        self.block_feature_counts_ = tuple(int(indices.size) for indices in block_partitions)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Return compiled residual features for new samples."""

        self._check_is_fitted()
        X = as_2d_float(X)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}.")

        embeddings = [
            self.feature_map_.transform_columns(X, block.feature_indices) @ block.projection_weights
            for block in self.blocks_
        ]
        return np.column_stack(embeddings)

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Return closed-form class scores."""

        embedding = self.transform(X)
        design = np.column_stack([np.ones(embedding.shape[0]), embedding])
        return design @ self.readout_weights_

    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.decision_function(X)
        return self.classes_[np.argmax(scores, axis=1)]

    @property
    def synthesis_rule(self) -> str:
        return "train_only_rbf_oracle + residual_spectral_targets + closed_form_ridge_blocks"

    @property
    def uses_iterative_parameter_optimization(self) -> bool:
        return False

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "readout_weights_"):
            raise RuntimeError("Model must be fitted before prediction.")


class _PCAQuantileReLUFeatureMap:
    """Train-only PCA directions with deterministic quantile ReLU knots."""

    def __init__(
        self,
        *,
        feature_count: int,
        quantile_min: float,
        quantile_max: float,
        quantile_count: int,
    ):
        self.feature_count = feature_count
        self.quantile_min = quantile_min
        self.quantile_max = quantile_max
        self.quantile_count = quantile_count

    def fit(self, X: np.ndarray) -> _PCAQuantileReLUFeatureMap:
        X = as_2d_float(X)
        self.standardizer_ = Standardizer().fit(X)
        standardized = self.standardizer_.transform(X)
        _, _, vt = np.linalg.svd(standardized, full_matrices=False)
        components = vt.copy()

        for row_index in range(components.shape[0]):
            row = components[row_index]
            pivot = int(np.argmax(np.abs(row)))
            if row[pivot] < 0.0:
                components[row_index] *= -1.0

        n_components = components.shape[0]
        quantiles = np.linspace(self.quantile_min, self.quantile_max, self.quantile_count)
        weights = np.empty((X.shape[1], self.feature_count), dtype=float)
        thresholds = np.empty(self.feature_count, dtype=float)

        for feature_index in range(self.feature_count):
            signed_direction_index = feature_index % (2 * n_components)
            component_index = signed_direction_index // 2
            sign = 1.0 if signed_direction_index % 2 == 0 else -1.0
            quantile_index = (feature_index // (2 * n_components)) % quantiles.size
            direction = sign * components[component_index]
            projected = standardized @ direction
            weights[:, feature_index] = direction
            thresholds[feature_index] = float(np.quantile(projected, quantiles[quantile_index]))

        self.weights_ = weights
        self.thresholds_ = thresholds
        self.n_features_in_ = X.shape[1]
        return self

    def transform_standardized(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        return self.standardizer_.transform(X)

    def transform_columns(self, X: np.ndarray, feature_indices: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        X = as_2d_float(X)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}.")
        standardized = self.standardizer_.transform(X)
        weights = self.weights_[:, feature_indices]
        thresholds = self.thresholds_[feature_indices]
        return relu(standardized @ weights - thresholds)

    def _check_is_fitted(self) -> None:
        if not hasattr(self, "weights_"):
            raise RuntimeError("Feature map must be fitted before transform.")


def _positive_spectral_embedding(
    matrix: np.ndarray,
    *,
    rank: int,
    eps: float,
) -> tuple[np.ndarray, np.ndarray, int, float]:
    symmetric = _symmetrize(matrix)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    threshold = eps * max(1.0, float(np.max(np.abs(eigenvalues))))
    positive_mask = eigenvalues > threshold
    positive_values = eigenvalues[positive_mask]
    positive_vectors = eigenvectors[:, positive_mask]
    selected_values = positive_values[:rank]
    selected_vectors = positive_vectors[:, :rank]

    if selected_values.size == 0:
        return np.zeros((matrix.shape[0], 0), dtype=float), selected_values, 0, 0.0

    embedding = selected_vectors * np.sqrt(selected_values)[None, :]
    positive_energy = float(np.sum(positive_values**2))
    selected_energy = float(np.sum(selected_values**2))
    spectral_energy = selected_energy / positive_energy if positive_energy > 0.0 else 0.0
    return embedding, selected_values, int(positive_values.size), spectral_energy


def _interleaved_feature_partitions(
    *,
    total_feature_count: int,
    block_count: int,
) -> tuple[np.ndarray, ...]:
    return tuple(
        np.arange(block_index, total_feature_count, block_count, dtype=int)
        for block_index in range(block_count)
    )


def _symmetrize(matrix: np.ndarray) -> np.ndarray:
    return 0.5 * (matrix + matrix.T)


def _one_hot(labels: np.ndarray, classes: np.ndarray) -> np.ndarray:
    class_to_index = {label: index for index, label in enumerate(classes)}
    encoded = np.zeros((labels.shape[0], classes.shape[0]), dtype=float)
    for row_index, label in enumerate(labels):
        encoded[row_index, class_to_index[label]] = 1.0
    return encoded
