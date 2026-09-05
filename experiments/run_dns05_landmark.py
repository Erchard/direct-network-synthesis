"""Validation-only landmark kernel-map diagnostic; never evaluates test samples."""

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

import numpy as np

from dns.features import (
    Standardizer,
    deterministic_relu_projection,
    stratified_train_validation_test_split,
)
from dns.kernels import rbf_kernel
from dns.synthesis import DNS05CompiledFeatureClassifier, DNS05FeatureCompilerConfig
from dns.synthesis.linear_algebra import solve_primal_ridge
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
from experiments.run_dns05_readout import kernel_readout

EIGEN_CUTOFF = 1e-10


def farthest_first_indices(X, count):
    """Deterministic maximin landmark order in the given feature space."""
    X = np.asarray(X, dtype=float)
    if count <= 0:
        raise ValueError("count must be positive.")
    if count >= len(X):
        return np.arange(len(X), dtype=int)
    centroid = X.mean(axis=0)
    first = int(np.argmin(np.sum((X - centroid) ** 2, axis=1)))
    return _farthest_fill(X, count, [first])


def class_balanced_farthest_indices(X, y, count):
    """Allocate farthest-first landmarks across train classes, then fill globally."""
    X = np.asarray(X, dtype=float)
    labels = np.asarray(y)
    classes = np.unique(labels)
    base = count // len(classes)
    remainder = count % len(classes)
    selected: list[int] = []
    for offset, label in enumerate(classes):
        quota = base + int(offset < remainder)
        local = np.flatnonzero(labels == label)
        if quota == 0 or local.size == 0:
            continue
        chosen = farthest_first_indices(X[local], min(quota, local.size))
        selected.extend(int(local[index]) for index in chosen)
    return _farthest_fill(X, min(count, len(X)), selected)


def uniform_landmark_indices(n_samples, count, seed):
    if count <= 0:
        raise ValueError("count must be positive.")
    if count >= n_samples:
        return np.arange(n_samples, dtype=int)
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(n_samples, size=count, replace=False))


def nystrom_features(X, landmarks, gamma):
    basis_kernel = rbf_kernel(landmarks, gamma=gamma)
    inverse_root, landmark_rank = _inverse_square_root_psd(basis_kernel)
    return rbf_kernel(X, landmarks, gamma=gamma) @ inverse_root, landmark_rank


def random_fourier_pair(train, validation, count, gamma, seed):
    if count <= 0:
        raise ValueError("count must be positive.")
    rng = np.random.default_rng(seed)
    weights = rng.normal(scale=np.sqrt(2.0 * gamma), size=(train.shape[1], count))
    bias = rng.uniform(0.0, 2.0 * np.pi, size=count)
    return _rff_transform(train, weights, bias), _rff_transform(validation, weights, bias)


def evaluate_development(X_train, y_train, X_validation, y_validation, config, seed):
    """Only development arrays enter this function; no test argument exists."""
    start = time.perf_counter()
    scaler = Standardizer().fit(X_train)
    train, validation = scaler.transform(X_train), scaler.transform(X_validation)
    preprocessing_time = time.perf_counter() - start
    classes = np.unique(y_train)
    targets, observed = one_hot(y_train, classes), one_hot(y_validation, classes)
    selection = select_rbf_oracle(
        train,
        targets,
        validation,
        y_validation,
        classes,
        split_seed=seed,
        config=config,
    )
    start = time.perf_counter()
    kernel = rbf_kernel(train, gamma=selection.gamma)
    cross = rbf_kernel(validation, train, gamma=selection.gamma)
    kernel_time = time.perf_counter() - start

    representations = _anchor_representations(
        X_train,
        y_train,
        X_validation,
        train,
        validation,
        kernel,
        cross,
        selection.gamma,
        config,
    )
    representations.extend(
        _landmark_representations(
            train,
            y_train,
            validation,
            kernel,
            selection.gamma,
            seed,
            config,
        )
    )
    representations.append(
        {
            "name": "rbf",
            "features": kernel,
            "validation_features": cross,
            "kernel_reconstruction_error": 0.0,
            "representation_time_seconds": kernel_time,
            "retained_train_samples": len(train),
            "uses_train_labels_for_representation": False,
            "landmark_count": None,
            "landmark_rank": None,
            "feature_family": "exact_kernel",
        }
    )
    return (
        _score_representations(
            representations, targets, observed, y_validation, classes, config, seed
        ),
        {"oracle": asdict(selection), "preprocessing_seconds": preprocessing_time},
    )


METRICS = [
    "validation_accuracy",
    "validation_rmse",
    "validation_r2",
    "rank",
    "feature_budget",
    "readout_parameter_count",
    "retained_train_samples",
    "solve_time_seconds",
    "inference_time_seconds",
    "representation_time_seconds",
    "kernel_reconstruction_error",
]


def summary(rows):
    return {
        metric: summarize_values([r[metric] for r in rows])
        for metric in METRICS
        if all(r[metric] is not None for r in rows)
    }


def aggregate(rows, pair_specs):
    models = sorted({r["model"] for r in rows})
    settings = sorted({(r["alpha"], r["intercept"]) for r in rows})
    seeds = sorted({r["split_seed"] for r in rows})
    selected = []
    matched = {}
    pairs = {}
    for model in models:
        for seed in seeds:
            candidates = [r for r in rows if r["model"] == model and r["split_seed"] == seed]
            selected.append(
                min(
                    candidates,
                    key=lambda r: (-r["validation_accuracy"], r["alpha"], r["intercept"]),
                )
            )
        for alpha, intercept in settings:
            group = [
                r
                for r in rows
                if r["model"] == model and r["alpha"] == alpha and r["intercept"] == intercept
            ]
            matched[f"{model}/alpha={alpha}/intercept={intercept}"] = summary(group)
    for left, right in pair_specs:
        for setting in [None, *settings]:
            source = (
                selected
                if setting is None
                else [r for r in rows if (r["alpha"], r["intercept"]) == setting]
            )
            left_rows = {r["split_seed"]: r for r in source if r["model"] == left}
            right_rows = {r["split_seed"]: r for r in source if r["model"] == right}
            if set(left_rows) != set(seeds) or set(right_rows) != set(seeds):
                continue
            pairs[f"{left}_minus_{right}/{setting}"] = {
                metric: summarize_values(
                    [left_rows[split][metric] - right_rows[split][metric] for split in seeds]
                )
                for metric in METRICS
                if all(
                    left_rows[split][metric] is not None and right_rows[split][metric] is not None
                    for split in seeds
                )
            }
    return {
        "matched_summary": matched,
        "selected_rows": selected,
        "selected_summary": {m: summary([r for r in selected if r["model"] == m]) for m in models},
        "paired_differences": pairs,
    }


def run(config):
    if config.get("dataset", {}).get("name") != "sklearn_digits":
        raise ValueError("Only sklearn_digits is supported by this runner.")
    X, y = load_digits_dataset()
    rows, records = [], []
    for seed in config["splits"]["split_seeds"]:
        train, validation, excluded = stratified_train_validation_test_split(
            y,
            seed=seed,
            train_fraction=config["splits"]["train_fraction"],
            validation_fraction=config["splits"]["validation_fraction"],
        )
        split_rows, record = evaluate_development(
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
        rows.extend(split_rows)
        print(f"Completed landmark split {seed}", flush=True)
    return {
        "config": config,
        "commit_sha": get_commit_sha(),
        "git_status_short": get_git_status_short(),
        "rows": rows,
        "splits": records,
        "test_status": "not_evaluated",
        "dataset_sha256": hashlib.sha256(X.tobytes() + y.tobytes()).hexdigest(),
        **aggregate(rows, config["paired_models"]),
    }


def _anchor_representations(
    X_train,
    y_train,
    X_validation,
    train,
    validation,
    kernel,
    cross,
    gamma,
    config,
):
    count = config["compiled_feature_count"]
    start = time.perf_counter()
    compiler = DNS05CompiledFeatureClassifier(
        gamma=gamma,
        config=DNS05FeatureCompilerConfig(total_feature_count=count, block_count=1),
    ).fit(X_train, y_train)
    compiled_validation = compiler.transform(X_validation)
    compilation_time = time.perf_counter() - start
    start = time.perf_counter()
    basis = compiler.feature_map_.transform_columns(X_train, np.arange(count))
    basis_validation = compiler.feature_map_.transform_columns(X_validation, np.arange(count))
    basis_time = time.perf_counter() - start
    start = time.perf_counter()
    weights, bias = deterministic_relu_projection(
        n_features=train.shape[1],
        hidden_units=config["fixed_relu_hidden_units"],
        seed=config["landmark_seed"],
    )
    fixed = relu_features(train, weights, bias, True)
    fixed_validation = relu_features(validation, weights, bias, True)
    fixed_time = time.perf_counter() - start
    representations = [
        {
            "name": "linear",
            "features": train,
            "validation_features": validation,
            "kernel_reconstruction_error": None,
            "representation_time_seconds": 0.0,
            "retained_train_samples": 0,
            "uses_train_labels_for_representation": False,
            "landmark_count": None,
            "landmark_rank": None,
            "feature_family": "linear",
        },
        {
            "name": f"fixed_relu_{fixed.shape[1]}",
            "features": fixed,
            "validation_features": fixed_validation,
            "kernel_reconstruction_error": None,
            "representation_time_seconds": fixed_time,
            "retained_train_samples": 0,
            "uses_train_labels_for_representation": False,
            "landmark_count": None,
            "landmark_rank": None,
            "feature_family": "seeded_relu",
        },
        {
            "name": f"pca_relu_{count}",
            "features": basis,
            "validation_features": basis_validation,
            "kernel_reconstruction_error": None,
            "representation_time_seconds": basis_time,
            "retained_train_samples": 0,
            "uses_train_labels_for_representation": False,
            "landmark_count": None,
            "landmark_rank": None,
            "feature_family": "pca_quantile_relu",
        },
        {
            "name": f"compiled_{count}",
            "features": compiler.train_embedding_,
            "validation_features": compiled_validation,
            "kernel_reconstruction_error": compiler.kernel_reconstruction_error_,
            "representation_time_seconds": compilation_time,
            "retained_train_samples": 0,
            "uses_train_labels_for_representation": True,
            "landmark_count": None,
            "landmark_rank": None,
            "feature_family": "dns05_compiled",
        },
    ]
    representations.extend(_spectral_representations(kernel, cross, config["landmark_counts"]))
    return representations


def _spectral_representations(kernel, cross, counts):
    start = time.perf_counter()
    values, vectors = np.linalg.eigh(kernel)
    order = np.argsort(values)[::-1]
    values, vectors = values[order], vectors[:, order]
    threshold = EIGEN_CUTOFF * max(1.0, float(values.max()))
    spectral_time = time.perf_counter() - start
    representations = []
    for count in counts:
        indices = np.flatnonzero(values > threshold)[:count]
        features = vectors[:, indices] * np.sqrt(values[indices])
        validation = cross @ (vectors[:, indices] / np.sqrt(values[indices]))
        representations.append(
            {
                "name": f"spectral_{count}",
                "features": features,
                "validation_features": validation,
                "kernel_reconstruction_error": _relative_kernel_error(kernel, features),
                "representation_time_seconds": spectral_time,
                "retained_train_samples": len(kernel),
                "uses_train_labels_for_representation": False,
                "landmark_count": None,
                "landmark_rank": None,
                "feature_family": "spectral_oracle",
            }
        )
    return representations


def _landmark_representations(train, y_train, validation, kernel, gamma, split_seed, config):
    representations = []
    for count in config["landmark_counts"]:
        selection_specs = [
            (
                "nystrom_uniform",
                uniform_landmark_indices(
                    len(train),
                    count,
                    config["landmark_seed"] + 1009 * split_seed + count,
                ),
                False,
                "uniform",
            ),
            ("nystrom_farthest", farthest_first_indices(train, count), False, "farthest_first"),
            (
                "nystrom_class_farthest",
                class_balanced_farthest_indices(train, y_train, count),
                True,
                "class_balanced_farthest_first",
            ),
        ]
        for prefix, indices, uses_labels, selection_name in selection_specs:
            start = time.perf_counter()
            landmarks = train[indices]
            features, landmark_rank = nystrom_features(train, landmarks, gamma)
            validation_features, _ = nystrom_features(validation, landmarks, gamma)
            construction_time = time.perf_counter() - start
            representations.append(
                {
                    "name": f"{prefix}_{count}",
                    "features": features,
                    "validation_features": validation_features,
                    "kernel_reconstruction_error": _relative_kernel_error(kernel, features),
                    "representation_time_seconds": construction_time,
                    "retained_train_samples": len(indices),
                    "uses_train_labels_for_representation": uses_labels,
                    "landmark_count": len(indices),
                    "landmark_rank": landmark_rank,
                    "feature_family": "nystrom",
                    "landmark_selection": selection_name,
                }
            )
        start = time.perf_counter()
        features, validation_features = random_fourier_pair(
            train,
            validation,
            count,
            gamma,
            config["rff_seed"] + 1009 * split_seed + count,
        )
        construction_time = time.perf_counter() - start
        representations.append(
            {
                "name": f"rff_{count}",
                "features": features,
                "validation_features": validation_features,
                "kernel_reconstruction_error": _relative_kernel_error(kernel, features),
                "representation_time_seconds": construction_time,
                "retained_train_samples": 0,
                "uses_train_labels_for_representation": False,
                "landmark_count": None,
                "landmark_rank": None,
                "feature_family": "random_fourier",
            }
        )
    return representations


def _score_representations(
    representations,
    targets,
    observed,
    y_validation,
    classes,
    config,
    split_seed,
):
    rows = []
    for representation in representations:
        name = representation["name"]
        features = representation["features"]
        validation_features = representation["validation_features"]
        rank = int(np.linalg.matrix_rank(features))
        for alpha in config["alphas"]:
            for intercept in config["intercepts"]:
                if name == "rbf":
                    scores, solve_time, inference_time = kernel_readout(
                        features,
                        targets,
                        validation_features,
                        alpha,
                        intercept,
                    )
                else:
                    start = time.perf_counter()
                    readout = solve_primal_ridge(
                        features,
                        targets,
                        alpha=alpha,
                        fit_intercept=intercept,
                    )
                    solve_time = time.perf_counter() - start
                    design = (
                        np.column_stack([np.ones(len(validation_features)), validation_features])
                        if intercept
                        else validation_features
                    )
                    start = time.perf_counter()
                    scores = design @ readout
                    inference_time = time.perf_counter() - start
                residual_sum = float(np.sum((scores - observed) ** 2))
                total_sum = float(np.sum((observed - observed.mean(axis=0)) ** 2))
                rows.append(
                    {
                        "model": name,
                        "split_seed": split_seed,
                        "alpha": alpha,
                        "intercept": intercept,
                        "validation_accuracy": float(
                            np.mean(classes[scores.argmax(axis=1)] == y_validation)
                        ),
                        "validation_rmse": float(np.sqrt(np.mean((scores - observed) ** 2))),
                        "validation_r2": 1.0 - residual_sum / total_sum,
                        "test_accuracy": None,
                        "test_rmse": None,
                        "test_r2": None,
                        "test_status": "not_evaluated",
                        "kernel_reconstruction_error": representation[
                            "kernel_reconstruction_error"
                        ],
                        "rank": rank,
                        "feature_budget": features.shape[1],
                        "readout_parameter_count": (features.shape[1] + int(intercept))
                        * len(classes),
                        "retained_train_samples": representation["retained_train_samples"],
                        "solve_time_seconds": solve_time,
                        "inference_time_seconds": inference_time,
                        "representation_time_seconds": representation[
                            "representation_time_seconds"
                        ],
                        "feature_family": representation["feature_family"],
                        "landmark_count": representation["landmark_count"],
                        "landmark_rank": representation["landmark_rank"],
                        "landmark_selection": representation.get("landmark_selection"),
                        "uses_train_labels_for_representation": representation[
                            "uses_train_labels_for_representation"
                        ],
                        "uses_iterative_parameter_optimization": False,
                    }
                )
    return rows


def _farthest_fill(X, count, initial):
    selected = []
    seen = set()
    for index in initial:
        if 0 <= index < len(X) and index not in seen:
            selected.append(int(index))
            seen.add(int(index))
        if len(selected) == count:
            return np.asarray(selected, dtype=int)
    if not selected:
        centroid = X.mean(axis=0)
        first = int(np.argmin(np.sum((X - centroid) ** 2, axis=1)))
        selected.append(first)
        seen.add(first)
    min_distances = np.full(len(X), np.inf, dtype=float)
    for index in selected:
        min_distances = np.minimum(min_distances, np.sum((X - X[index]) ** 2, axis=1))
    while len(selected) < count:
        scores = min_distances.copy()
        scores[list(seen)] = -np.inf
        index = int(np.argmax(scores))
        selected.append(index)
        seen.add(index)
        min_distances = np.minimum(min_distances, np.sum((X - X[index]) ** 2, axis=1))
    return np.asarray(selected, dtype=int)


def _inverse_square_root_psd(matrix):
    symmetric = 0.5 * (matrix + matrix.T)
    values, vectors = np.linalg.eigh(symmetric)
    threshold = EIGEN_CUTOFF * max(1.0, float(values.max()))
    keep = values > threshold
    scale = np.zeros_like(values)
    scale[keep] = 1.0 / np.sqrt(values[keep])
    return (vectors * scale) @ vectors.T, int(np.count_nonzero(keep))


def _rff_transform(X, weights, bias):
    return np.sqrt(2.0 / weights.shape[1]) * np.cos(X @ weights + bias)


def _relative_kernel_error(kernel, features):
    return float(np.linalg.norm(kernel - features @ features.T) / np.linalg.norm(kernel))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/dns05_landmark_digits.json"))
    parser.add_argument("--output", type=Path, default=Path("results/dns05_landmark_digits.json"))
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
        [sys.executable, "-m", "experiments.run_dns05_landmark", *sys.argv[1:]]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for model, metrics in result["selected_summary"].items():
        print(model, metrics["validation_accuracy"])


if __name__ == "__main__":
    main()
