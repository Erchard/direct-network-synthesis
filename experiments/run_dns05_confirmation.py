"""Fresh-boundary DNS05 confirmation runner with validation-selected test scoring."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from dns.features import (
    Standardizer,
    deterministic_relu_projection,
    stratified_train_validation_test_split,
)
from dns.kernels import rbf_kernel
from dns.synthesis.linear_algebra import solve_primal_ridge, stable_solve
from experiments.run_dns05_depth_width import (
    get_commit_sha,
    get_git_status_short,
    load_config,
    one_hot,
    relu_features,
    select_rbf_oracle,
    summarize_values,
)
from experiments.run_dns05_landmark import (
    EIGEN_CUTOFF,
    _inverse_square_root_psd,
    _relative_kernel_error,
    uniform_landmark_indices,
)
from experiments.run_dns05_prototype import _exact_train_match_count, class_hybrid_prototypes

PROJECT_ROOT = Path(__file__).resolve().parents[1]

METRICS = [
    "validation_accuracy",
    "validation_rmse",
    "validation_r2",
    "test_accuracy",
    "test_rmse",
    "test_r2",
    "rank",
    "feature_budget",
    "readout_parameter_count",
    "retained_train_samples",
    "model_state_bytes",
    "intermediate_array_bytes_estimate",
    "build_peak_tracemalloc_bytes",
    "train_feature_construction_time_seconds",
    "validation_feature_transform_time_seconds",
    "test_feature_transform_time_seconds",
    "readout_grid_solve_time_seconds",
    "selected_readout_validation_inference_mean_seconds",
    "selected_readout_test_inference_mean_seconds",
    "validation_prediction_mean_seconds",
    "test_prediction_mean_seconds",
    "fit_time_without_oracle_selection_seconds",
    "fit_time_with_oracle_selection_seconds",
    "kernel_reconstruction_error",
    "prototype_count",
    "prototype_train_exact_match_count",
]


def load_named_dataset(spec: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Load a locked confirmation dataset without inspecting model outcomes."""

    name = spec["name"]
    if name == "sklearn_breast_cancer":
        try:
            from sklearn.datasets import load_breast_cancer
        except ImportError as exc:
            raise RuntimeError("scikit-learn is required for sklearn_breast_cancer.") from exc

        data = load_breast_cancer()
        X = np.asarray(data.data, dtype=float)
        y = np.asarray(data.target)
        metadata = {
            "name": name,
            "source": "sklearn.datasets.load_breast_cancer",
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "n_classes": int(np.unique(y).size),
            "target_names": [str(value) for value in data.target_names],
        }
        return X, y, metadata
    if name == "synthetic_multiclass_v1":
        try:
            from sklearn.datasets import make_classification
        except ImportError as exc:
            raise RuntimeError("scikit-learn is required for synthetic_multiclass_v1.") from exc

        params = {
            "n_samples": int(spec["n_samples"]),
            "n_features": int(spec["n_features"]),
            "n_informative": int(spec["n_informative"]),
            "n_redundant": int(spec["n_redundant"]),
            "n_classes": int(spec["n_classes"]),
            "n_clusters_per_class": int(spec["n_clusters_per_class"]),
            "class_sep": float(spec["class_sep"]),
            "flip_y": float(spec["flip_y"]),
            "random_state": int(spec["random_seed"]),
        }
        X, y = make_classification(**params)
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        metadata = {
            "name": name,
            "source": "sklearn.datasets.make_classification",
            **params,
        }
        return X, y, metadata
    raise ValueError(f"Unsupported confirmation dataset: {name!r}.")


def run(config: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    datasets: list[dict[str, Any]] = []

    for dataset_spec in config["datasets"]:
        X, y, metadata = load_named_dataset(dataset_spec)
        dataset_name = metadata["name"]
        dataset_hash = hashlib.sha256(X.tobytes() + y.tobytes()).hexdigest()
        datasets.append({**metadata, "sha256": dataset_hash})
        for seed in config["splits"]["split_seeds"]:
            train, validation, test = stratified_train_validation_test_split(
                y,
                seed=int(seed),
                train_fraction=float(config["splits"]["train_fraction"]),
                validation_fraction=float(config["splits"]["validation_fraction"]),
            )
            split_result, record = evaluate_split(
                X[train],
                y[train],
                X[validation],
                y[validation],
                X[test],
                y[test],
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
                    "test_indices": test.tolist(),
                }
            )
            rows.extend(split_result["rows"])
            selected_rows.extend(split_result["selected_rows"])
            print(f"Completed confirmation split {dataset_name}/{seed}", flush=True)

    return {
        "config": config,
        "commit_sha": get_commit_sha(),
        "git_status_short": get_git_status_short(),
        "datasets": datasets,
        "rows": rows,
        "selected_rows": selected_rows,
        "splits": records,
        "test_status": "evaluated_after_validation_selection",
        **aggregate(rows, selected_rows, config["paired_models"]),
    }


def evaluate_split(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    config: dict[str, Any],
    seed: int,
    dataset_name: str,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Fit on train, select readouts on validation, then score selected readouts on test."""

    start = time.perf_counter()
    scaler = Standardizer().fit(X_train)
    train = scaler.transform(X_train)
    validation = scaler.transform(X_validation)
    test = scaler.transform(X_test)
    preprocessing_time = time.perf_counter() - start

    classes = np.unique(y_train)
    targets = one_hot(y_train, classes)
    validation_targets = one_hot(y_validation, classes)
    test_targets = one_hot(y_test, classes)

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

    representations = _build_representations(
        train,
        y_train,
        validation,
        test,
        selection.gamma,
        scaler,
        config,
        seed,
    )
    requested = set(config["models"])
    available = {representation["name"] for representation in representations}
    missing = requested - available
    if missing:
        raise ValueError(f"Requested models are unavailable: {sorted(missing)}")

    result = _score_representations(
        [
            representation
            for representation in representations
            if representation["name"] in requested
        ],
        targets,
        validation_targets,
        test_targets,
        y_validation,
        y_test,
        classes,
        preprocessing_time,
        oracle_selection_time,
        config,
        seed,
        dataset_name,
    )
    return result, {"oracle": asdict(selection), "preprocessing_seconds": preprocessing_time}


def _build_representations(
    train: np.ndarray,
    y_train: np.ndarray,
    validation: np.ndarray,
    test: np.ndarray,
    gamma: float,
    scaler: Standardizer,
    config: dict[str, Any],
    seed: int,
) -> list[dict[str, Any]]:
    count = int(config["feature_count"])
    kernel = rbf_kernel(train, gamma=gamma)
    return [
        _linear_representation(train, validation, test, scaler),
        _fixed_relu_representation(train, validation, test, scaler, config),
        _nystrom_uniform_representation(train, validation, test, scaler, gamma, config, seed),
        _hybrid_prototype_representation(
            train,
            y_train,
            validation,
            test,
            scaler,
            kernel,
            gamma,
            config,
        ),
        _spectral_representation(train, validation, test, scaler, kernel, gamma, count),
        _rbf_representation(train, validation, test, scaler, kernel, gamma),
    ]


def _linear_representation(train, validation, test, scaler):
    return {
        "name": "linear",
        "features": train,
        "validation_features": validation,
        "test_features": test,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": None,
        "train_feature_construction_time_seconds": 0.0,
        "validation_feature_transform_time_seconds": 0.0,
        "test_feature_transform_time_seconds": 0.0,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_),
        "intermediate_array_bytes_estimate": train.nbytes + validation.nbytes + test.nbytes,
        "build_peak_tracemalloc_bytes": 0,
        "retained_train_samples": 0,
        "requires_rbf_gamma_selection": False,
        "uses_train_labels_for_representation": False,
        "feature_family": "linear",
        "prototype_count": None,
        "prototype_train_exact_match_count": None,
    }


def _fixed_relu_representation(train, validation, test, scaler, config):
    total_features = int(config["fixed_relu_total_feature_count"])
    hidden_units = total_features - train.shape[1]
    if hidden_units <= 0:
        raise ValueError("fixed_relu_total_feature_count must exceed dataset feature count.")

    def build():
        weights, bias = deterministic_relu_projection(
            n_features=train.shape[1],
            hidden_units=hidden_units,
            seed=int(config["fixed_relu_seed"]),
        )
        start = time.perf_counter()
        features = relu_features(train, weights, bias, include_original=True)
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_features = relu_features(validation, weights, bias, include_original=True)
        validation_time = time.perf_counter() - start
        start = time.perf_counter()
        test_features = relu_features(test, weights, bias, include_original=True)
        test_time = time.perf_counter() - start
        return (
            features,
            validation_features,
            test_features,
            weights,
            bias,
            train_time,
            validation_time,
            test_time,
        )

    (
        (features, validation_features, test_features, weights, bias, train_time, val_time, test_time),
        peak,
    ) = _measure_peak(build)
    return {
        "name": f"fixed_relu_{features.shape[1]}",
        "features": features,
        "validation_features": validation_features,
        "test_features": test_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": None,
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": val_time,
        "test_feature_transform_time_seconds": test_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, weights, bias),
        "intermediate_array_bytes_estimate": (
            features.nbytes + validation_features.nbytes + test_features.nbytes
        ),
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": 0,
        "requires_rbf_gamma_selection": False,
        "uses_train_labels_for_representation": False,
        "feature_family": "seeded_relu",
        "prototype_count": None,
        "prototype_train_exact_match_count": None,
    }


def _nystrom_uniform_representation(train, validation, test, scaler, gamma, config, seed):
    count = int(config["feature_count"])

    def build():
        start = time.perf_counter()
        indices = uniform_landmark_indices(
            len(train),
            count,
            int(config["landmark_seed"]) + 1009 * seed + count,
        )
        landmarks = train[indices]
        landmark_kernel = rbf_kernel(landmarks, gamma=gamma)
        inverse_root, landmark_rank = _inverse_square_root_psd(landmark_kernel)
        train_to_landmarks = rbf_kernel(train, landmarks, gamma=gamma)
        features = train_to_landmarks @ inverse_root
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_to_landmarks = rbf_kernel(validation, landmarks, gamma=gamma)
        validation_features = validation_to_landmarks @ inverse_root
        validation_time = time.perf_counter() - start
        start = time.perf_counter()
        test_to_landmarks = rbf_kernel(test, landmarks, gamma=gamma)
        test_features = test_to_landmarks @ inverse_root
        test_time = time.perf_counter() - start
        intermediate = (
            landmark_kernel.nbytes
            + train_to_landmarks.nbytes
            + validation_to_landmarks.nbytes
            + test_to_landmarks.nbytes
        )
        return (
            features,
            validation_features,
            test_features,
            landmarks,
            inverse_root,
            landmark_rank,
            train_time,
            validation_time,
            test_time,
            intermediate,
        )

    (
        (
            features,
            validation_features,
            test_features,
            landmarks,
            inverse_root,
            landmark_rank,
            train_time,
            val_time,
            test_time,
            intermediate,
        ),
        peak,
    ) = _measure_peak(build)
    return {
        "name": f"nystrom_uniform_{count}",
        "features": features,
        "validation_features": validation_features,
        "test_features": test_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": _relative_kernel_error(rbf_kernel(train, gamma=gamma), features),
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": val_time,
        "test_feature_transform_time_seconds": test_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, landmarks, inverse_root),
        "intermediate_array_bytes_estimate": intermediate,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": len(landmarks),
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": False,
        "feature_family": "nystrom",
        "landmark_rank": landmark_rank,
        "prototype_count": None,
        "prototype_train_exact_match_count": None,
    }


def _hybrid_prototype_representation(
    train,
    y_train,
    validation,
    test,
    scaler,
    kernel,
    gamma,
    config,
):
    count = int(config["feature_count"])
    quantiles = np.asarray(config["prototype_quantiles"], dtype=float)

    def build():
        start = time.perf_counter()
        centers = class_hybrid_prototypes(
            train,
            y_train,
            count,
            quantiles,
            float(config["dipole_shift_fraction"]),
            gamma,
            int(config["hybrid_boundary_pairs_per_class"]),
        )
        center_kernel = rbf_kernel(centers, gamma=gamma)
        inverse_root, center_rank = _inverse_square_root_psd(center_kernel)
        train_to_centers = rbf_kernel(train, centers, gamma=gamma)
        features = train_to_centers @ inverse_root
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_to_centers = rbf_kernel(validation, centers, gamma=gamma)
        validation_features = validation_to_centers @ inverse_root
        validation_time = time.perf_counter() - start
        start = time.perf_counter()
        test_to_centers = rbf_kernel(test, centers, gamma=gamma)
        test_features = test_to_centers @ inverse_root
        test_time = time.perf_counter() - start
        intermediate = (
            center_kernel.nbytes
            + train_to_centers.nbytes
            + validation_to_centers.nbytes
            + test_to_centers.nbytes
        )
        return (
            centers,
            features,
            validation_features,
            test_features,
            inverse_root,
            center_rank,
            train_time,
            validation_time,
            test_time,
            intermediate,
        )

    (
        (
            centers,
            features,
            validation_features,
            test_features,
            inverse_root,
            center_rank,
            train_time,
            val_time,
            test_time,
            intermediate,
        ),
        peak,
    ) = _measure_peak(build)
    return {
        "name": f"prototype_class_hybrid_{count}",
        "features": features,
        "validation_features": validation_features,
        "test_features": test_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": _relative_kernel_error(kernel, features),
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": val_time,
        "test_feature_transform_time_seconds": test_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, centers, inverse_root),
        "intermediate_array_bytes_estimate": intermediate,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": 0,
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": True,
        "feature_family": "synthetic_rbf_prototypes",
        "landmark_rank": center_rank,
        "prototype_count": len(centers),
        "prototype_train_exact_match_count": _exact_train_match_count(train, centers),
    }


def _spectral_representation(train, validation, test, scaler, kernel, gamma, count):
    def build():
        start = time.perf_counter()
        values, vectors = np.linalg.eigh(kernel)
        order = np.argsort(values)[::-1]
        values, vectors = values[order], vectors[:, order]
        threshold = EIGEN_CUTOFF * max(1.0, float(values.max()))
        indices = np.flatnonzero(values > threshold)[:count]
        extension = vectors[:, indices] / np.sqrt(values[indices])
        features = vectors[:, indices] * np.sqrt(values[indices])
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_cross = rbf_kernel(validation, train, gamma=gamma)
        validation_features = validation_cross @ extension
        validation_time = time.perf_counter() - start
        start = time.perf_counter()
        test_cross = rbf_kernel(test, train, gamma=gamma)
        test_features = test_cross @ extension
        test_time = time.perf_counter() - start
        intermediate = (
            kernel.nbytes
            + values.nbytes
            + vectors.nbytes
            + validation_cross.nbytes
            + test_cross.nbytes
        )
        return (
            features,
            validation_features,
            test_features,
            extension,
            train_time,
            validation_time,
            test_time,
            intermediate,
        )

    (
        (
            features,
            validation_features,
            test_features,
            extension,
            train_time,
            val_time,
            test_time,
            intermediate,
        ),
        peak,
    ) = _measure_peak(build)
    return {
        "name": f"spectral_{count}",
        "features": features,
        "validation_features": validation_features,
        "test_features": test_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": _relative_kernel_error(kernel, features),
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": val_time,
        "test_feature_transform_time_seconds": test_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, train, extension),
        "intermediate_array_bytes_estimate": intermediate,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": len(train),
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": False,
        "feature_family": "spectral_oracle",
        "prototype_count": None,
        "prototype_train_exact_match_count": None,
    }


def _rbf_representation(train, validation, test, scaler, kernel, gamma):
    def build():
        start = time.perf_counter()
        validation_cross = rbf_kernel(validation, train, gamma=gamma)
        validation_time = time.perf_counter() - start
        start = time.perf_counter()
        test_cross = rbf_kernel(test, train, gamma=gamma)
        test_time = time.perf_counter() - start
        return validation_cross, test_cross, validation_time, test_time

    (validation_cross, test_cross, val_time, test_time), peak = _measure_peak(build)
    return {
        "name": "rbf",
        "features": kernel,
        "validation_features": validation_cross,
        "test_features": test_cross,
        "predictor": _kernel_predictor,
        "kernel_reconstruction_error": 0.0,
        "train_feature_construction_time_seconds": 0.0,
        "validation_feature_transform_time_seconds": val_time,
        "test_feature_transform_time_seconds": test_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, train),
        "intermediate_array_bytes_estimate": kernel.nbytes + validation_cross.nbytes + test_cross.nbytes,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": len(train),
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": False,
        "feature_family": "exact_kernel",
        "prototype_count": None,
        "prototype_train_exact_match_count": None,
    }


def _score_representations(
    representations,
    targets,
    validation_targets,
    test_targets,
    y_validation,
    y_test,
    classes,
    preprocessing_time,
    oracle_selection_time,
    config,
    seed,
    dataset_name,
):
    rows = []
    selected_rows = []
    for representation in representations:
        candidates = []
        grid_solve_time = 0.0
        for alpha in config["alphas"]:
            for intercept in config["intercepts"]:
                scores, readout, solve_time, inference_time, readout_bytes = representation[
                    "predictor"
                ](representation, targets, alpha, intercept, "validation")
                row = _row_from_scores(
                    representation,
                    scores,
                    validation_targets,
                    y_validation,
                    classes,
                    alpha,
                    intercept,
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
                item[0]["alpha"],
                item[0]["intercept"],
            ),
        )
        test_scores, test_inference = _predict_partition(
            representation,
            selected_readout,
            selected_row["intercept"],
            "test",
        )
        repeated_validation = _repeat_inference(
            representation,
            selected_readout,
            selected_row["intercept"],
            "validation",
            int(config["prediction_warmups"]),
            int(config["prediction_repeats"]),
        )
        repeated_test = _repeat_inference(
            representation,
            selected_readout,
            selected_row["intercept"],
            "test",
            int(config["prediction_warmups"]),
            int(config["prediction_repeats"]),
        )
        fit_without_oracle = (
            representation["train_feature_construction_time_seconds"] + grid_solve_time
        )
        fit_with_oracle = (
            fit_without_oracle
            + preprocessing_time
            + (oracle_selection_time if representation["requires_rbf_gamma_selection"] else 0.0)
        )
        selected_rows.append(
            {
                **selected_row,
                **_test_metrics(test_scores, test_targets, y_test, classes),
                "test_status": "evaluated_after_validation_selection",
                "selection_status": "validation_selected",
                "readout_grid_solve_time_seconds": grid_solve_time,
                "selected_readout_validation_inference_mean_seconds": repeated_validation,
                "selected_readout_test_inference_mean_seconds": repeated_test,
                "validation_prediction_mean_seconds": (
                    representation["validation_feature_transform_time_seconds"]
                    + repeated_validation
                ),
                "test_prediction_mean_seconds": (
                    representation["test_feature_transform_time_seconds"] + repeated_test
                ),
                "fit_time_without_oracle_selection_seconds": fit_without_oracle,
                "fit_time_with_oracle_selection_seconds": fit_with_oracle,
                "model_state_bytes": representation["model_state_base_bytes"]
                + selected_readout_bytes,
                "test_readout_inference_time_seconds": test_inference,
            }
        )
    return {"rows": rows, "selected_rows": selected_rows}


def _linear_predictor(representation, targets, alpha, intercept, partition):
    start = time.perf_counter()
    readout = solve_primal_ridge(
        representation["features"],
        targets,
        alpha=float(alpha),
        fit_intercept=bool(intercept),
    )
    solve_time = time.perf_counter() - start
    features = representation[f"{partition}_features"]
    start = time.perf_counter()
    scores = _predict_linear(features, readout, bool(intercept))
    inference_time = time.perf_counter() - start
    return scores, readout, solve_time, inference_time, readout.nbytes


def _kernel_predictor(representation, targets, alpha, intercept, partition):
    start = time.perf_counter()
    readout = _fit_kernel_readout(
        representation["features"],
        targets,
        float(alpha),
        bool(intercept),
    )
    solve_time = time.perf_counter() - start
    features = representation[f"{partition}_features"]
    start = time.perf_counter()
    scores = _predict_kernel(features, readout)
    inference_time = time.perf_counter() - start
    return scores, readout, solve_time, inference_time, _kernel_readout_bytes(readout)


def _predict_partition(representation, readout, intercept, partition):
    features = representation[f"{partition}_features"]
    start = time.perf_counter()
    if representation["predictor"] is _kernel_predictor:
        scores = _predict_kernel(features, readout)
    else:
        scores = _predict_linear(features, readout, bool(intercept))
    return scores, time.perf_counter() - start


def _fit_kernel_readout(kernel, targets, alpha, intercept):
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


def _predict_linear(features, readout, intercept):
    design = np.column_stack([np.ones(len(features)), features]) if intercept else features
    return design @ readout


def _predict_kernel(cross, readout):
    if readout["intercept"]:
        cross = cross - cross.mean(axis=1)[:, None] - readout["column_mean"] + readout["grand_mean"]
    return cross @ readout["dual"] + readout["target_mean"]


def _row_from_scores(
    representation,
    scores,
    observed,
    labels,
    classes,
    alpha,
    intercept,
    solve_time,
    inference_time,
    readout_bytes,
    preprocessing_time,
    oracle_selection_time,
    seed,
    dataset_name,
):
    residual_sum = float(np.sum((scores - observed) ** 2))
    total_sum = float(np.sum((observed - observed.mean(axis=0)) ** 2))
    predictions = classes[scores.argmax(axis=1)]
    return {
        "dataset": dataset_name,
        "model": representation["name"],
        "split_seed": seed,
        "alpha": alpha,
        "intercept": intercept,
        "validation_accuracy": float(np.mean(predictions == labels)),
        "validation_rmse": float(np.sqrt(np.mean((scores - observed) ** 2))),
        "validation_r2": 1.0 - residual_sum / total_sum if total_sum else 0.0,
        "test_accuracy": None,
        "test_rmse": None,
        "test_r2": None,
        "test_status": "not_evaluated_grid_row",
        "kernel_reconstruction_error": representation["kernel_reconstruction_error"],
        "rank": int(np.linalg.matrix_rank(representation["features"])),
        "feature_budget": int(representation["features"].shape[1]),
        "readout_parameter_count": (
            representation["features"].shape[1] + int(bool(intercept))
        )
        * len(classes),
        "retained_train_samples": representation["retained_train_samples"],
        "model_state_bytes": representation["model_state_base_bytes"] + readout_bytes,
        "readout_state_bytes": readout_bytes,
        "intermediate_array_bytes_estimate": representation["intermediate_array_bytes_estimate"],
        "build_peak_tracemalloc_bytes": representation["build_peak_tracemalloc_bytes"],
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
        "test_feature_transform_time_seconds": representation["test_feature_transform_time_seconds"],
        "readout_solve_time_seconds": solve_time,
        "readout_validation_inference_time_seconds": inference_time,
        "readout_grid_solve_time_seconds": solve_time,
        "selected_readout_validation_inference_mean_seconds": inference_time,
        "selected_readout_test_inference_mean_seconds": None,
        "validation_prediction_mean_seconds": (
            representation["validation_feature_transform_time_seconds"] + inference_time
        ),
        "test_prediction_mean_seconds": None,
        "fit_time_without_oracle_selection_seconds": (
            representation["train_feature_construction_time_seconds"] + solve_time
        ),
        "fit_time_with_oracle_selection_seconds": (
            representation["train_feature_construction_time_seconds"]
            + solve_time
            + preprocessing_time
            + (oracle_selection_time if representation["requires_rbf_gamma_selection"] else 0.0)
        ),
        "requires_rbf_gamma_selection": representation["requires_rbf_gamma_selection"],
        "uses_train_labels_for_representation": representation[
            "uses_train_labels_for_representation"
        ],
        "feature_family": representation["feature_family"],
        "prototype_count": representation["prototype_count"],
        "prototype_train_exact_match_count": representation["prototype_train_exact_match_count"],
        "uses_iterative_parameter_optimization": False,
    }


def _test_metrics(scores, observed, labels, classes):
    residual_sum = float(np.sum((scores - observed) ** 2))
    total_sum = float(np.sum((observed - observed.mean(axis=0)) ** 2))
    predictions = classes[scores.argmax(axis=1)]
    return {
        "test_accuracy": float(np.mean(predictions == labels)),
        "test_rmse": float(np.sqrt(np.mean((scores - observed) ** 2))),
        "test_r2": 1.0 - residual_sum / total_sum if total_sum else 0.0,
    }


def _repeat_inference(representation, readout, intercept, partition, warmups, repeats):
    for _ in range(warmups):
        _predict_partition(representation, readout, intercept, partition)
    timings = []
    for _ in range(repeats):
        _, elapsed = _predict_partition(representation, readout, intercept, partition)
        timings.append(elapsed)
    return float(np.mean(timings))


def _kernel_readout_bytes(readout):
    arrays = [readout["dual"], readout["target_mean"]]
    if readout["column_mean"] is not None:
        arrays.append(readout["column_mean"])
    return _arrays_nbytes(*arrays) + 8


def _measure_peak(function):
    tracemalloc.start()
    try:
        result = function()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, int(peak)


def _arrays_nbytes(*arrays):
    return int(sum(np.asarray(array).nbytes for array in arrays if array is not None))


def summary(rows):
    return {
        metric: summarize_values([r[metric] for r in rows])
        for metric in METRICS
        if rows and all(r.get(metric) is not None for r in rows)
    }


def aggregate(rows, selected_rows, pair_specs):
    datasets = sorted({r["dataset"] for r in selected_rows})
    summaries = {}
    efficiency = {}
    pairs = {}
    for dataset in datasets:
        dataset_selected = [r for r in selected_rows if r["dataset"] == dataset]
        models = sorted({r["model"] for r in dataset_selected})
        summaries[dataset] = {
            model: summary([r for r in dataset_selected if r["model"] == model])
            for model in models
        }
        rbf_by_seed = {r["split_seed"]: r for r in dataset_selected if r["model"] == "rbf"}
        efficiency[dataset] = {}
        for model in models:
            group = [r for r in dataset_selected if r["model"] == model]
            if set(rbf_by_seed) != {r["split_seed"] for r in group}:
                continue
            efficiency[dataset][model] = {
                "test_accuracy_gap_to_rbf": summarize_values(
                    [rbf_by_seed[row["split_seed"]]["test_accuracy"] - row["test_accuracy"] for row in group]
                ),
                "model_state_bytes_ratio_to_rbf": summarize_values(
                    [
                        row["model_state_bytes"]
                        / rbf_by_seed[row["split_seed"]]["model_state_bytes"]
                        for row in group
                    ]
                ),
                "test_prediction_time_ratio_to_rbf": summarize_values(
                    [
                        row["test_prediction_mean_seconds"]
                        / rbf_by_seed[row["split_seed"]]["test_prediction_mean_seconds"]
                        for row in group
                    ]
                ),
            }
        for left, right in pair_specs:
            left_rows = {
                r["split_seed"]: r
                for r in dataset_selected
                if r["model"] == left
            }
            right_rows = {
                r["split_seed"]: r
                for r in dataset_selected
                if r["model"] == right
            }
            seeds = sorted(set(left_rows) & set(right_rows))
            if not seeds:
                continue
            pairs[f"{dataset}:{left}_minus_{right}"] = {
                metric: summarize_values(
                    [left_rows[seed][metric] - right_rows[seed][metric] for seed in seeds]
                )
                for metric in METRICS
                if all(
                    left_rows[seed].get(metric) is not None
                    and right_rows[seed].get(metric) is not None
                    for seed in seeds
                )
            }
    return {
        "selected_summary": summaries,
        "efficiency_summary": efficiency,
        "paired_differences": pairs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/dns05_fresh_confirmation_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/dns05_fresh_confirmation_v1.json"),
    )
    args = parser.parse_args()
    result = run(load_config(args.config))
    from importlib.metadata import version

    result["environment"] = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "packages": {p: version(p) for p in ["numpy", "scikit-learn"]},
    }
    result["command"] = subprocess.list2cmdline(
        [sys.executable, "-m", "experiments.run_dns05_confirmation", *sys.argv[1:]]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for dataset, models in result["selected_summary"].items():
        print(dataset)
        for model, metrics in models.items():
            print(model, metrics["validation_accuracy"], metrics["test_accuracy"])


if __name__ == "__main__":
    main()
