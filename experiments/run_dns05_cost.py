"""Validation-only cost accounting for compact DNS05/RBF representations."""

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

import numpy as np

from dns.features import (
    Standardizer,
    deterministic_relu_projection,
    stratified_train_validation_test_split,
)
from dns.kernels import rbf_kernel
from dns.synthesis import DNS05CompiledFeatureClassifier, DNS05FeatureCompilerConfig
from dns.synthesis.dns05_kernel_compiler import _PCAQuantileReLUFeatureMap
from dns.synthesis.linear_algebra import solve_primal_ridge, stable_solve
from experiments.run_dns05_depth_width import (
    get_commit_sha,
    get_git_status_short,
    load_config,
    load_digits_dataset,
    one_hot,
    relu_features,
    select_rbf_oracle,
    summarize_values,
)
from experiments.run_dns05_landmark import (
    EIGEN_CUTOFF,
    _inverse_square_root_psd,
    _relative_kernel_error,
    _rff_transform,
    class_balanced_farthest_indices,
    farthest_first_indices,
    uniform_landmark_indices,
)

METRICS = [
    "validation_accuracy",
    "validation_rmse",
    "validation_r2",
    "rank",
    "feature_budget",
    "readout_parameter_count",
    "retained_train_samples",
    "model_state_bytes",
    "intermediate_array_bytes_estimate",
    "build_peak_tracemalloc_bytes",
    "train_feature_construction_time_seconds",
    "validation_feature_transform_time_seconds",
    "readout_grid_solve_time_seconds",
    "selected_readout_inference_mean_seconds",
    "validation_prediction_mean_seconds",
    "fit_time_without_oracle_selection_seconds",
    "fit_time_with_oracle_selection_seconds",
    "kernel_reconstruction_error",
]


def evaluate_development(X_train, y_train, X_validation, y_validation, config, seed):
    """Only development arrays enter this function; no test argument exists."""
    preprocessing_start = time.perf_counter()
    scaler = Standardizer().fit(X_train)
    train, validation = scaler.transform(X_train), scaler.transform(X_validation)
    preprocessing_time = time.perf_counter() - preprocessing_start
    classes = np.unique(y_train)
    targets, observed = one_hot(y_train, classes), one_hot(y_validation, classes)

    oracle_start = time.perf_counter()
    selection = select_rbf_oracle(
        train,
        targets,
        validation,
        y_validation,
        classes,
        split_seed=seed,
        config=config,
    )
    oracle_selection_time = time.perf_counter() - oracle_start

    representations = _build_representations(
        X_train,
        y_train,
        X_validation,
        train,
        validation,
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
    rows, selected = _score_representations(
        [
            representation
            for representation in representations
            if representation["name"] in requested
        ],
        targets,
        observed,
        y_validation,
        classes,
        preprocessing_time,
        oracle_selection_time,
        config,
        seed,
    )
    return (
        {"rows": rows, "selected_rows": selected},
        {
            "oracle": asdict(selection),
            "preprocessing_seconds": preprocessing_time,
            "oracle_selection_seconds": oracle_selection_time,
        },
    )


def summary(rows):
    return {
        metric: summarize_values([r[metric] for r in rows])
        for metric in METRICS
        if all(r[metric] is not None for r in rows)
    }


def aggregate(rows, selected_rows, pair_specs):
    models = sorted({r["model"] for r in selected_rows})
    seeds = sorted({r["split_seed"] for r in selected_rows})
    selected_summary = {
        model: summary([r for r in selected_rows if r["model"] == model]) for model in models
    }
    rbf_by_seed = {r["split_seed"]: r for r in selected_rows if r["model"] == "rbf"}
    efficiency = {}
    for model in models:
        group = [r for r in selected_rows if r["model"] == model]
        if set(rbf_by_seed) == {r["split_seed"] for r in group}:
            gaps = [
                rbf_by_seed[row["split_seed"]]["validation_accuracy"] - row["validation_accuracy"]
                for row in group
            ]
            byte_ratios = [
                row["model_state_bytes"] / rbf_by_seed[row["split_seed"]]["model_state_bytes"]
                for row in group
            ]
            prediction_ratios = [
                row["validation_prediction_mean_seconds"]
                / rbf_by_seed[row["split_seed"]]["validation_prediction_mean_seconds"]
                for row in group
            ]
            efficiency[model] = {
                "accuracy_gap_to_rbf": summarize_values(gaps),
                "model_state_bytes_ratio_to_rbf": summarize_values(byte_ratios),
                "validation_prediction_time_ratio_to_rbf": summarize_values(prediction_ratios),
            }
    pairs = {}
    for left, right in pair_specs:
        left_rows = {r["split_seed"]: r for r in selected_rows if r["model"] == left}
        right_rows = {r["split_seed"]: r for r in selected_rows if r["model"] == right}
        if set(left_rows) != set(seeds) or set(right_rows) != set(seeds):
            continue
        pairs[f"{left}_minus_{right}"] = {
            metric: summarize_values(
                [left_rows[seed][metric] - right_rows[seed][metric] for seed in seeds]
            )
            for metric in METRICS
            if all(
                left_rows[seed][metric] is not None and right_rows[seed][metric] is not None
                for seed in seeds
            )
        }
    return {
        "selected_summary": selected_summary,
        "efficiency_summary": efficiency,
        "paired_differences": pairs,
    }


def run(config):
    if config.get("dataset", {}).get("name") != "sklearn_digits":
        raise ValueError("Only sklearn_digits is supported by this runner.")
    X, y = load_digits_dataset()
    rows, selected_rows, records = [], [], []
    for seed in config["splits"]["split_seeds"]:
        train, validation, excluded = stratified_train_validation_test_split(
            y,
            seed=seed,
            train_fraction=config["splits"]["train_fraction"],
            validation_fraction=config["splits"]["validation_fraction"],
        )
        split_result, record = evaluate_development(
            X[train],
            y[train],
            X[validation],
            y[validation],
            config,
            seed,
        )
        record.update(
            {
                "seed": seed,
                "train_indices": train.tolist(),
                "validation_indices": validation.tolist(),
                "excluded_indices": excluded.tolist(),
            }
        )
        records.append(record)
        rows.extend(split_result["rows"])
        selected_rows.extend(split_result["selected_rows"])
        print(f"Completed cost split {seed}", flush=True)
    return {
        "config": config,
        "commit_sha": get_commit_sha(),
        "git_status_short": get_git_status_short(),
        "rows": rows,
        "selected_rows": selected_rows,
        "splits": records,
        "test_status": "not_evaluated",
        "dataset_sha256": hashlib.sha256(X.tobytes() + y.tobytes()).hexdigest(),
        **aggregate(rows, selected_rows, config["paired_models"]),
    }


def _build_representations(
    X_train, y_train, X_validation, train, validation, gamma, scaler, config, seed
):
    representations = []
    standardizer_bytes = _arrays_nbytes(scaler.mean_, scaler.scale_)
    representations.append(
        {
            "name": "linear",
            "features": train,
            "validation_features": validation,
            "predictor": _linear_predictor,
            "kernel_reconstruction_error": None,
            "train_feature_construction_time_seconds": 0.0,
            "validation_feature_transform_time_seconds": 0.0,
            "model_state_base_bytes": standardizer_bytes,
            "intermediate_array_bytes_estimate": train.nbytes + validation.nbytes,
            "build_peak_tracemalloc_bytes": 0,
            "retained_train_samples": 0,
            "requires_rbf_gamma_selection": False,
            "uses_train_labels_for_representation": False,
            "feature_family": "linear",
        }
    )
    representations.extend(
        [
            _fixed_relu_representation(train, validation, scaler, config),
            _pca_relu_representation(X_train, X_validation, scaler, config),
            _compiled_representation(X_train, y_train, X_validation, scaler, gamma, config),
        ]
    )
    for count in config["landmark_counts"]:
        representations.extend(
            [
                _rff_representation(train, validation, scaler, gamma, config, seed, count),
                _nystrom_representation(
                    train,
                    y_train,
                    validation,
                    scaler,
                    gamma,
                    config,
                    seed,
                    count,
                    "uniform",
                ),
                _nystrom_representation(
                    train,
                    y_train,
                    validation,
                    scaler,
                    gamma,
                    config,
                    seed,
                    count,
                    "farthest",
                ),
                _nystrom_representation(
                    train,
                    y_train,
                    validation,
                    scaler,
                    gamma,
                    config,
                    seed,
                    count,
                    "class_farthest",
                ),
                _spectral_representation(train, validation, scaler, gamma, count),
            ]
        )
    representations.append(_rbf_representation(train, validation, scaler, gamma))
    return representations


def _fixed_relu_representation(train, validation, scaler, config):
    def build():
        weights, bias = deterministic_relu_projection(
            n_features=train.shape[1],
            hidden_units=config["fixed_relu_hidden_units"],
            seed=config["fixed_relu_seed"],
        )
        start = time.perf_counter()
        features = relu_features(train, weights, bias, True)
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_features = relu_features(validation, weights, bias, True)
        validation_time = time.perf_counter() - start
        return features, validation_features, weights, bias, train_time, validation_time

    (features, validation_features, weights, bias, train_time, validation_time), peak = (
        _measure_peak(build)
    )
    return {
        "name": f"fixed_relu_{features.shape[1]}",
        "features": features,
        "validation_features": validation_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": None,
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": validation_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, weights, bias),
        "intermediate_array_bytes_estimate": features.nbytes + validation_features.nbytes,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": 0,
        "requires_rbf_gamma_selection": False,
        "uses_train_labels_for_representation": False,
        "feature_family": "seeded_relu",
    }


def _pca_relu_representation(X_train, X_validation, scaler, config):
    count = config["compiled_feature_count"]

    def build():
        start = time.perf_counter()
        feature_map = _PCAQuantileReLUFeatureMap(
            feature_count=count,
            quantile_min=0.1,
            quantile_max=0.9,
            quantile_count=5,
        ).fit(X_train)
        features = feature_map.transform_columns(X_train, np.arange(count))
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_features = feature_map.transform_columns(X_validation, np.arange(count))
        validation_time = time.perf_counter() - start
        return features, validation_features, feature_map, train_time, validation_time

    (features, validation_features, feature_map, train_time, validation_time), peak = _measure_peak(
        build
    )
    return {
        "name": f"pca_relu_{count}",
        "features": features,
        "validation_features": validation_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": None,
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": validation_time,
        "model_state_base_bytes": _arrays_nbytes(
            feature_map.standardizer_.mean_,
            feature_map.standardizer_.scale_,
            feature_map.weights_,
            feature_map.thresholds_,
        ),
        "intermediate_array_bytes_estimate": features.nbytes + validation_features.nbytes,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": 0,
        "requires_rbf_gamma_selection": False,
        "uses_train_labels_for_representation": False,
        "feature_family": "pca_quantile_relu",
    }


def _compiled_representation(X_train, y_train, X_validation, scaler, gamma, config):
    count = config["compiled_feature_count"]

    def build():
        start = time.perf_counter()
        compiler = DNS05CompiledFeatureClassifier(
            gamma=gamma,
            config=DNS05FeatureCompilerConfig(total_feature_count=count, block_count=1),
        ).fit(X_train, y_train)
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_features = compiler.transform(X_validation)
        validation_time = time.perf_counter() - start
        return compiler, validation_features, train_time, validation_time

    (compiler, validation_features, train_time, validation_time), peak = _measure_peak(build)
    state_arrays = [
        compiler.feature_map_.standardizer_.mean_,
        compiler.feature_map_.standardizer_.scale_,
        compiler.feature_map_.weights_,
        compiler.feature_map_.thresholds_,
        *(block.projection_weights for block in compiler.blocks_),
    ]
    return {
        "name": f"compiled_{count}",
        "features": compiler.train_embedding_,
        "validation_features": validation_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": compiler.kernel_reconstruction_error_,
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": validation_time,
        "model_state_base_bytes": _arrays_nbytes(*state_arrays),
        "intermediate_array_bytes_estimate": (
            compiler.train_embedding_.nbytes
            + validation_features.nbytes
            + X_train.shape[0] * X_train.shape[0] * 8
        ),
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": 0,
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": False,
        "feature_family": "dns05_compiled",
    }


def _rff_representation(train, validation, scaler, gamma, config, seed, count):
    def build():
        rng = np.random.default_rng(config["rff_seed"] + 1009 * seed + count)
        weights = rng.normal(scale=np.sqrt(2.0 * gamma), size=(train.shape[1], count))
        bias = rng.uniform(0.0, 2.0 * np.pi, size=count)
        start = time.perf_counter()
        features = _rff_transform(train, weights, bias)
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_features = _rff_transform(validation, weights, bias)
        validation_time = time.perf_counter() - start
        return features, validation_features, weights, bias, train_time, validation_time

    (features, validation_features, weights, bias, train_time, validation_time), peak = (
        _measure_peak(build)
    )
    return {
        "name": f"rff_{count}",
        "features": features,
        "validation_features": validation_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": _relative_kernel_error(
            rbf_kernel(train, gamma=gamma), features
        ),
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": validation_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, weights, bias),
        "intermediate_array_bytes_estimate": features.nbytes + validation_features.nbytes,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": 0,
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": False,
        "feature_family": "random_fourier",
    }


def _nystrom_representation(
    train, y_train, validation, scaler, gamma, config, seed, count, strategy
):
    def build():
        start = time.perf_counter()
        if strategy == "uniform":
            indices = uniform_landmark_indices(
                len(train),
                count,
                config["landmark_seed"] + 1009 * seed + count,
            )
        elif strategy == "farthest":
            indices = farthest_first_indices(train, count)
        elif strategy == "class_farthest":
            indices = class_balanced_farthest_indices(train, y_train, count)
        else:
            raise ValueError(f"Unknown Nystrom landmark strategy: {strategy}")
        selection_time = time.perf_counter() - start
        landmarks = train[indices]
        start = time.perf_counter()
        landmark_kernel = rbf_kernel(landmarks, gamma=gamma)
        inverse_root, landmark_rank = _inverse_square_root_psd(landmark_kernel)
        normalize_time = time.perf_counter() - start
        start = time.perf_counter()
        train_to_landmarks = rbf_kernel(train, landmarks, gamma=gamma)
        features = train_to_landmarks @ inverse_root
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        validation_to_landmarks = rbf_kernel(validation, landmarks, gamma=gamma)
        validation_features = validation_to_landmarks @ inverse_root
        validation_time = time.perf_counter() - start
        return (
            features,
            validation_features,
            landmarks,
            inverse_root,
            landmark_rank,
            selection_time,
            normalize_time,
            train_time,
            validation_time,
            train_to_landmarks.nbytes + landmark_kernel.nbytes + validation_to_landmarks.nbytes,
        )

    (
        (
            features,
            validation_features,
            landmarks,
            inverse_root,
            landmark_rank,
            selection_time,
            normalize_time,
            train_time,
            validation_time,
            intermediate_bytes,
        ),
        peak,
    ) = _measure_peak(build)
    name = f"nystrom_{strategy}_{count}"
    return {
        "name": name,
        "features": features,
        "validation_features": validation_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": _relative_kernel_error(
            rbf_kernel(train, gamma=gamma), features
        ),
        "train_feature_construction_time_seconds": selection_time + normalize_time + train_time,
        "validation_feature_transform_time_seconds": validation_time,
        "model_state_base_bytes": _arrays_nbytes(
            scaler.mean_, scaler.scale_, landmarks, inverse_root
        ),
        "intermediate_array_bytes_estimate": intermediate_bytes,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": len(landmarks),
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": strategy == "class_farthest",
        "feature_family": "nystrom",
        "landmark_rank": landmark_rank,
        "landmark_selection": strategy,
    }


def _spectral_representation(train, validation, scaler, gamma, count):
    def build():
        start = time.perf_counter()
        kernel = rbf_kernel(train, gamma=gamma)
        kernel_time = time.perf_counter() - start
        start = time.perf_counter()
        values, vectors = np.linalg.eigh(kernel)
        order = np.argsort(values)[::-1]
        values, vectors = values[order], vectors[:, order]
        threshold = EIGEN_CUTOFF * max(1.0, float(values.max()))
        indices = np.flatnonzero(values > threshold)[:count]
        extension = vectors[:, indices] / np.sqrt(values[indices])
        features = vectors[:, indices] * np.sqrt(values[indices])
        eigen_time = time.perf_counter() - start
        start = time.perf_counter()
        cross = rbf_kernel(validation, train, gamma=gamma)
        validation_features = cross @ extension
        validation_time = time.perf_counter() - start
        return (
            features,
            validation_features,
            kernel,
            extension,
            kernel_time,
            eigen_time,
            validation_time,
            kernel.nbytes + values.nbytes + vectors.nbytes + cross.nbytes,
        )

    (
        (
            features,
            validation_features,
            kernel,
            extension,
            kernel_time,
            eigen_time,
            validation_time,
            intermediate_bytes,
        ),
        peak,
    ) = _measure_peak(build)
    return {
        "name": f"spectral_{count}",
        "features": features,
        "validation_features": validation_features,
        "predictor": _linear_predictor,
        "kernel_reconstruction_error": _relative_kernel_error(kernel, features),
        "train_feature_construction_time_seconds": kernel_time + eigen_time,
        "validation_feature_transform_time_seconds": validation_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, train, extension),
        "intermediate_array_bytes_estimate": intermediate_bytes,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": len(train),
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": False,
        "feature_family": "spectral_oracle",
    }


def _rbf_representation(train, validation, scaler, gamma):
    def build():
        start = time.perf_counter()
        kernel = rbf_kernel(train, gamma=gamma)
        train_time = time.perf_counter() - start
        start = time.perf_counter()
        cross = rbf_kernel(validation, train, gamma=gamma)
        validation_time = time.perf_counter() - start
        return kernel, cross, train_time, validation_time

    (kernel, cross, train_time, validation_time), peak = _measure_peak(build)
    return {
        "name": "rbf",
        "features": kernel,
        "validation_features": cross,
        "predictor": _kernel_predictor,
        "kernel_reconstruction_error": 0.0,
        "train_feature_construction_time_seconds": train_time,
        "validation_feature_transform_time_seconds": validation_time,
        "model_state_base_bytes": _arrays_nbytes(scaler.mean_, scaler.scale_, train),
        "intermediate_array_bytes_estimate": kernel.nbytes + cross.nbytes,
        "build_peak_tracemalloc_bytes": peak,
        "retained_train_samples": len(train),
        "requires_rbf_gamma_selection": True,
        "uses_train_labels_for_representation": False,
        "feature_family": "exact_kernel",
    }


def _score_representations(
    representations,
    targets,
    observed,
    y_validation,
    classes,
    preprocessing_time,
    oracle_selection_time,
    config,
    seed,
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
                ](
                    representation,
                    targets,
                    alpha,
                    intercept,
                )
                row = _row_from_scores(
                    representation,
                    scores,
                    observed,
                    y_validation,
                    classes,
                    alpha,
                    intercept,
                    solve_time,
                    inference_time,
                    readout_bytes,
                    preprocessing_time,
                    oracle_selection_time,
                    0.0,
                    seed,
                )
                rows.append(row)
                candidates.append((row, scores, readout, readout_bytes))
                grid_solve_time += solve_time
        selected_row, _, selected_readout, selected_readout_bytes = min(
            candidates,
            key=lambda item: (
                -item[0]["validation_accuracy"],
                item[0]["alpha"],
                item[0]["intercept"],
            ),
        )
        repeated_inference = _repeat_inference(
            representation,
            selected_readout,
            selected_row["intercept"],
            config["prediction_warmups"],
            config["prediction_repeats"],
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
                "selection_status": "validation_selected",
                "readout_grid_solve_time_seconds": grid_solve_time,
                "selected_readout_inference_mean_seconds": repeated_inference,
                "validation_prediction_mean_seconds": (
                    representation["validation_feature_transform_time_seconds"] + repeated_inference
                ),
                "fit_time_without_oracle_selection_seconds": fit_without_oracle,
                "fit_time_with_oracle_selection_seconds": fit_with_oracle,
                "model_state_bytes": representation["model_state_base_bytes"]
                + selected_readout_bytes,
            }
        )
    return rows, selected_rows


def _linear_predictor(representation, targets, alpha, intercept):
    features = representation["features"]
    validation_features = representation["validation_features"]
    start = time.perf_counter()
    readout = solve_primal_ridge(features, targets, alpha=alpha, fit_intercept=intercept)
    solve_time = time.perf_counter() - start
    start = time.perf_counter()
    scores = _predict_linear(validation_features, readout, intercept)
    inference_time = time.perf_counter() - start
    return scores, readout, solve_time, inference_time, readout.nbytes


def _kernel_predictor(representation, targets, alpha, intercept):
    kernel = representation["features"]
    cross = representation["validation_features"]
    start = time.perf_counter()
    readout = _fit_kernel_readout(kernel, targets, alpha, intercept)
    solve_time = time.perf_counter() - start
    start = time.perf_counter()
    scores = _predict_kernel(cross, readout)
    inference_time = time.perf_counter() - start
    return scores, readout, solve_time, inference_time, _kernel_readout_bytes(readout)


def _row_from_scores(
    representation,
    scores,
    observed,
    y_validation,
    classes,
    alpha,
    intercept,
    solve_time,
    inference_time,
    readout_bytes,
    preprocessing_time,
    oracle_selection_time,
    grid_solve_time,
    seed,
):
    residual_sum = float(np.sum((scores - observed) ** 2))
    total_sum = float(np.sum((observed - observed.mean(axis=0)) ** 2))
    predictions = classes[scores.argmax(axis=1)]
    return {
        "model": representation["name"],
        "split_seed": seed,
        "alpha": alpha,
        "intercept": intercept,
        "validation_accuracy": float(np.mean(predictions == y_validation)),
        "validation_rmse": float(np.sqrt(np.mean((scores - observed) ** 2))),
        "validation_r2": 1.0 - residual_sum / total_sum,
        "test_accuracy": None,
        "test_rmse": None,
        "test_r2": None,
        "test_status": "not_evaluated",
        "kernel_reconstruction_error": representation["kernel_reconstruction_error"],
        "rank": int(np.linalg.matrix_rank(representation["features"])),
        "feature_budget": representation["features"].shape[1],
        "readout_parameter_count": (representation["features"].shape[1] + int(intercept))
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
        "readout_solve_time_seconds": solve_time,
        "readout_inference_time_seconds": inference_time,
        "readout_grid_solve_time_seconds": grid_solve_time,
        "selected_readout_inference_mean_seconds": inference_time,
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
            + (oracle_selection_time if representation["requires_rbf_gamma_selection"] else 0.0)
        ),
        "requires_rbf_gamma_selection": representation["requires_rbf_gamma_selection"],
        "uses_train_labels_for_representation": representation[
            "uses_train_labels_for_representation"
        ],
        "feature_family": representation["feature_family"],
        "uses_iterative_parameter_optimization": False,
    }


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


def _repeat_inference(representation, readout, intercept, warmups, repeats):
    predictor = _predict_kernel if representation["name"] == "rbf" else _predict_linear
    features = representation["validation_features"]
    for _ in range(warmups):
        predictor(features, readout, intercept) if predictor is _predict_linear else predictor(
            features, readout
        )
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        predictor(features, readout, intercept) if predictor is _predict_linear else predictor(
            features, readout
        )
        timings.append(time.perf_counter() - start)
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/dns05_cost_digits.json"))
    parser.add_argument("--output", type=Path, default=Path("results/dns05_cost_digits.json"))
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
        [sys.executable, "-m", "experiments.run_dns05_cost", *sys.argv[1:]]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for model, metrics in result["selected_summary"].items():
        accuracy = metrics["validation_accuracy"]
        bytes_ = metrics["model_state_bytes"]
        prediction = metrics["validation_prediction_mean_seconds"]
        print(model, accuracy, bytes_, prediction)


if __name__ == "__main__":
    main()
