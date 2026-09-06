"""Validation-only per-example error geometry diagnostic."""

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
from dns.synthesis.linear_algebra import solve_primal_ridge
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
    class_balanced_farthest_indices,
    farthest_first_indices,
    uniform_landmark_indices,
)
from experiments.run_dns05_prototype import _prototype_representations
from experiments.run_dns05_readout import kernel_readout

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

DEFAULT_ANALYSIS_PAIRS = [
    ("compiled_192", "spectral_192"),
    ("compiled_192", "nystrom_uniform_192"),
    ("compiled_192", "nystrom_farthest_192"),
    ("compiled_192", "fixed_relu_256"),
    ("nystrom_uniform_192", "spectral_192"),
    ("spectral_192", "rbf"),
]


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

    representations = _build_representations(
        X_train,
        y_train,
        X_validation,
        train,
        validation,
        kernel,
        cross,
        selection.gamma,
        kernel_time,
        config,
        seed,
    )
    rows, selected, predictions = _select_predictions(
        representations,
        targets,
        observed,
        y_validation,
        classes,
        config,
        seed,
    )
    samples = _sample_records(
        predictions,
        train,
        y_train,
        validation,
        y_validation,
        cross,
        selection.gamma,
        config,
        seed,
    )
    return (
        {"rows": rows, "selected_rows": selected, "sample_records": samples},
        {"oracle": asdict(selection), "preprocessing_seconds": preprocessing_time},
    )


def aggregate(rows, selected_rows, sample_records, config):
    seeds = sorted({r["split_seed"] for r in selected_rows})
    selected_summary = {
        model: _summary([r for r in selected_rows if r["model"] == model])
        for model in sorted({r["model"] for r in selected_rows})
    }
    return {
        "selected_summary": selected_summary,
        "tag_counts": _tag_counts(sample_records, seeds),
        "tag_geometry": _tag_geometry(sample_records),
        "confusion_counts": _confusion_counts(sample_records, config["models"]),
        "pair_error_overlap": _pair_error_overlap(
            sample_records,
            config["analysis_pairs"],
            seeds,
        ),
    }


def run(config):
    if config.get("dataset", {}).get("name") != "sklearn_digits":
        raise ValueError("Only sklearn_digits is supported by this runner.")
    X, y = load_digits_dataset()
    rows, selected_rows, samples, records = [], [], [], []
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
        for sample in split_result["sample_records"]:
            sample["global_index"] = int(validation[sample["validation_position"]])
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
        samples.extend(split_result["sample_records"])
        print(f"Completed error-geometry split {seed}", flush=True)
    return {
        "config": config,
        "commit_sha": get_commit_sha(),
        "git_status_short": get_git_status_short(),
        "rows": rows,
        "selected_rows": selected_rows,
        "sample_records": samples,
        "splits": records,
        "test_status": "not_evaluated",
        "dataset_sha256": hashlib.sha256(X.tobytes() + y.tobytes()).hexdigest(),
        **aggregate(rows, selected_rows, samples, config),
    }


def _build_representations(
    X_train,
    y_train,
    X_validation,
    train,
    validation,
    kernel,
    cross,
    gamma,
    kernel_time,
    config,
    seed,
):
    representations = _anchor_representations(
        X_train,
        y_train,
        X_validation,
        train,
        validation,
        kernel,
        cross,
        gamma,
        config,
    )
    representations.extend(
        _landmark_representations(train, y_train, validation, kernel, gamma, seed, config)
    )
    if config.get("include_prototype_representations", False):
        representations.extend(
            _prototype_representations(train, y_train, validation, kernel, gamma, config)
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
    requested = set(config["models"])
    available = {r["name"] for r in representations}
    missing = requested - available
    if missing:
        raise ValueError(f"Requested models are unavailable: {sorted(missing)}")
    return [r for r in representations if r["name"] in requested]


def _select_predictions(representations, targets, observed, y_validation, classes, config, seed):
    rows = []
    selected_rows = []
    selected_predictions = {}
    for representation in representations:
        candidates = []
        for alpha in config["alphas"]:
            for intercept in config["intercepts"]:
                scores, solve_time, inference_time = _scores_for_readout(
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
                    seed,
                )
                rows.append(row)
                candidates.append((row, scores))
        selected_row, selected_scores = min(
            candidates,
            key=lambda item: (
                -item[0]["validation_accuracy"],
                item[0]["alpha"],
                item[0]["intercept"],
            ),
        )
        selected_rows.append({**selected_row, "selection_status": "validation_selected"})
        selected_predictions[representation["name"]] = _prediction_records(
            selected_scores,
            y_validation,
            classes,
        )
    return rows, selected_rows, selected_predictions


def _scores_for_readout(representation, targets, alpha, intercept):
    name = representation["name"]
    features = representation["features"]
    validation_features = representation["validation_features"]
    if name == "rbf":
        return kernel_readout(features, targets, validation_features, alpha, intercept)
    start = time.perf_counter()
    readout = solve_primal_ridge(features, targets, alpha=alpha, fit_intercept=intercept)
    solve_time = time.perf_counter() - start
    design = (
        np.column_stack([np.ones(len(validation_features)), validation_features])
        if intercept
        else validation_features
    )
    start = time.perf_counter()
    scores = design @ readout
    return scores, solve_time, time.perf_counter() - start


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
    seed,
):
    features = representation["features"]
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
        "rank": int(np.linalg.matrix_rank(features)),
        "feature_budget": features.shape[1],
        "readout_parameter_count": (features.shape[1] + int(intercept)) * len(classes),
        "retained_train_samples": representation["retained_train_samples"],
        "solve_time_seconds": solve_time,
        "inference_time_seconds": inference_time,
        "representation_time_seconds": representation["representation_time_seconds"],
        "feature_family": representation["feature_family"],
                        "landmark_count": representation["landmark_count"],
                        "landmark_rank": representation["landmark_rank"],
                        "landmark_selection": representation.get("landmark_selection"),
                        "prototype_count": representation.get("prototype_count"),
                        "prototype_train_exact_match_count": representation.get(
                            "prototype_train_exact_match_count"
                        ),
                        "uses_train_labels_for_representation": representation[
                            "uses_train_labels_for_representation"
                        ],
        "uses_iterative_parameter_optimization": False,
    }


def _prediction_records(scores, y_validation, classes):
    order = np.argsort(scores, axis=1)
    top = order[:, -1]
    second = order[:, -2]
    predictions = classes[top]
    return [
        {
            "predicted_label": int(predictions[index]),
            "correct": bool(predictions[index] == y_validation[index]),
            "score_margin": float(scores[index, top[index]] - scores[index, second[index]]),
            "true_class_score": float(
                scores[index, np.flatnonzero(classes == y_validation[index])[0]]
            ),
            "predicted_class_score": float(scores[index, top[index]]),
            "runner_up_label": int(classes[second[index]]),
        }
        for index in range(len(y_validation))
    ]


def _sample_records(
    predictions,
    train,
    y_train,
    validation,
    y_validation,
    cross,
    gamma,
    config,
    seed,
):
    neighbor_records = _neighbor_records(cross, y_train, y_validation, config["neighbor_k"])
    coverage = _landmark_coverage(train, y_train, validation, y_validation, gamma, config, seed)
    records = []
    for position, neighbor in enumerate(neighbor_records):
        per_model = {model: values[position] for model, values in predictions.items()}
        records.append(
            {
                "split_seed": seed,
                "validation_position": position,
                "true_label": int(y_validation[position]),
                **neighbor,
                "landmark_coverage": {
                    model: values[position] for model, values in coverage.items()
                },
                "predictions": per_model,
                "tags": _tags(per_model, config.get("analysis_pairs")),
            }
        )
    return records


def _neighbor_records(cross, y_train, y_validation, k):
    records = []
    k = min(k, len(y_train))
    for position, similarities in enumerate(cross):
        true_label = y_validation[position]
        same = y_train == true_label
        other = ~same
        top = np.argsort(similarities)[-k:][::-1]
        nearest = int(np.argmax(similarities))
        max_same = float(np.max(similarities[same]))
        max_other = float(np.max(similarities[other]))
        records.append(
            {
                "nearest_train_label": int(y_train[nearest]),
                "nearest_train_similarity": float(similarities[nearest]),
                "max_same_class_similarity": max_same,
                "max_other_class_similarity": max_other,
                "same_minus_other_similarity_margin": max_same - max_other,
                "top_k_true_class_fraction": float(np.mean(y_train[top] == true_label)),
            }
        )
    return records


def _landmark_coverage(train, y_train, validation, y_validation, gamma, config, seed):
    count = config["diagnostic_landmark_count"]
    specs = {
        f"nystrom_uniform_{count}": uniform_landmark_indices(
            len(train),
            count,
            config["landmark_seed"] + 1009 * seed + count,
        ),
        f"nystrom_farthest_{count}": farthest_first_indices(train, count),
        f"nystrom_class_farthest_{count}": class_balanced_farthest_indices(
            train,
            y_train,
            count,
        ),
    }
    coverage = {}
    for name, indices in specs.items():
        similarities = rbf_kernel(validation, train[indices], gamma=gamma)
        nearest = np.argmax(similarities, axis=1)
        nearest_labels = y_train[indices[nearest]]
        coverage[name] = [
            {
                "max_similarity": float(similarities[position, nearest[position]]),
                "nearest_landmark_label": int(nearest_labels[position]),
                "nearest_landmark_correct": bool(
                    nearest_labels[position] == y_validation[position]
                ),
            }
            for position in range(len(validation))
        ]
    return coverage


def _tags(predictions, analysis_pairs=None):
    tags = []
    if all(item["correct"] for item in predictions.values()):
        tags.append("all_selected_correct")
    if not any(item["correct"] for item in predictions.values()):
        tags.append("all_selected_wrong")
    pairs = DEFAULT_ANALYSIS_PAIRS if analysis_pairs is None else analysis_pairs
    for left, right in pairs:
        _add_pair_tag(tags, predictions, left, right)
    return tags


def _add_pair_tag(tags, predictions, left, right):
    if left not in predictions or right not in predictions:
        return
    if not predictions[left]["correct"] and predictions[right]["correct"]:
        tags.append(f"{left}_miss_{right}_hit")
    if predictions[left]["correct"] and not predictions[right]["correct"]:
        tags.append(f"{left}_hit_{right}_miss")


def _summary(rows):
    return {
        metric: summarize_values([r[metric] for r in rows])
        for metric in METRICS
        if all(r.get(metric) is not None for r in rows)
    }


def _tag_counts(sample_records, seeds):
    tags = sorted({tag for record in sample_records for tag in record["tags"]})
    return {
        tag: {
            "total": sum(tag in record["tags"] for record in sample_records),
            "per_split": summarize_values(
                [
                    sum(
                        tag in record["tags"]
                        for record in sample_records
                        if record["split_seed"] == seed
                    )
                    for seed in seeds
                ]
            ),
        }
        for tag in tags
    }


def _tag_geometry(sample_records):
    tags = sorted({tag for record in sample_records for tag in record["tags"]})
    keys = [
        "same_minus_other_similarity_margin",
        "top_k_true_class_fraction",
        "nearest_train_similarity",
        "max_same_class_similarity",
        "max_other_class_similarity",
    ]
    coverage_models = [
        "nystrom_uniform_192",
        "nystrom_farthest_192",
        "nystrom_class_farthest_192",
    ]
    summaries = {}
    for tag in tags:
        group = [record for record in sample_records if tag in record["tags"]]
        summaries[tag] = {key: summarize_values([record[key] for record in group]) for key in keys}
        for model in coverage_models:
            if all(model in record["landmark_coverage"] for record in group):
                summaries[tag][f"{model}_max_similarity"] = summarize_values(
                    [record["landmark_coverage"][model]["max_similarity"] for record in group]
                )
    return summaries


def _confusion_counts(sample_records, models):
    counts = {model: {} for model in models}
    for record in sample_records:
        true = record["true_label"]
        for model in models:
            prediction = record["predictions"][model]["predicted_label"]
            key = f"{true}->{prediction}"
            counts[model][key] = counts[model].get(key, 0) + 1
    return counts


def _pair_error_overlap(sample_records, pairs, seeds):
    overlap = {}
    for left, right in pairs:
        per_split = []
        for seed in seeds:
            split = [record for record in sample_records if record["split_seed"] == seed]
            left_errors = {
                record["validation_position"]
                for record in split
                if not record["predictions"][left]["correct"]
            }
            right_errors = {
                record["validation_position"]
                for record in split
                if not record["predictions"][right]["correct"]
            }
            union = left_errors | right_errors
            per_split.append(
                {
                    "split_seed": seed,
                    "left_errors": len(left_errors),
                    "right_errors": len(right_errors),
                    "shared_errors": len(left_errors & right_errors),
                    "left_only_errors": len(left_errors - right_errors),
                    "right_only_errors": len(right_errors - left_errors),
                    "jaccard": len(left_errors & right_errors) / len(union) if union else 1.0,
                }
            )
        overlap[f"{left}_vs_{right}"] = {
            key: summarize_values([row[key] for row in per_split])
            for key in [
                "left_errors",
                "right_errors",
                "shared_errors",
                "left_only_errors",
                "right_only_errors",
                "jaccard",
            ]
        }
    return overlap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/dns05_error_geometry_digits.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/dns05_error_geometry_digits.json"),
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
        [sys.executable, "-m", "experiments.run_dns05_error_geometry", *sys.argv[1:]]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for tag, values in result["tag_counts"].items():
        print(tag, values["per_split"])


if __name__ == "__main__":
    main()
