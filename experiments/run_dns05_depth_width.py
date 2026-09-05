"""Run the DNS 0.5 depth-versus-width digits experiment."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dns.features import (
    Standardizer,
    deterministic_relu_projection,
    relu,
    stratified_train_validation_test_split,
)
from dns.kernels import median_heuristic_gamma, rbf_kernel
from dns.metrics import accuracy_score, summarize_metric_rows
from dns.synthesis import (
    DNS05CompiledFeatureClassifier,
    DNS05FeatureCompilerConfig,
)
from dns.synthesis.linear_algebra import solve_primal_ridge, stable_solve

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "dns05_depth_width_digits.json"


@dataclass(frozen=True)
class OracleSelection:
    split_seed: int
    base_gamma: float
    gamma_multiplier: float
    gamma: float
    alpha: float
    validation_accuracy: float
    selection_time_seconds: float


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_digits_dataset() -> tuple[np.ndarray, np.ndarray]:
    try:
        from sklearn.datasets import load_digits
    except ImportError as exc:
        raise RuntimeError(
            "The DNS 0.5 digits experiment requires scikit-learn. "
            "Install the project with `python -m pip install -e .`."
        ) from exc

    digits = load_digits()
    return np.asarray(digits.data, dtype=float), np.asarray(digits.target)


def run(config: dict[str, Any], *, max_splits: int | None = None) -> dict[str, Any]:
    if config["dataset"]["name"] != "sklearn_digits":
        raise ValueError("This experiment runner currently supports only sklearn_digits.")

    X, y = load_digits_dataset()
    split_seeds = [int(seed) for seed in config["splits"]["split_seeds"]]
    if max_splits is not None:
        split_seeds = split_seeds[:max_splits]

    rows: list[dict[str, float | str | bool | int]] = []
    oracle_selections: list[dict[str, float | int]] = []
    block_diagnostics: list[dict[str, float | str | int]] = []
    for split_seed in split_seeds:
        split_rows, split_selection, split_blocks = evaluate_split(
            X,
            y,
            split_seed=split_seed,
            config=config,
        )
        rows.extend(split_rows)
        oracle_selections.append(asdict(split_selection))
        block_diagnostics.extend(split_blocks)

    return {
        "config": config,
        "commit_sha": get_commit_sha(),
        "git_status_short": get_git_status_short(),
        "rows": rows,
        "summary": summarize_metric_rows(rows),
        "paired_differences": paired_differences(rows),
        "oracle_selections": oracle_selections,
        "block_diagnostics": block_diagnostics,
    }


def evaluate_split(
    X: np.ndarray,
    y: np.ndarray,
    *,
    split_seed: int,
    config: dict[str, Any],
) -> tuple[
    list[dict[str, float | str | bool | int]],
    OracleSelection,
    list[dict[str, float | str | int]],
]:
    split_config = config["splits"]
    model_config = config["models"]
    train_idx, validation_idx, test_idx = stratified_train_validation_test_split(
        y,
        seed=split_seed,
        train_fraction=float(split_config["train_fraction"]),
        validation_fraction=float(split_config["validation_fraction"]),
    )

    X_train, y_train = X[train_idx], y[train_idx]
    X_validation, y_validation = X[validation_idx], y[validation_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    standardizer = Standardizer().fit(X_train)
    X_train_std = standardizer.transform(X_train)
    X_validation_std = standardizer.transform(X_validation)
    X_test_std = standardizer.transform(X_test)
    classes = np.unique(y_train)
    y_train_one_hot = one_hot(y_train, classes)

    selection = select_rbf_oracle(
        X_train_std,
        y_train_one_hot,
        X_validation_std,
        y_validation,
        classes,
        split_seed=split_seed,
        config=config,
    )

    rows = [
        evaluate_linear_classifier(
            X_train_std,
            y_train_one_hot,
            X_validation_std,
            y_validation,
            X_test_std,
            y_test,
            classes,
            alpha=float(model_config["linear_alpha"]),
            split_seed=split_seed,
        ),
        evaluate_rbf_oracle(
            X_train_std,
            y_train_one_hot,
            X_validation_std,
            y_validation,
            X_test_std,
            y_test,
            classes,
            gamma=selection.gamma,
            alpha=selection.alpha,
            selection_time_seconds=selection.selection_time_seconds,
            split_seed=split_seed,
        ),
        evaluate_deterministic_relu_classifier(
            X_train_std,
            y_train_one_hot,
            X_validation_std,
            y_validation,
            X_test_std,
            y_test,
            classes,
            hidden_units=int(model_config["relu_hidden_units"]),
            seed=int(model_config["relu_seed"]),
            include_original=bool(model_config["relu_include_original"]),
            alpha=float(model_config["linear_alpha"]),
            split_seed=split_seed,
        ),
    ]

    compiled_rows: list[dict[str, float | str | bool | int]] = []
    block_diagnostics: list[dict[str, float | str | int]] = []
    compiled_block_counts = [1] + [int(count) for count in model_config["compiled_block_counts"]]
    for block_count in compiled_block_counts:
        row, diagnostics = evaluate_compiled_classifier(
            X_train,
            y_train,
            X_validation,
            y_validation,
            X_test,
            y_test,
            gamma=selection.gamma,
            block_count=block_count,
            config=config,
            split_seed=split_seed,
        )
        compiled_rows.append(row)
        block_diagnostics.extend(diagnostics)

    if model_config.get("full_basis_diagnostic", False):
        for block_count in compiled_block_counts[1:]:
            row, diagnostics = evaluate_compiled_classifier(
                X_train, y_train, X_validation, y_validation, X_test, y_test,
                gamma=selection.gamma, block_count=block_count, config=config,
                split_seed=split_seed, full_basis=True,
            )
            compiled_rows.append(row)
            block_diagnostics.extend(diagnostics)
        rows.append(evaluate_spectral_reference(
            X_train_std, y_train_one_hot, X_validation_std, y_validation,
            X_test_std, y_test, classes, gamma=selection.gamma,
            rank=int(model_config["compiled_total_feature_count"]),
            alpha=float(model_config["compiled_readout_alpha"]), split_seed=split_seed,
        ))

    return rows + compiled_rows, selection, block_diagnostics


def select_rbf_oracle(
    X_train: np.ndarray,
    y_train_one_hot: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    classes: np.ndarray,
    *,
    split_seed: int,
    config: dict[str, Any],
) -> OracleSelection:
    selection_config = config["oracle_selection"]
    base_gamma = median_heuristic_gamma(X_train)
    gamma_multipliers = [float(value) for value in selection_config["gamma_multipliers"]]
    alpha_values = [float(value) for value in selection_config["alpha_values"]]
    start = time.perf_counter()
    best: OracleSelection | None = None

    for gamma_multiplier in gamma_multipliers:
        gamma = base_gamma * gamma_multiplier
        train_kernel = rbf_kernel(X_train, gamma=gamma)
        validation_kernel = rbf_kernel(X_validation, X_train, gamma=gamma)
        eye = np.eye(train_kernel.shape[0])
        for alpha in alpha_values:
            dual = stable_solve(train_kernel + alpha * eye, y_train_one_hot)
            validation_pred = classes[np.argmax(validation_kernel @ dual, axis=1)]
            validation_accuracy = accuracy_score(y_validation, validation_pred)
            candidate = OracleSelection(
                split_seed=split_seed,
                base_gamma=base_gamma,
                gamma_multiplier=gamma_multiplier,
                gamma=gamma,
                alpha=alpha,
                validation_accuracy=validation_accuracy,
                selection_time_seconds=time.perf_counter() - start,
            )
            if best is None or candidate.validation_accuracy > best.validation_accuracy:
                best = candidate

    if best is None:
        raise RuntimeError("RBF oracle selection did not evaluate any candidates.")
    return OracleSelection(
        split_seed=best.split_seed,
        base_gamma=best.base_gamma,
        gamma_multiplier=best.gamma_multiplier,
        gamma=best.gamma,
        alpha=best.alpha,
        validation_accuracy=best.validation_accuracy,
        selection_time_seconds=time.perf_counter() - start,
    )


def evaluate_linear_classifier(
    X_train: np.ndarray,
    y_train_one_hot: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    classes: np.ndarray,
    *,
    alpha: float,
    split_seed: int,
) -> dict[str, float | str | bool | int]:
    start = time.perf_counter()
    weights = solve_primal_ridge(X_train, y_train_one_hot, alpha=alpha, fit_intercept=True)
    solve_time = time.perf_counter() - start
    validation_pred = predict_primal(X_validation, weights, classes)
    start = time.perf_counter()
    test_pred = predict_primal(X_test, weights, classes)
    inference_time = time.perf_counter() - start
    return classification_row(
        model="linear_ridge_classifier",
        split_seed=split_seed,
        y_validation=y_validation,
        validation_pred=validation_pred,
        y_test=y_test,
        test_pred=test_pred,
        solve_time_seconds=solve_time,
        inference_time_seconds=inference_time,
        feature_budget=X_train.shape[1],
        compiled_rank=int(np.linalg.matrix_rank(X_train)),
    )


def evaluate_rbf_oracle(
    X_train: np.ndarray,
    y_train_one_hot: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    classes: np.ndarray,
    *,
    gamma: float,
    alpha: float,
    selection_time_seconds: float,
    split_seed: int,
) -> dict[str, float | str | bool | int]:
    start = time.perf_counter()
    train_kernel = rbf_kernel(X_train, gamma=gamma)
    dual = stable_solve(train_kernel + alpha * np.eye(X_train.shape[0]), y_train_one_hot)
    solve_time = time.perf_counter() - start
    validation_scores = rbf_kernel(X_validation, X_train, gamma=gamma) @ dual
    validation_pred = classes[np.argmax(validation_scores, axis=1)]
    start = time.perf_counter()
    test_pred = classes[np.argmax(rbf_kernel(X_test, X_train, gamma=gamma) @ dual, axis=1)]
    inference_time = time.perf_counter() - start
    row = classification_row(
        model="rbf_kernel_ridge_oracle",
        split_seed=split_seed,
        y_validation=y_validation,
        validation_pred=validation_pred,
        y_test=y_test,
        test_pred=test_pred,
        solve_time_seconds=solve_time,
        inference_time_seconds=inference_time,
        feature_budget=X_train.shape[0],
        compiled_rank=int(np.linalg.matrix_rank(train_kernel)),
        kernel_reconstruction_error=0.0,
    )
    row["selected_gamma"] = float(gamma)
    row["selected_alpha"] = float(alpha)
    row["selection_time_seconds"] = float(selection_time_seconds)
    return row


def evaluate_deterministic_relu_classifier(
    X_train: np.ndarray,
    y_train_one_hot: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    classes: np.ndarray,
    *,
    hidden_units: int,
    seed: int,
    include_original: bool,
    alpha: float,
    split_seed: int,
) -> dict[str, float | str | bool | int]:
    start = time.perf_counter()
    feature_weights, feature_bias = deterministic_relu_projection(
        n_features=X_train.shape[1],
        hidden_units=hidden_units,
        seed=seed,
    )
    train_features = relu_features(X_train, feature_weights, feature_bias, include_original)
    weights = solve_primal_ridge(train_features, y_train_one_hot, alpha=alpha, fit_intercept=True)
    solve_time = time.perf_counter() - start
    validation_features = relu_features(
        X_validation,
        feature_weights,
        feature_bias,
        include_original,
    )
    validation_pred = predict_primal(validation_features, weights, classes)
    start = time.perf_counter()
    test_features = relu_features(X_test, feature_weights, feature_bias, include_original)
    test_pred = predict_primal(test_features, weights, classes)
    inference_time = time.perf_counter() - start
    return classification_row(
        model="deterministic_relu_classifier",
        split_seed=split_seed,
        y_validation=y_validation,
        validation_pred=validation_pred,
        y_test=y_test,
        test_pred=test_pred,
        solve_time_seconds=solve_time,
        inference_time_seconds=inference_time,
        feature_budget=train_features.shape[1],
        compiled_rank=int(np.linalg.matrix_rank(train_features)),
    )


def evaluate_compiled_classifier(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    *,
    gamma: float,
    block_count: int,
    config: dict[str, Any],
    split_seed: int,
    full_basis: bool = False,
) -> tuple[dict[str, float | str | bool | int], list[dict[str, float | str | int]]]:
    model_config = config["models"]
    total_feature_count = int(model_config["compiled_total_feature_count"])
    compiler_config = DNS05FeatureCompilerConfig(
        total_feature_count=total_feature_count,
        block_count=block_count,
        projection_alpha=float(model_config["compiled_projection_alpha"]),
        readout_alpha=float(model_config["compiled_readout_alpha"]),
        quantile_min=float(model_config["compiled_quantile_min"]),
        quantile_max=float(model_config["compiled_quantile_max"]),
        quantile_count=int(model_config["compiled_quantile_count"]),
        full_basis=full_basis,
    )
    name = compiled_model_name(total_feature_count, block_count)
    if full_basis:
        name += "_full_basis"
    model = DNS05CompiledFeatureClassifier(gamma=gamma, config=compiler_config)
    start = time.perf_counter()
    model.fit(X_train, y_train)
    solve_time = time.perf_counter() - start
    validation_pred = model.predict(X_validation)
    start = time.perf_counter()
    test_pred = model.predict(X_test)
    inference_time = time.perf_counter() - start
    block_errors = [diagnostic.reconstruction_error for diagnostic in model.block_diagnostics_]
    block_energy = [
        diagnostic.spectral_energy_captured for diagnostic in model.block_diagnostics_
    ]
    row = classification_row(
        model=name,
        split_seed=split_seed,
        y_validation=y_validation,
        validation_pred=validation_pred,
        y_test=y_test,
        test_pred=test_pred,
        solve_time_seconds=solve_time,
        inference_time_seconds=inference_time,
        feature_budget=model.feature_budget_,
        compiled_rank=model.compiled_rank_,
        block_count=block_count,
        kernel_reconstruction_error=model.kernel_reconstruction_error_,
        mean_block_spectral_energy=float(np.mean(block_energy)),
        first_block_reconstruction_error=float(block_errors[0]),
    )
    diagnostics = [
        {
            "model": name,
            "split_seed": split_seed,
            **asdict(diagnostic),
        }
        for diagnostic in model.block_diagnostics_
    ]
    row["basis_feature_count"] = total_feature_count
    row["block_basis_evaluations"] = total_feature_count * (block_count if full_basis else 1)
    row["embedding_dimension"] = model.train_embedding_.shape[1]
    row["projection_parameter_count"] = sum(b.projection_weights.size for b in model.blocks_)
    return row, diagnostics


def evaluate_spectral_reference(
    X_train, targets, X_validation, y_validation, X_test, y_test, classes,
    *, gamma, rank, alpha, split_seed,
):
    """Train-only truncated kernel embedding with out-of-sample extension.

    This is an optimal train Gram approximation, not an accuracy upper bound.
    Inference retains all training examples and is not a compact neural model.
    """
    start = time.perf_counter()
    kernel = rbf_kernel(X_train, gamma=gamma)
    values, vectors = np.linalg.eigh(kernel)
    indices = np.argsort(values)[::-1][:rank]
    indices = indices[values[indices] > 1e-10 * max(1.0, values.max())]
    embedding = vectors[:, indices] * np.sqrt(values[indices])
    extension = vectors[:, indices] / np.sqrt(values[indices])
    weights = solve_primal_ridge(embedding, targets, alpha=alpha, fit_intercept=True)
    solve_time = time.perf_counter() - start
    val = predict_primal(rbf_kernel(X_validation, X_train, gamma=gamma) @ extension,
                         weights, classes)
    start = time.perf_counter()
    test = predict_primal(rbf_kernel(X_test, X_train, gamma=gamma) @ extension,
                          weights, classes)
    inference_time = time.perf_counter() - start
    return classification_row(
        model=f"spectral_oracle_{rank}", split_seed=split_seed,
        y_validation=y_validation, validation_pred=val, y_test=y_test, test_pred=test,
        solve_time_seconds=solve_time, inference_time_seconds=inference_time,
        feature_budget=rank, compiled_rank=len(indices),
        kernel_reconstruction_error=float(
            np.linalg.norm(kernel - embedding @ embedding.T) / np.linalg.norm(kernel)
        ),
    )


def relu_features(
    X: np.ndarray,
    feature_weights: np.ndarray,
    feature_bias: np.ndarray,
    include_original: bool,
) -> np.ndarray:
    hidden = relu(X @ feature_weights + feature_bias)
    if include_original:
        return np.column_stack([X, hidden])
    return hidden


def predict_primal(X: np.ndarray, weights: np.ndarray, classes: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(X.shape[0]), X])
    scores = design @ weights
    return classes[np.argmax(scores, axis=1)]


def classification_row(
    *,
    model: str,
    split_seed: int,
    y_validation: np.ndarray,
    validation_pred: np.ndarray,
    y_test: np.ndarray,
    test_pred: np.ndarray,
    solve_time_seconds: float,
    inference_time_seconds: float,
    feature_budget: int,
    compiled_rank: int,
    block_count: int = 0,
    kernel_reconstruction_error: float | None = None,
    mean_block_spectral_energy: float | None = None,
    first_block_reconstruction_error: float | None = None,
) -> dict[str, float | str | bool | int]:
    row: dict[str, float | str | bool | int] = {
        "model": model,
        "split_seed": split_seed,
        "validation_accuracy": accuracy_score(y_validation, validation_pred),
        "test_accuracy": accuracy_score(y_test, test_pred),
        "solve_time_seconds": float(solve_time_seconds),
        "inference_time_seconds": float(inference_time_seconds),
        "feature_budget": int(feature_budget),
        "compiled_rank": int(compiled_rank),
        "block_count": int(block_count),
        "uses_iterative_parameter_optimization": False,
    }
    classes = np.unique(np.concatenate([y_validation, y_test, validation_pred, test_pred]))
    for partition, truth, prediction in (
        ("validation", y_validation, validation_pred), ("test", y_test, test_pred)
    ):
        observed = one_hot(truth, classes)
        predicted = one_hot(prediction, classes)
        residual_sum = float(np.sum((observed - predicted) ** 2))
        total_sum = float(np.sum((observed - observed.mean(axis=0)) ** 2))
        row[f"{partition}_rmse"] = float(np.sqrt(np.mean((observed - predicted) ** 2)))
        row[f"{partition}_r2"] = 1.0 - residual_sum / total_sum if total_sum else 0.0
    if kernel_reconstruction_error is not None:
        row["kernel_reconstruction_error"] = float(kernel_reconstruction_error)
    if mean_block_spectral_energy is not None:
        row["mean_block_spectral_energy"] = float(mean_block_spectral_energy)
    if first_block_reconstruction_error is not None:
        row["first_block_reconstruction_error"] = float(first_block_reconstruction_error)
    return row


def paired_differences(rows: list[dict[str, float | str | bool | int]]) -> dict[str, Any]:
    models = {str(row["model"]) for row in rows}
    one_shot_models = sorted(model for model in models if model.startswith("dns05_one_shot_"))
    residual_models = sorted(model for model in models if model.startswith("dns05_residual_"))
    comparisons: list[tuple[str, str]] = []
    comparisons.extend((model, one_shot_models[0]) for model in residual_models if one_shot_models)
    comparisons.extend(
        (model, "rbf_kernel_ridge_oracle") for model in one_shot_models + residual_models
    )
    comparisons.extend(
        (model, reference) for reference in sorted(models)
        if reference.startswith("spectral_oracle_")
        for model in one_shot_models + residual_models
    )
    comparisons.extend(
        (model, model.removesuffix("_full_basis")) for model in residual_models
        if model.endswith("_full_basis")
    )

    by_model: dict[str, dict[int, dict[str, float | str | bool | int]]] = {}
    for row in rows:
        by_model.setdefault(str(row["model"]), {})[int(row["split_seed"])] = row

    result: dict[str, Any] = {}
    for left, right in comparisons:
        common_seeds = sorted(set(by_model.get(left, {})) & set(by_model.get(right, {})))
        metric_names = sorted(
            set().union(*(by_model[left][seed].keys() for seed in common_seeds))
            & set().union(*(by_model[right][seed].keys() for seed in common_seeds))
        )
        metrics: dict[str, dict[str, float | int]] = {}
        for metric_name in metric_names:
            if metric_name in {"model", "split_seed", "uses_iterative_parameter_optimization"}:
                continue
            differences = []
            for seed in common_seeds:
                left_value = by_model[left][seed][metric_name]
                right_value = by_model[right][seed][metric_name]
                if is_real_number(left_value) and is_real_number(right_value):
                    differences.append(float(left_value) - float(right_value))
            if differences:
                metrics[metric_name] = summarize_values(differences)
        result[f"{left}_minus_{right}"] = {
            "n_splits": len(common_seeds),
            "metrics": metrics,
        }
    return result


def summarize_values(values: list[float]) -> dict[str, float | int]:
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "n": len(values),
    }


def is_real_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and np.isfinite(value)


def one_hot(labels: np.ndarray, classes: np.ndarray) -> np.ndarray:
    class_to_index = {label: index for index, label in enumerate(classes)}
    encoded = np.zeros((labels.shape[0], classes.shape[0]), dtype=float)
    for row_index, label in enumerate(labels):
        encoded[row_index, class_to_index[label]] = 1.0
    return encoded


def compiled_model_name(total_feature_count: int, block_count: int) -> str:
    if block_count == 1:
        return f"dns05_one_shot_{total_feature_count}"
    if total_feature_count % block_count == 0:
        return f"dns05_residual_{block_count}x{total_feature_count // block_count}"
    return f"dns05_residual_{block_count}blocks_{total_feature_count}"


def print_summary(summary: dict[str, Any]) -> None:
    print(
        "Model                              val_acc          test_acc         "
        "kernel_err      rank/features    solve_s   infer_s"
    )
    print(
        "---------------------------------  ---------------  ---------------  "
        "--------------  ---------------  --------  --------"
    )
    for model, model_summary in summary.items():
        metrics = model_summary["metrics"]
        val_acc = metric_cell(metrics, "validation_accuracy")
        test_acc = metric_cell(metrics, "test_accuracy")
        kernel_error = metric_cell(metrics, "kernel_reconstruction_error")
        rank = metric_mean(metrics, "compiled_rank")
        budget = metric_mean(metrics, "feature_budget")
        solve_time = metric_mean(metrics, "solve_time_seconds")
        inference_time = metric_mean(metrics, "inference_time_seconds")
        print(
            f"{model:<33}  {val_acc:<15}  {test_acc:<15}  {kernel_error:<14}  "
            f"{rank:>5.1f}/{budget:<7.1f}  {solve_time:>8.3f}  {inference_time:>8.3f}"
        )


def metric_cell(metrics: dict[str, Any], name: str) -> str:
    if name not in metrics:
        return "-"
    return f"{metrics[name]['mean']:.4f} +/- {metrics[name]['std']:.4f}"


def metric_mean(metrics: dict[str, Any], name: str) -> float:
    if name not in metrics:
        return float("nan")
    return float(metrics[name]["mean"])


def get_commit_sha() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip()


def get_git_status_short() -> str:
    completed = subprocess.run(
        ["git", "status", "--short"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--write-results", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results" / "dns05_depth_width_digits_summary.json",
    )
    parser.add_argument("--max-splits", type=int, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    config = load_config(args.config)
    result = run(config, max_splits=args.max_splits)
    command_args = sys.argv[1:] if argv is None else argv
    result["command"] = subprocess.list2cmdline(
        [sys.executable, "-m", "experiments.run_dns05_depth_width", *command_args]
    )
    print_summary(result["summary"])

    if args.write_results:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
