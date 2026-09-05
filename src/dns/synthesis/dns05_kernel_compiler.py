"""DNS 0.5 initial kernel compiler prototype."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import numpy as np

from dns.kernels.common import linear_kernel
from dns.kernels.rbf import median_heuristic_gamma, rbf_kernel
from dns.synthesis.linear_algebra import as_2d_float

CompiledKernel = Callable[[np.ndarray, np.ndarray | None], np.ndarray]


@dataclass(frozen=True)
class KernelSpec:
    """A weighted kernel component for the DNS 0.5 compiler."""

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
