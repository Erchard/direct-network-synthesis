"""DNS05 train/validation-only failure-mode and scaling audit.

This runner intentionally has no test argument in ``evaluate_development``. The
split keeps an excluded partition for auditability, but every metric below is
computed from train and validation data only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from dns.features import Standardizer, stratified_train_validation_test_split
from dns.kernels import rbf_kernel
from dns.synthesis.linear_algebra import solve_primal_ridge, stable_solve
from experiments.run_dns05_confirmation import load_named_dataset
from experiments.run_dns05_depth_width import (
    get_commit_sha,
    get_git_status_short,
    load_config,
    load_digits_dataset,
    one_hot,
    select_rbf_oracle,
    summarize_values,
)
from experiments.run_dns05_landmark import _inverse_square_root_psd, uniform_landmark_indices
from experiments.run_dns05_prototype import class_hybrid_prototypes

EIGEN_CUTOFF = 1e-10

SUMMARY_METRICS = [
    "validation_accuracy",
    "validation_rmse",
    "validation_r2",
    "kernel_reconstruction_error",
    "rank",
    "rank_fraction",
    "effective_rank",
    "feature_budget",
    "model_state_bytes",
    "retained_train_samples",
    "train_feature_construction_time_seconds",
    "validation_feature_transform_time_seconds",
    "readout_grid_solve_time_seconds",
    "selected_readout_validation_inference_mean_seconds",
    "validation_prediction_mean_seconds",
    "fit_time_with_oracle_selection_seconds",
    "mean_max_train_kernel_similarity",
    "p05_max_train_kernel_similarity",
    "center_exact_train_match_count",
    "basis_rank",
    "basis_condition_number",
    "feature_condition_number",
]


def load_audit_dataset(spec: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Load a locked audit dataset without looking at model outcomes."""

    if spec["name"] == "sklearn_digits":
        X, y = load_digits_dataset()
        return X, y, {
            "name": "sklearn_digits",
            "source": "sklearn.datasets.load_digits",
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "n_classes": int(np.unique(y).size),
        }
    return load_named_dataset(spec)


def run(config: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    datasets: list[dict[str, Any]] = []

    for dataset_spec in config["datasets"]:
        X, y, metadata = load_audit_dataset(dataset_spec)
        dataset_name = metadata["name"]
        dataset_hash = hashlib.sha256(X.tobytes() + y.tobytes()).hexdigest()
        datasets.append({**metadata, "sha256": dataset_hash})
        split_seeds = dataset_spec.get("split_seeds", config["splits"]["split_seeds"])

        for seed in split_seeds:
            train, validation, excluded = stratified_train_validation_test_split(
                y,
                seed=int(seed),
                train_fraction=float(config["splits"]["train_fraction"]),
                validation_fraction=float(config["splits"]["validation_fraction"]),
            )
            split_result, record = evaluate_development(
                X[train],
                y[train],
                X[validation],
                y[validation],
                config,
                int(seed),
                dataset_name,
            )
            records.append(
                {
                    **record,
                    "dataset": dataset_name,
                    "seed": int(seed),
                    "train_indices": train.tolist(),
                    "validation_indices": validation.tolist(),
                    "excluded_indices": excluded.tolist(),
                }
            )
            rows.extend(split_result["rows"])
            selected_rows.extend(split_result["selected_rows"])
            print(f"Completed failure-scaling split {dataset_name}/{seed}", flush=True)

    return {
        "config": config,
        "commit_sha": get_commit_sha(),
        "git_status_short": get_git_status_short(),
        "datasets": datasets,
        "rows": rows,
        "selected_rows": selected_rows,
        "splits": records,
        "test_status": "not_evaluated",
        **aggregate(selected_rows, config["paired_families"]),
    }


def evaluate_development(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    config: dict[str, Any],
    seed: int,
    dataset_name: str,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Evaluate only train/validation partitions; no test partition is accepted."""

    start = time.perf_counter()
    scaler = Standardizer().fit(X_train)
    train = scaler.transform(X_train)
    validation = scaler.transform(X_validation)
    preprocessing_time = time.perf_counter() - start

    classes = np.unique(y_train)
    targets = one_hot(y_train, classes)
    observed = one_hot(y_validation, classes)

    start = time.perf_counter()
    selection = select_rbf_oracle(
        train,
        targets,
        validation,
        y_validation,
        classes,
        split_seed=seed,
        config=config,
    )
    oracle_selection_time = time.perf_counter() - start

    start = time.perf_counter()
    kernel = rbf_kernel(train, gamma=selection.gamma)
    validation_cross = rbf_kernel(validation, train, gamma=selection.gamma)
    kernel_time = time.perf_counter() - start

    representations = _build_representations(
        train,
        y_train,
        validation,
        kernel,
        validation_cross,
        selection.gamma,
        scaler,
        config,
        seed,
    )
    split_result = _score_representations(
        representations,
        targets,
        observed,
        y_validation,
        classes,
        preprocessing_time,
        oracle_selection_time,
        config,
        seed,
        dataset_name,
    )
    return split_result, {
        "oracle": asdict(selection),
        "preprocessing_seconds": preprocessing_time,
        "train_kernel_build_seconds": kernel_time,
    }


def _build_representations(
    train: np.ndarray,
    y_train: np.ndarray,
    validation: np.ndarray,
    kernel: np.ndarray,
    validation_cross: np.ndarray,
    gamma: float,
    scaler: Standardizer,
    config: dict[str, Any],
    seed: int,
) -> list[dict[str, Any]]:
    families = set(config["model_families"])
    feature_counts = [int(value) for value in config["feature_counts"]]
    representations: list[dict[str, Any]] = []

    for count in feature_counts:
        if "nystrom_uniform" in families:
            representations.append(
                _nystrom_uniform_representation(
                    train,
                    validation,
                    kernel,
                    gamma,
                    scaler,
                    count,
                    seed,
                    config,
                )
            )
        if "prototype_class_hybrid" in families:
            representations.append(
                _hybrid_prototype_representation(
                    train,
                    y_train,
                    validation,
                    kernel,
                    gamma,
                    scaler,
                    count,
                    config,
                )
            )

    if "spectral" in families:
        representations.extend(
            _spectral_representations(
                train,
                validation_cross,
                kernel,
                gamma,
                scaler,
                feature_counts,
            )
        )
    if config.get("include_rbf_reference", True):
        representations.append(_rbf_representation(train, validation_cross, kernel, scaler))
    return representations


def _nystrom_uniform_representation(
    train: np.ndarray,
    validation: np.ndarray,
    kernel: np.ndarray,
    gamma: float,
    scaler: Standardizer,
    requested_count: int,
    seed: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    count = min(requested_count, len(train))
    start = time.perf_counter()
    indices = uniform_landmark_indices(
        len(train),
        count,
        int(config["landmark_seed"]) + 1009 * seed + requested_count,
    )
    centers = train[indices]
    basis_kernel = rbf_kernel(centers, gamma=gamma)
    inverse_root, basis_rank = _inverse_square_root_psd(basis_kernel)
    train_to_centers = rbf_kernel(train, centers, gamma=gamma)
    features = train_to_centers @ inverse_root
    train_time = time.perf_counter() - start

    start = time.perf_counter()
    validation_to_centers = rbf_kernel(validation, centers, gamma=gamma)
    validation_features = validation_to_centers @ inverse_root
    validation_time = time.perf_counter() - start

    intermediate = (
        basis_kernel.nbytes
        + train_to_centers.nbytes
        + validation_to_centers.nbytes
    )
    return _representation(
        name=f"nystrom_uniform_{requested_count}",
        model_family="nystrom_uniform",
        features=features,
        validation_features=validation_features,
        kernel=kernel,
        scaler=scaler,
        train=train,
        centers=centers,
        basis_kernel=basis_kernel,
        train_to_centers=train_to_centers,
        basis_rank=basis_rank,
        train_feature_construction_time_seconds=train_time,
        validation_feature_transform_time_seconds=validation_time,
        model_state_base_bytes=_arrays_nbytes(scaler.mean_, scaler.scale_, centers, inverse_root),
        intermediate_array_bytes_estimate=intermediate,
        requested_feature_count=requested_count,
        retained_train_samples=len(centers),
        uses_train_labels_for_representation=False,
        requires_rbf_gamma_selection=True,
        predictor="linear",
        gamma=gamma,
        basis_is_train_samples=True,
    )


def _hybrid_prototype_representation(
    train: np.ndarray,
    y_train: np.ndarray,
    validation: np.ndarray,
    kernel: np.ndarray,
    gamma: float,
    scaler: Standardizer,
    requested_count: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    quantiles = np.asarray(config["prototype_quantiles"], dtype=float)
    start = time.perf_counter()
    centers = class_hybrid_prototypes(
        train,
        y_train,
        requested_count,
        quantiles,
        float(config["dipole_shift_fraction"]),
        gamma,
        int(config["hybrid_boundary_pairs_per_class"]),
    )
    basis_kernel = rbf_kernel(centers, gamma=gamma)
    inverse_root, basis_rank = _inverse_square_root_psd(basis_kernel)
    train_to_centers = rbf_kernel(train, centers, gamma=gamma)
    features = train_to_centers @ inverse_root
    train_time = time.perf_counter() - start

    start = time.perf_counter()
    validation_to_centers = rbf_kernel(validation, centers, gamma=gamma)
    validation_features = validation_to_centers @ inverse_root
    validation_time = time.perf_counter() - start

    intermediate = (
        basis_kernel.nbytes
        + train_to_centers.nbytes
        + validation_to_centers.nbytes
    )
    return _representation(
        name=f"prototype_class_hybrid_{requested_count}",
        model_family="prototype_class_hybrid",
        features=features,
        validation_features=validation_features,
        kernel=kernel,
        scaler=scaler,
        train=train,
        centers=centers,
        basis_kernel=basis_kernel,
        train_to_centers=train_to_centers,
        basis_rank=basis_rank,
        train_feature_construction_time_seconds=train_time,
        validation_feature_transform_time_seconds=validation_time,
        model_state_base_bytes=_arrays_nbytes(scaler.mean_, scaler.scale_, centers, inverse_root),
        intermediate_array_bytes_estimate=intermediate,
        requested_feature_count=requested_count,
        retained_train_samples=0,
        uses_train_labels_for_representation=True,
        requires_rbf_gamma_selection=True,
        predictor="linear",
        gamma=gamma,
        basis_is_train_samples=False,
    )


def _spectral_representations(
    train: np.ndarray,
    validation_cross: np.ndarray,
    kernel: np.ndarray,
    gamma: float,
    scaler: Standardizer,
    requested_counts: list[int],
) -> list[dict[str, Any]]:
    start = time.perf_counter()
    values, vectors = np.linalg.eigh(kernel)
    eigen_time = time.perf_counter() - start
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    threshold = EIGEN_CUTOFF * max(1.0, float(values.max()))
    valid_indices = np.flatnonzero(values > threshold)

    representations: list[dict[str, Any]] = []
    for requested_count in requested_counts:
        indices = valid_indices[: min(requested_count, valid_indices.size)]
        start = time.perf_counter()
        extension = vectors[:, indices] / np.sqrt(values[indices])
        features = vectors[:, indices] * np.sqrt(values[indices])
        feature_time = time.perf_counter() - start

        start = time.perf_counter()
        validation_features = validation_cross @ extension
        validation_time = time.perf_counter() - start

        intermediate = kernel.nbytes + values.nbytes + vectors.nbytes + validation_cross.nbytes
        representations.append(
            _representation(
                name=f"spectral_{requested_count}",
                model_family="spectral",
                features=features,
                validation_features=validation_features,
                kernel=kernel,
                scaler=scaler,
                train=train,
                centers=None,
                basis_kernel=None,
                train_to_centers=None,
                basis_rank=int(indices.size),
                train_feature_construction_time_seconds=eigen_time + feature_time,
                validation_feature_transform_time_seconds=validation_time,
                model_state_base_bytes=_arrays_nbytes(scaler.mean_, scaler.scale_, train, extension),
                intermediate_array_bytes_estimate=intermediate,
                requested_feature_count=requested_count,
                retained_train_samples=len(train),
                uses_train_labels_for_representation=False,
                requires_rbf_gamma_selection=True,
                predictor="linear",
                gamma=gamma,
                basis_is_train_samples=None,
            )
        )
    return representations


def _rbf_representation(
    train: np.ndarray,
    validation_cross: np.ndarray,
    kernel: np.ndarray,
    scaler: Standardizer,
) -> dict[str, Any]:
    return _representation(
        name="rbf",
        model_family="exact_kernel",
        features=kernel,
        validation_features=validation_cross,
        kernel=kernel,
        scaler=scaler,
        train=train,
        centers=None,
        basis_kernel=None,
        train_to_centers=None,
        basis_rank=int(np.linalg.matrix_rank(kernel)),
        train_feature_construction_time_seconds=0.0,
        validation_feature_transform_time_seconds=0.0,
        model_state_base_bytes=_arrays_nbytes(scaler.mean_, scaler.scale_, train),
        intermediate_array_bytes_estimate=kernel.nbytes + validation_cross.nbytes,
        requested_feature_count=None,
        retained_train_samples=len(train),
        uses_train_labels_for_representation=False,
        requires_rbf_gamma_selection=True,
        predictor="kernel",
        gamma=None,
        basis_is_train_samples=None,
        kernel_reconstruction_error=0.0,
    )


def _representation(
    *,
    name: str,
    model_family: str,
    features: np.ndarray,
    validation_features: np.ndarray,
    kernel: np.ndarray,
    scaler: Standardizer,
    train: np.ndarray,
    centers: np.ndarray | None,
    basis_kernel: np.ndarray | None,
    train_to_centers: np.ndarray | None,
    basis_rank: int,
    train_feature_construction_time_seconds: float,
    validation_feature_transform_time_seconds: float,
    model_state_base_bytes: int,
    intermediate_array_bytes_estimate: int,
    requested_feature_count: int | None,
    retained_train_samples: int,
    uses_train_labels_for_representation: bool,
    requires_rbf_gamma_selection: bool,
    predictor: str,
    gamma: float | None,
    basis_is_train_samples: bool | None,
    kernel_reconstruction_error: float | None = None,
) -> dict[str, Any]:
    feature_metrics = _feature_metrics(features)
    center_metrics = _center_metrics(train, centers, gamma, basis_kernel, train_to_centers)
    if kernel_reconstruction_error is None:
        kernel_reconstruction_error = _relative_kernel_error(kernel, features)
    return {
        "name": name,
        "model_family": model_family,
        "features": features,
        "validation_features": validation_features,
        "predictor": predictor,
        "kernel_reconstruction_error": kernel_reconstruction_error,
        "rank": feature_metrics["rank"],
        "rank_fraction": feature_metrics["rank_fraction"],
        "effective_rank": feature_metrics["effective_rank"],
        "feature_condition_number": feature_metrics["feature_condition_number"],
        "feature_budget": int(features.shape[1]),
        "train_feature_construction_time_seconds": train_feature_construction_time_seconds,
        "validation_feature_transform_time_seconds": validation_feature_transform_time_seconds,
        "model_state_base_bytes": model_state_base_bytes,
        "intermediate_array_bytes_estimate": int(intermediate_array_bytes_estimate),
        "requested_feature_count": requested_feature_count,
        "retained_train_samples": int(retained_train_samples),
        "requires_rbf_gamma_selection": requires_rbf_gamma_selection,
        "uses_train_labels_for_representation": uses_train_labels_for_representation,
        "basis_count": None if centers is None else len(centers),
        "basis_rank": int(basis_rank),
        "basis_is_train_samples": basis_is_train_samples,
        "scaler_state_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_),
        **center_metrics,
    }


def _score_representations(
    representations: list[dict[str, Any]],
    targets: np.ndarray,
    observed: np.ndarray,
    y_validation: np.ndarray,
    classes: np.ndarray,
    preprocessing_time: float,
    oracle_selection_time: float,
    config: dict[str, Any],
    seed: int,
    dataset_name: str,
) -> dict[str, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []

    for representation in representations:
        candidates = []
        grid_solve_time = 0.0
        for alpha in config["alphas"]:
            for intercept in config["intercepts"]:
                scores, readout, solve_time, inference_time, readout_bytes = _fit_and_score(
                    representation,
                    targets,
                    float(alpha),
                    bool(intercept),
                )
                row = _row_from_scores(
                    representation,
                    scores,
                    observed,
                    y_validation,
                    classes,
                    float(alpha),
                    bool(intercept),
                    solve_time,
                    inference_time,
                    readout_bytes,
                    preprocessing_time,
                    oracle_selection_time,
                    seed,
                    dataset_name,
                )
                rows.append(row)
                candidates.append((row, readout, readout_bytes))
                grid_solve_time += solve_time

        selected_row, selected_readout, selected_readout_bytes = min(
            candidates,
            key=lambda item: (
                -item[0]["validation_accuracy"],
                item[0]["validation_rmse"],
                item[0]["alpha"],
                item[0]["intercept"],
            ),
        )
        repeated_validation = _repeat_inference(
            representation,
            selected_readout,
            selected_row["intercept"],
            int(config["prediction_warmups"]),
            int(config["prediction_repeats"]),
        )
        selected_rows.append(
            {
                **selected_row,
                "selection_status": "validation_selected",
                "readout_grid_solve_time_seconds": grid_solve_time,
                "selected_readout_validation_inference_mean_seconds": repeated_validation,
                "validation_prediction_mean_seconds": (
                    representation["validation_feature_transform_time_seconds"]
                    + repeated_validation
                ),
                "fit_time_without_oracle_selection_seconds": (
                    representation["train_feature_construction_time_seconds"]
                    + grid_solve_time
                ),
                "fit_time_with_oracle_selection_seconds": (
                    representation["train_feature_construction_time_seconds"]
                    + grid_solve_time
                    + preprocessing_time
                    + (
                        oracle_selection_time
                        if representation["requires_rbf_gamma_selection"]
                        else 0.0
                    )
                ),
                "model_state_bytes": (
                    representation["model_state_base_bytes"] + selected_readout_bytes
                ),
                "readout_state_bytes": selected_readout_bytes,
            }
        )
    return {"rows": rows, "selected_rows": selected_rows}


def _fit_and_score(
    representation: dict[str, Any],
    targets: np.ndarray,
    alpha: float,
    intercept: bool,
) -> tuple[np.ndarray, Any, float, float, int]:
    if representation["predictor"] == "kernel":
        start = time.perf_counter()
        readout = _fit_kernel_readout(representation["features"], targets, alpha, intercept)
        solve_time = time.perf_counter() - start
        start = time.perf_counter()
        scores = _predict_kernel(representation["validation_features"], readout)
        inference_time = time.perf_counter() - start
        return scores, readout, solve_time, inference_time, _kernel_readout_bytes(readout)

    start = time.perf_counter()
    readout = solve_primal_ridge(
        representation["features"],
        targets,
        alpha=alpha,
        fit_intercept=intercept,
    )
    solve_time = time.perf_counter() - start
    start = time.perf_counter()
    scores = _predict_linear(representation["validation_features"], readout, intercept)
    inference_time = time.perf_counter() - start
    return scores, readout, solve_time, inference_time, int(readout.nbytes)


def _row_from_scores(
    representation: dict[str, Any],
    scores: np.ndarray,
    observed: np.ndarray,
    labels: np.ndarray,
    classes: np.ndarray,
    alpha: float,
    intercept: bool,
    solve_time: float,
    inference_time: float,
    readout_bytes: int,
    preprocessing_time: float,
    oracle_selection_time: float,
    seed: int,
    dataset_name: str,
) -> dict[str, Any]:
    residual_sum = float(np.sum((scores - observed) ** 2))
    total_sum = float(np.sum((observed - observed.mean(axis=0)) ** 2))
    predictions = classes[scores.argmax(axis=1)]
    model_state_bytes = representation["model_state_base_bytes"] + readout_bytes
    return {
        "dataset": dataset_name,
        "model": representation["name"],
        "model_family": representation["model_family"],
        "split_seed": seed,
        "alpha": alpha,
        "intercept": intercept,
        "validation_accuracy": float(np.mean(predictions == labels)),
        "validation_rmse": float(np.sqrt(np.mean((scores - observed) ** 2))),
        "validation_r2": 1.0 - residual_sum / total_sum if total_sum else 0.0,
        "test_accuracy": None,
        "test_rmse": None,
        "test_r2": None,
        "test_status": "not_evaluated_validation_only_audit",
        "kernel_reconstruction_error": representation["kernel_reconstruction_error"],
        "rank": representation["rank"],
        "rank_fraction": representation["rank_fraction"],
        "effective_rank": representation["effective_rank"],
        "feature_condition_number": representation["feature_condition_number"],
        "feature_budget": representation["feature_budget"],
        "requested_feature_count": representation["requested_feature_count"],
        "basis_count": representation["basis_count"],
        "basis_rank": representation["basis_rank"],
        "basis_is_train_samples": representation["basis_is_train_samples"],
        "center_exact_train_match_count": representation["center_exact_train_match_count"],
        "prototype_train_exact_match_count": representation["center_exact_train_match_count"],
        "retained_train_samples": representation["retained_train_samples"],
        "readout_parameter_count": (
            representation["feature_budget"] + int(intercept)
        ) * len(classes),
        "model_state_bytes": model_state_bytes,
        "readout_state_bytes": readout_bytes,
        "scaler_state_bytes": representation["scaler_state_bytes"],
        "intermediate_array_bytes_estimate": representation["intermediate_array_bytes_estimate"],
        "preprocessing_time_seconds": preprocessing_time,
        "oracle_selection_time_seconds": (
            oracle_selection_time if representation["requires_rbf_gamma_selection"] else 0.0
        ),
        "train_feature_construction_time_seconds": representation[
            "train_feature_construction_time_seconds"
        ],
        "validation_feature_transform_time_seconds": representation[
            "validation_feature_transform_time_seconds"
        ],
        "readout_solve_time_seconds": solve_time,
        "readout_validation_inference_time_seconds": inference_time,
        "readout_grid_solve_time_seconds": solve_time,
        "selected_readout_validation_inference_mean_seconds": inference_time,
        "validation_prediction_mean_seconds": (
            representation["validation_feature_transform_time_seconds"] + inference_time
        ),
        "fit_time_without_oracle_selection_seconds": (
            representation["train_feature_construction_time_seconds"] + solve_time
        ),
        "fit_time_with_oracle_selection_seconds": (
            representation["train_feature_construction_time_seconds"]
            + solve_time
            + preprocessing_time
            + (
                oracle_selection_time
                if representation["requires_rbf_gamma_selection"]
                else 0.0
            )
        ),
        "requires_rbf_gamma_selection": representation["requires_rbf_gamma_selection"],
        "uses_train_labels_for_representation": representation[
            "uses_train_labels_for_representation"
        ],
        "uses_iterative_parameter_optimization": False,
        **_row_center_metrics(representation),
    }


def _row_center_metrics(representation: dict[str, Any]) -> dict[str, Any]:
    return {
        key: representation[key]
        for key in (
            "mean_max_train_kernel_similarity",
            "std_max_train_kernel_similarity",
            "min_max_train_kernel_similarity",
            "p05_max_train_kernel_similarity",
            "median_max_train_kernel_similarity",
            "coverage_fraction_ge_0_5",
            "coverage_fraction_ge_0_8",
            "basis_condition_number",
        )
    }


def _fit_kernel_readout(
    kernel: np.ndarray,
    targets: np.ndarray,
    alpha: float,
    intercept: bool,
) -> dict[str, Any]:
    if intercept:
        column_mean = kernel.mean(axis=0)
        grand_mean = float(kernel.mean())
        centered = kernel - column_mean[None, :] - column_mean[:, None] + grand_mean
        target_mean = targets.mean(axis=0)
    else:
        column_mean = None
        grand_mean = 0.0
        centered = kernel
        target_mean = np.zeros(targets.shape[1], dtype=float)
    dual = stable_solve(centered + alpha * np.eye(len(targets)), targets - target_mean)
    return {
        "dual": dual,
        "intercept": intercept,
        "column_mean": column_mean,
        "grand_mean": grand_mean,
        "target_mean": target_mean,
    }


def _predict_kernel(cross: np.ndarray, readout: dict[str, Any]) -> np.ndarray:
    if readout["intercept"]:
        cross = cross - cross.mean(axis=1)[:, None] - readout["column_mean"] + readout["grand_mean"]
    return cross @ readout["dual"] + readout["target_mean"]


def _predict_linear(features: np.ndarray, readout: np.ndarray, intercept: bool) -> np.ndarray:
    design = np.column_stack([np.ones(len(features)), features]) if intercept else features
    return design @ readout


def _repeat_inference(
    representation: dict[str, Any],
    readout: Any,
    intercept: bool,
    warmups: int,
    repeats: int,
) -> float:
    for _ in range(warmups):
        _predict_with_readout(representation, readout, intercept)
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        _predict_with_readout(representation, readout, intercept)
        timings.append(time.perf_counter() - start)
    return float(np.mean(timings)) if timings else 0.0


def _predict_with_readout(
    representation: dict[str, Any],
    readout: Any,
    intercept: bool,
) -> np.ndarray:
    if representation["predictor"] == "kernel":
        return _predict_kernel(representation["validation_features"], readout)
    return _predict_linear(representation["validation_features"], readout, intercept)


def _feature_metrics(features: np.ndarray) -> dict[str, Any]:
    feature_budget = int(features.shape[1])
    rank = int(np.linalg.matrix_rank(features))
    singular_values = np.linalg.svd(features, compute_uv=False)
    threshold = EIGEN_CUTOFF * max(1.0, float(singular_values.max(initial=0.0)))
    kept = singular_values[singular_values > threshold]
    if kept.size:
        condition = float(kept.max() / kept.min())
        effective_rank = float((kept.sum() ** 2) / np.sum(kept**2))
    else:
        condition = None
        effective_rank = 0.0
    return {
        "rank": rank,
        "rank_fraction": rank / max(1, feature_budget),
        "effective_rank": effective_rank,
        "feature_condition_number": condition,
    }


def _center_metrics(
    train: np.ndarray,
    centers: np.ndarray | None,
    gamma: float | None,
    basis_kernel: np.ndarray | None,
    train_to_centers: np.ndarray | None,
) -> dict[str, Any]:
    if centers is None or gamma is None:
        return {
            "center_exact_train_match_count": None,
            "mean_max_train_kernel_similarity": None,
            "std_max_train_kernel_similarity": None,
            "min_max_train_kernel_similarity": None,
            "p05_max_train_kernel_similarity": None,
            "median_max_train_kernel_similarity": None,
            "coverage_fraction_ge_0_5": None,
            "coverage_fraction_ge_0_8": None,
            "basis_condition_number": None,
        }
    if basis_kernel is None:
        basis_kernel = rbf_kernel(centers, gamma=gamma)
    if train_to_centers is None:
        train_to_centers = rbf_kernel(train, centers, gamma=gamma)

    max_similarity = train_to_centers.max(axis=1)
    basis_condition = _condition_number_from_eigenvalues(np.linalg.eigvalsh(basis_kernel))
    return {
        "center_exact_train_match_count": _exact_train_match_count(train, centers),
        "mean_max_train_kernel_similarity": float(np.mean(max_similarity)),
        "std_max_train_kernel_similarity": float(np.std(max_similarity, ddof=1)),
        "min_max_train_kernel_similarity": float(np.min(max_similarity)),
        "p05_max_train_kernel_similarity": float(np.quantile(max_similarity, 0.05)),
        "median_max_train_kernel_similarity": float(np.median(max_similarity)),
        "coverage_fraction_ge_0_5": float(np.mean(max_similarity >= 0.5)),
        "coverage_fraction_ge_0_8": float(np.mean(max_similarity >= 0.8)),
        "basis_condition_number": basis_condition,
    }


def _condition_number_from_eigenvalues(values: np.ndarray) -> float | None:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return None
    threshold = EIGEN_CUTOFF * max(1.0, float(values.max()))
    kept = values[values > threshold]
    if kept.size == 0:
        return None
    return float(kept.max() / kept.min())


def _exact_train_match_count(train: np.ndarray, centers: np.ndarray) -> int:
    count = 0
    for center in centers:
        matches = np.all(np.isclose(train, center, rtol=0.0, atol=1e-12), axis=1)
        count += int(np.any(matches))
    return count


def _relative_kernel_error(kernel: np.ndarray, features: np.ndarray) -> float:
    denominator = float(np.linalg.norm(kernel))
    if denominator == 0.0:
        return 0.0
    return float(np.linalg.norm(kernel - features @ features.T) / denominator)


def _kernel_readout_bytes(readout: dict[str, Any]) -> int:
    arrays = [readout["dual"], readout["target_mean"]]
    if readout["column_mean"] is not None:
        arrays.append(readout["column_mean"])
    return _arrays_nbytes(*arrays) + 8


def _arrays_nbytes(*arrays: np.ndarray | None) -> int:
    return int(sum(np.asarray(array).nbytes for array in arrays if array is not None))


def aggregate(
    selected_rows: list[dict[str, Any]],
    pair_specs: list[list[str]],
) -> dict[str, Any]:
    return {
        "selected_summary": _selected_summary(selected_rows),
        "paired_differences": _paired_differences(selected_rows, pair_specs),
    }


def _selected_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, int | None], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["dataset"], row["model"], row["requested_feature_count"])
        groups.setdefault(key, []).append(row)
    summaries = []
    for (dataset, model, requested_count), group in sorted(groups.items(), key=str):
        summaries.append(
            {
                "dataset": dataset,
                "model": model,
                "requested_feature_count": requested_count,
                "n_splits": len({row["split_seed"] for row in group}),
                "metrics": _summarize_metrics(group, SUMMARY_METRICS),
            }
        )
    return summaries


def _paired_differences(
    rows: list[dict[str, Any]],
    pair_specs: list[list[str]],
) -> list[dict[str, Any]]:
    by_key = {
        (
            row["dataset"],
            row["model_family"],
            row["requested_feature_count"],
            row["split_seed"],
        ): row
        for row in rows
        if row["requested_feature_count"] is not None
    }
    datasets = sorted({row["dataset"] for row in rows})
    counts = sorted(
        {
            row["requested_feature_count"]
            for row in rows
            if row["requested_feature_count"] is not None
        }
    )
    reports = []
    for left, right in pair_specs:
        for dataset in datasets:
            for count in counts:
                left_rows = {
                    seed: row
                    for (row_dataset, family, row_count, seed), row in by_key.items()
                    if row_dataset == dataset and family == left and row_count == count
                }
                right_rows = {
                    seed: row
                    for (row_dataset, family, row_count, seed), row in by_key.items()
                    if row_dataset == dataset and family == right and row_count == count
                }
                common_seeds = sorted(set(left_rows) & set(right_rows))
                if not common_seeds:
                    continue
                metrics = {}
                for metric in SUMMARY_METRICS:
                    differences = []
                    for seed in common_seeds:
                        left_value = left_rows[seed].get(metric)
                        right_value = right_rows[seed].get(metric)
                        if is_real_number(left_value) and is_real_number(right_value):
                            differences.append(float(left_value) - float(right_value))
                    if differences:
                        metrics[metric] = summarize_values(differences)
                reports.append(
                    {
                        "dataset": dataset,
                        "requested_feature_count": count,
                        "left_family": left,
                        "right_family": right,
                        "n_splits": len(common_seeds),
                        "metrics": metrics,
                    }
                )
    return reports


def _summarize_metrics(
    rows: list[dict[str, Any]],
    metrics: list[str],
) -> dict[str, dict[str, float | int]]:
    summary = {}
    for metric in metrics:
        values = [float(row[metric]) for row in rows if is_real_number(row.get(metric))]
        if values:
            summary[metric] = summarize_values(values)
    return summary


def is_real_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and np.isfinite(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/dns05_failure_scaling_audit.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/dns05_failure_scaling_audit.json"),
    )
    args = parser.parse_args()
    result = run(load_config(args.config))

    from importlib.metadata import version

    result["environment"] = {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scikit_learn": version("scikit-learn"),
    }
    result["command"] = " ".join(sys.argv)
    result["git_diff_stat"] = subprocess.run(
        ["git", "diff", "--stat"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
