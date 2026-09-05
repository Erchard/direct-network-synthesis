"""Run the starter DNS baseline comparison."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dns.baselines import (
    DeterministicReLUBaseline,
    KernelRidgeRegressor,
    LinearRidgeRegressor,
    RBFKernelRidgeRegressor,
)
from dns.features import train_validation_test_split
from dns.metrics import r2_score, root_mean_squared_error, summarize_metric_rows
from dns.synthesis import (
    DNS04Config,
    DNS04Synthesizer,
    DNS05KernelCompiler,
    KernelSpec,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default_experiment.json"


def make_synthetic_nonlinear_regression(
    *,
    seed: int,
    n_samples: int,
    n_features: int,
    noise: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a deterministic nonlinear regression problem."""

    if n_features < 4:
        raise ValueError("n_features must be at least 4 for the starter dataset.")

    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_samples, n_features))
    linear_weights = np.linspace(0.8, -0.4, n_features)
    linear_part = X @ linear_weights
    nonlinear_part = (
        np.sin(1.5 * X[:, 0])
        + 0.5 * np.maximum(X[:, 1] - X[:, 2], 0.0)
        + 0.25 * X[:, 3] ** 2
    )
    y = linear_part + nonlinear_part + rng.normal(scale=noise, size=n_samples)
    return X, y


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def evaluate_split(
    X: np.ndarray,
    y: np.ndarray,
    *,
    split_seed: int,
    config: dict[str, Any],
) -> list[dict[str, float | str | bool | int]]:
    split_config = config["splits"]
    model_config = config["models"]
    train_idx, validation_idx, test_idx = train_validation_test_split(
        len(y),
        seed=split_seed,
        train_fraction=float(split_config["train_fraction"]),
        validation_fraction=float(split_config["validation_fraction"]),
    )

    X_train, y_train = X[train_idx], y[train_idx]
    X_validation, y_validation = X[validation_idx], y[validation_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    dns05_compiler = DNS05KernelCompiler(
        [
            KernelSpec("linear", weight=0.35),
            KernelSpec("rbf", weight=0.65),
        ]
    )

    models = {
        "linear_ridge": LinearRidgeRegressor(alpha=float(model_config["ridge_alpha"])),
        "rbf_kernel_ridge": RBFKernelRidgeRegressor(alpha=float(model_config["kernel_alpha"])),
        "deterministic_relu": DeterministicReLUBaseline(
            hidden_units=int(model_config["relu_hidden_units"]),
            alpha=float(model_config["ridge_alpha"]),
            seed=int(model_config["relu_seed"]),
        ),
        "dns04_svd_relu": DNS04Synthesizer(
            DNS04Config(
                feature_count=int(model_config["dns04_feature_count"]),
                alpha=float(model_config["ridge_alpha"]),
            )
        ),
        "dns05_compiled_kernel": KernelRidgeRegressor(
            kernel=dns05_compiler.compile(X_reference=X_train),
            alpha=float(model_config["kernel_alpha"]),
        ),
    }

    rows: list[dict[str, float | str | bool | int]] = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        validation_pred = model.predict(X_validation)
        test_pred = model.predict(X_test)
        rows.append(
            {
                "model": name,
                "split_seed": split_seed,
                "validation_rmse": root_mean_squared_error(y_validation, validation_pred),
                "validation_r2": r2_score(y_validation, validation_pred),
                "test_rmse": root_mean_squared_error(y_test, test_pred),
                "test_r2": r2_score(y_test, test_pred),
                "uses_iterative_parameter_optimization": bool(
                    model.uses_iterative_parameter_optimization
                ),
            }
        )
    return rows


def run(config: dict[str, Any]) -> dict[str, Any]:
    dataset_config = config["dataset"]
    X, y = make_synthetic_nonlinear_regression(
        seed=int(dataset_config["data_seed"]),
        n_samples=int(dataset_config["n_samples"]),
        n_features=int(dataset_config["n_features"]),
        noise=float(dataset_config["noise"]),
    )

    rows: list[dict[str, float | str | bool | int]] = []
    for split_seed in config["splits"]["split_seeds"]:
        rows.extend(evaluate_split(X, y, split_seed=int(split_seed), config=config))

    return {
        "config": config,
        "rows": rows,
        "summary": summarize_metric_rows(rows),
    }


def print_summary(summary: dict[str, Any]) -> None:
    print("Model                     val_rmse          test_rmse         test_r2")
    print("------------------------  ----------------  ----------------  ----------------")
    for model, model_summary in summary.items():
        metrics = model_summary["metrics"]
        val_rmse = metrics["validation_rmse"]
        test_rmse = metrics["test_rmse"]
        test_r2 = metrics["test_r2"]
        print(
            f"{model:<24}  "
            f"{val_rmse['mean']:.4f} +/- {val_rmse['std']:.4f}  "
            f"{test_rmse['mean']:.4f} +/- {test_rmse['std']:.4f}  "
            f"{test_r2['mean']:.4f} +/- {test_r2['std']:.4f}"
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--write-results", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results" / "baseline_regression_summary.json",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    config = load_config(args.config)
    result = run(config)
    print_summary(result["summary"])

    if args.write_results:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
