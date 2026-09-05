"""Regression metrics and summary helpers."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean((y_true - y_pred) ** 2))


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residual = float(np.sum((y_true - y_pred) ** 2))
    centered = y_true - np.mean(y_true)
    total = float(np.sum(centered**2))
    if total == 0.0:
        return 0.0
    return 1.0 - residual / total


def summarize_metric_rows(rows: Iterable[dict[str, float | str | bool | int]]) -> dict[str, dict]:
    """Summarize per-split metric rows by model name."""

    grouped: dict[str, list[dict[str, float | str | bool | int]]] = {}
    for row in rows:
        grouped.setdefault(str(row["model"]), []).append(row)

    summary: dict[str, dict] = {}
    for model, model_rows in grouped.items():
        metric_names = [
            name
            for name, value in model_rows[0].items()
            if name not in {"model", "split_seed", "uses_iterative_parameter_optimization"}
            and isinstance(value, int | float)
        ]
        summary[model] = {
            "n_splits": len(model_rows),
            "uses_iterative_parameter_optimization": bool(
                model_rows[0]["uses_iterative_parameter_optimization"]
            ),
            "metrics": {
                name: {
                    "mean": float(np.mean([float(row[name]) for row in model_rows])),
                    "std": float(np.std([float(row[name]) for row in model_rows], ddof=1))
                    if len(model_rows) > 1
                    else 0.0,
                }
                for name in metric_names
            },
        }
    return summary
