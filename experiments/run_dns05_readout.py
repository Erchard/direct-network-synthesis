"""Validation-only matched-readout diagnostic; never evaluates test samples."""

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


def kernel_readout(train_kernel, targets, cross_kernel, alpha, intercept):
    """Ridge with an unpenalized intercept, equivalent to centered primal ridge."""
    if intercept:
        column_mean = train_kernel.mean(axis=0)
        grand_mean = train_kernel.mean()
        centered = train_kernel - column_mean[None, :] - column_mean[:, None] + grand_mean
        cross = cross_kernel - cross_kernel.mean(axis=1)[:, None] - column_mean + grand_mean
        target_mean = targets.mean(axis=0)
    else:
        centered, cross, target_mean = train_kernel, cross_kernel, 0.0
    start = time.perf_counter()
    dual = stable_solve(centered + alpha * np.eye(len(targets)), targets - target_mean)
    solve_time = time.perf_counter() - start
    start = time.perf_counter()
    scores = cross @ dual + target_mean
    return scores, solve_time, time.perf_counter() - start


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
    count = config["feature_count"]
    start = time.perf_counter()
    kernel = rbf_kernel(train, gamma=selection.gamma)
    cross = rbf_kernel(validation, train, gamma=selection.gamma)
    kernel_time = time.perf_counter() - start
    start = time.perf_counter()
    compiler = DNS05CompiledFeatureClassifier(
        gamma=selection.gamma,
        config=DNS05FeatureCompilerConfig(total_feature_count=count, block_count=1),
    ).fit(X_train, y_train)
    compiled_validation = compiler.transform(X_validation)
    compilation_time = time.perf_counter() - start
    start = time.perf_counter()
    basis = compiler.feature_map_.transform_columns(X_train, np.arange(count))
    basis_validation = compiler.feature_map_.transform_columns(X_validation, np.arange(count))
    basis_time = time.perf_counter() - start
    start = time.perf_counter()
    values, vectors = np.linalg.eigh(kernel)
    indices = np.argsort(values)[::-1][:count]
    indices = indices[values[indices] > 1e-10 * max(1.0, values.max())]
    spectral = vectors[:, indices] * np.sqrt(values[indices])
    spectral_validation = cross @ (vectors[:, indices] / np.sqrt(values[indices]))
    spectral_time = time.perf_counter() - start
    start = time.perf_counter()
    weights, bias = deterministic_relu_projection(
        n_features=train.shape[1],
        hidden_units=count,
        seed=config["relu_seed"],
    )
    fixed = relu_features(train, weights, bias, True)
    fixed_validation = relu_features(validation, weights, bias, True)
    fixed_time = time.perf_counter() - start
    representations = {
        "linear": (train, validation, None, 0.0),
        "fixed_relu": (fixed, fixed_validation, None, fixed_time),
        "pca_relu": (basis, basis_validation, None, basis_time),
        "compiled": (
            compiler.train_embedding_,
            compiled_validation,
            compiler.kernel_reconstruction_error_,
            compilation_time,
        ),
        "spectral": (
            spectral,
            spectral_validation,
            float(np.linalg.norm(kernel - spectral @ spectral.T) / np.linalg.norm(kernel)),
            spectral_time,
        ),
        "rbf": (kernel, cross, 0.0, kernel_time),
    }
    rows = []
    for name, (features, new_features, error, construction_time) in representations.items():
        rank = int(np.linalg.matrix_rank(features))
        for alpha in config["alphas"]:
            for intercept in config["intercepts"]:
                if name == "rbf":
                    scores, solve_time, inference_time = kernel_readout(
                        features,
                        targets,
                        new_features,
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
                        np.column_stack([np.ones(len(new_features)), new_features])
                        if intercept
                        else new_features
                    )
                    start = time.perf_counter()
                    scores = design @ readout
                    inference_time = time.perf_counter() - start
                residual_sum = float(np.sum((scores - observed) ** 2))
                total_sum = float(np.sum((observed - observed.mean(axis=0)) ** 2))
                rows.append(
                    {
                        "model": name,
                        "split_seed": seed,
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
                        "kernel_reconstruction_error": error,
                        "rank": rank,
                        "feature_budget": features.shape[1],
                        "readout_parameter_count": (features.shape[1] + int(intercept))
                        * len(classes),
                        "retained_train_samples": len(train) if name in {"rbf", "spectral"} else 0,
                        "solve_time_seconds": solve_time,
                        "inference_time_seconds": inference_time,
                        "representation_time_seconds": construction_time,
                        "uses_iterative_parameter_optimization": False,
                    }
                )
    return rows, {"oracle": asdict(selection), "preprocessing_seconds": preprocessing_time}


METRICS = [
    "validation_accuracy",
    "validation_rmse",
    "validation_r2",
    "rank",
    "feature_budget",
    "readout_parameter_count",
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


def aggregate(rows):
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
                    key=lambda r: (
                        -r["validation_accuracy"],
                        r["alpha"],
                        r["intercept"],
                    ),
                )
            )
        for alpha, intercept in settings:
            group = [
                r
                for r in rows
                if r["model"] == model and r["alpha"] == alpha and r["intercept"] == intercept
            ]
            matched[f"{model}/alpha={alpha}/intercept={intercept}"] = summary(group)
    for left, right in [
        ("compiled", "pca_relu"),
        ("compiled", "spectral"),
        ("spectral", "rbf"),
        ("compiled", "fixed_relu"),
    ]:
        for setting in [None, *settings]:
            source = (
                selected
                if setting is None
                else [r for r in rows if (r["alpha"], r["intercept"]) == setting]
            )
            lrows = {r["split_seed"]: r for r in source if r["model"] == left}
            rrows = {r["split_seed"]: r for r in source if r["model"] == right}
            pairs[f"{left}_minus_{right}/{setting}"] = {
                metric: summarize_values([lrows[s][metric] - rrows[s][metric] for s in seeds])
                for metric in METRICS
                if all(lrows[s][metric] is not None and rrows[s][metric] is not None for s in seeds)
            }
    return {
        "matched_summary": matched,
        "selected_rows": selected,
        "selected_summary": {m: summary([r for r in selected if r["model"] == m]) for m in models},
        "paired_differences": pairs,
    }


def run(config):
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
        print(f"Completed development split {seed}", flush=True)
    return {
        "config": config,
        "commit_sha": get_commit_sha(),
        "git_status_short": get_git_status_short(),
        "rows": rows,
        "splits": records,
        "test_status": "not_evaluated",
        "dataset_sha256": hashlib.sha256(X.tobytes() + y.tobytes()).hexdigest(),
        **aggregate(rows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/dns05_readout_digits.json"))
    parser.add_argument("--output", type=Path, default=Path("results/dns05_readout_digits.json"))
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
        [sys.executable, "-m", "experiments.run_dns05_readout", *sys.argv[1:]]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for model, metrics in result["selected_summary"].items():
        print(model, metrics["validation_accuracy"])


if __name__ == "__main__":
    main()
