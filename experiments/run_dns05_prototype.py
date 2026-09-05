"""Validation-only synthetic prototype diagnostic for DNS05 geometry compression."""

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

from dns.features import Standardizer, stratified_train_validation_test_split
from dns.kernels import rbf_kernel
from experiments.run_dns05_depth_width import (
    get_commit_sha,
    get_git_status_short,
    load_config,
    load_digits_dataset,
    one_hot,
    select_rbf_oracle,
    summarize_values,
)
from experiments.run_dns05_landmark import (
    _anchor_representations,
    _landmark_representations,
    _score_representations,
    nystrom_features,
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
    "prototype_count",
    "prototype_train_exact_match_count",
]


def global_pca_prototypes(X, count, quantiles):
    """Synthetic centers from global PCA axes and projection quantiles."""
    X = np.asarray(X, dtype=float)
    if count <= 0:
        raise ValueError("count must be positive.")
    components = _oriented_pca_components(X)
    center = X.mean(axis=0)
    projections = (X - center) @ components.T
    centers = np.empty((count, X.shape[1]), dtype=float)
    for index in range(count):
        component_index = index % components.shape[0]
        quantile = quantiles[(index // components.shape[0]) % len(quantiles)]
        offset = float(np.quantile(projections[:, component_index], quantile))
        centers[index] = center + offset * components[component_index]
    return centers


def class_pca_prototypes(X, y, count, quantiles):
    """Synthetic class-local centers; stores no actual train samples."""
    X = np.asarray(X, dtype=float)
    labels = np.asarray(y)
    classes = np.unique(labels)
    quotas = _balanced_quotas(count, len(classes))
    centers = []
    for class_index, label in enumerate(classes):
        local = X[labels == label]
        quota = min(quotas[class_index], count - len(centers))
        if quota <= 0:
            continue
        class_mean = local.mean(axis=0)
        centers.append(class_mean)
        if quota == 1:
            continue
        components = _oriented_pca_components(local)
        projections = (local - class_mean) @ components.T
        for offset_index in range(quota - 1):
            component_index = offset_index % components.shape[0]
            quantile = quantiles[(offset_index // components.shape[0]) % len(quantiles)]
            offset = float(np.quantile(projections[:, component_index], quantile))
            centers.append(class_mean + offset * components[component_index])
    if len(centers) < count:
        centers.extend(global_pca_prototypes(X, count - len(centers), quantiles))
    return np.asarray(centers[:count], dtype=float)


def class_dipole_prototypes(X, y, count, quantiles, shift_fraction, gamma):
    """Class-local synthetic centers shifted toward and away from nearest rival classes."""
    X = np.asarray(X, dtype=float)
    labels = np.asarray(y)
    if count <= 0:
        raise ValueError("count must be positive.")
    if not 0.0 <= shift_fraction <= 1.0:
        raise ValueError("shift_fraction must be between 0 and 1.")
    classes = np.unique(labels)
    quotas = _balanced_quotas(count, len(classes))
    rivals = _nearest_rival_labels(X, labels, classes, gamma)
    centers = []
    for class_index, label in enumerate(classes):
        local = X[labels == label]
        quota = min(quotas[class_index], count - len(centers))
        if quota <= 0:
            continue
        class_mean = local.mean(axis=0)
        centers.append(class_mean)
        if quota == 1:
            continue
        rival_mean = X[labels == rivals[label]].mean(axis=0)
        boundary_vector = rival_mean - class_mean
        if float(np.linalg.norm(boundary_vector)) <= 1e-12:
            boundary_vector = _oriented_pca_components(local)[0]
        boundary_shift = shift_fraction * boundary_vector
        components = _oriented_pca_components(local)
        projections = (local - class_mean) @ components.T
        for offset_index in range(quota - 1):
            pair_index = offset_index // 2
            component_index = pair_index % components.shape[0]
            quantile = quantiles[(pair_index // components.shape[0]) % len(quantiles)]
            offset = float(np.quantile(projections[:, component_index], quantile))
            polarity = 1.0 if offset_index % 2 == 0 else -1.0
            centers.append(
                class_mean
                + offset * components[component_index]
                + polarity * boundary_shift
            )
    if len(centers) < count:
        centers.extend(global_pca_prototypes(X, count - len(centers), quantiles))
    return np.asarray(centers[:count], dtype=float)


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
    representations.extend(
        _prototype_representations(
            train,
            y_train,
            validation,
            kernel,
            selection.gamma,
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
            "prototype_count": None,
            "prototype_train_exact_match_count": None,
        }
    )
    rows = _score_representations(
        representations,
        targets,
        observed,
        y_validation,
        classes,
        config,
        seed,
    )
    _attach_prototype_metadata(rows, representations)
    return rows, {"oracle": asdict(selection), "preprocessing_seconds": preprocessing_time}


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
        print(f"Completed prototype split {seed}", flush=True)
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


def summary(rows):
    return {
        metric: summarize_values([r[metric] for r in rows])
        for metric in METRICS
        if all(r.get(metric) is not None for r in rows)
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
                    left_rows[split].get(metric) is not None
                    and right_rows[split].get(metric) is not None
                    for split in seeds
                )
            }
    return {
        "matched_summary": matched,
        "selected_rows": selected,
        "selected_summary": {m: summary([r for r in selected if r["model"] == m]) for m in models},
        "paired_differences": pairs,
    }


def _prototype_representations(train, y_train, validation, kernel, gamma, config):
    representations = []
    quantiles = np.asarray(config["prototype_quantiles"], dtype=float)
    for count in config["landmark_counts"]:
        families = [
            ("prototype_global_pca", global_pca_prototypes(train, count, quantiles), False),
            ("prototype_class_pca", class_pca_prototypes(train, y_train, count, quantiles), True),
        ]
        if config.get("include_dipole_prototypes", False):
            families.append(
                (
                    "prototype_class_dipole",
                    class_dipole_prototypes(
                        train,
                        y_train,
                        count,
                        quantiles,
                        float(config["dipole_shift_fraction"]),
                        gamma,
                    ),
                    True,
                )
            )
        for name, centers, uses_labels in families:
            start = time.perf_counter()
            features, rank = nystrom_features(train, centers, gamma)
            validation_features, _ = nystrom_features(validation, centers, gamma)
            construction_time = time.perf_counter() - start
            representations.append(
                {
                    "name": f"{name}_{count}",
                    "features": features,
                    "validation_features": validation_features,
                    "kernel_reconstruction_error": float(
                        np.linalg.norm(kernel - features @ features.T) / np.linalg.norm(kernel)
                    ),
                    "representation_time_seconds": construction_time,
                    "retained_train_samples": 0,
                    "uses_train_labels_for_representation": uses_labels,
                    "landmark_count": None,
                    "landmark_rank": rank,
                    "feature_family": "synthetic_rbf_prototypes",
                    "prototype_count": len(centers),
                    "prototype_train_exact_match_count": _exact_train_match_count(train, centers),
                }
            )
    return representations


def _attach_prototype_metadata(rows, representations):
    metadata = {
        representation["name"]: {
            "prototype_count": representation.get("prototype_count"),
            "prototype_train_exact_match_count": representation.get(
                "prototype_train_exact_match_count"
            ),
        }
        for representation in representations
    }
    for row in rows:
        row.update(metadata[row["model"]])


def _oriented_pca_components(X):
    X = np.asarray(X, dtype=float)
    centered = X - X.mean(axis=0)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt.copy()
    for row_index, row in enumerate(components):
        pivot = int(np.argmax(np.abs(row)))
        if row[pivot] < 0.0:
            components[row_index] *= -1.0
    return components


def _balanced_quotas(total, group_count):
    base = total // group_count
    remainder = total % group_count
    return [base + int(index < remainder) for index in range(group_count)]


def _nearest_rival_labels(X, labels, classes, gamma):
    class_arrays = {label: X[labels == label] for label in classes}
    rivals = {}
    for label in classes:
        best_label = None
        best_affinity = -np.inf
        local = class_arrays[label]
        for other in classes:
            if other == label:
                continue
            affinity = float(rbf_kernel(local, class_arrays[other], gamma=gamma).mean())
            if affinity > best_affinity:
                best_affinity = affinity
                best_label = other
        rivals[label] = best_label
    return rivals


def _exact_train_match_count(train, centers):
    matches = 0
    for center in centers:
        matches += int(np.any(np.all(np.isclose(train, center, atol=1e-12, rtol=0.0), axis=1)))
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/dns05_prototype_digits.json"))
    parser.add_argument("--output", type=Path, default=Path("results/dns05_prototype_digits.json"))
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
        [sys.executable, "-m", "experiments.run_dns05_prototype", *sys.argv[1:]]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for model, metrics in result["selected_summary"].items():
        print(model, metrics["validation_accuracy"])


if __name__ == "__main__":
    main()
