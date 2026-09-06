"""End-to-end primary-width stream diagnostic on FMSA development splits."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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
from dns.synthesis.linear_algebra import solve_primal_ridge, solve_streaming_primal_ridge
from experiments.run_dns05_depth_width import one_hot, select_rbf_oracle
from experiments.run_dns05_failure_scaling import (
    _fit_kernel_readout,
    _kernel_readout_bytes,
    _predict_kernel,
    load_audit_dataset,
)
from experiments.run_dns05_landmark import _inverse_square_root_psd, uniform_landmark_indices
from experiments.run_streaming_resource_probe import memory

CONFIG = Path("configs/dns05_bm_end_to_end.json")


def evaluate(train_raw, labels, validation_raw, validation_labels, seed, method, cfg, base):
    start_total = time.perf_counter()
    scaler = Standardizer().fit(train_raw)
    train = scaler.transform(train_raw)
    validation = scaler.transform(validation_raw)
    classes = np.unique(labels)
    targets = one_hot(labels, classes)
    observed = one_hot(validation_labels, classes)
    before_oracle = memory()
    start = time.perf_counter()
    selection = None
    if method not in ("linear", "relu"):
        selection = select_rbf_oracle(
            train, targets, validation, validation_labels, classes,
            split_seed=seed, config=base,
        )
    oracle_seconds = time.perf_counter() - start
    after_oracle = memory()
    gamma = selection.gamma if selection else None
    start = time.perf_counter()
    budget = cfg["feature_budget"]
    stored = [scaler.mean_, scaler.scale_]
    retained = 0
    if method in ("batch", "stream"):
        centers = train[uniform_landmark_indices(
            len(train), min(budget, len(train)), base["landmark_seed"] + 1009 * seed + budget,
        )].copy()
        root, _ = _inverse_square_root_psd(rbf_kernel(centers, gamma=gamma))
        stored += [centers, root]
        retained = len(centers)

        def transform(x):
            return rbf_kernel(x, centers, gamma=gamma) @ root
    elif method == "linear":
        def transform(x):
            return x
    elif method == "relu":
        projection, bias = deterministic_relu_projection(
            n_features=train.shape[1], hidden_units=budget, seed=cfg["relu_seed"],
        )
        stored += [projection, bias]

        def transform(x):
            return np.maximum(x @ projection + bias, 0)
    elif method == "spectral":
        values, vectors = np.linalg.eigh(rbf_kernel(train, gamma=gamma))
        indices = np.flatnonzero(values > 1e-10 * max(1, values.max()))[::-1][:budget]
        extension = vectors[:, indices] / np.sqrt(values[indices])
        stored += [train, extension]
        retained = len(train)

        def transform(x):
            return rbf_kernel(x, train, gamma=gamma) @ extension
    elif method == "rbf":
        stored += [train]
        retained = len(train)

        def transform(x):
            return rbf_kernel(x, train, gamma=gamma)
    else:
        raise ValueError(method)
    features = None if method == "stream" else transform(train)
    map_seconds = time.perf_counter() - start
    validation_features = transform(validation)
    grid = []
    readouts = []
    for alpha in base["alphas"]:
        for intercept in base["intercepts"]:
            start = time.perf_counter()
            if method == "stream":
                size = cfg["block_size"]
                weights = solve_streaming_primal_ridge(
                    (transform(train[i:i + size]) for i in range(0, len(train), size)),
                    (targets[i:i + size] for i in range(0, len(train), size)),
                    alpha=alpha, fit_intercept=intercept,
                )
            elif method == "rbf":
                weights = _fit_kernel_readout(features, targets, alpha, intercept)
            else:
                weights = solve_primal_ridge(features, targets, alpha=alpha, fit_intercept=intercept)
            solve_seconds = time.perf_counter() - start
            scores = predict_features(validation_features, weights, intercept, method)
            residual = np.sum((scores - observed)**2)
            grid.append({
                "alpha": alpha, "intercept": intercept,
                "validation_accuracy": float(np.mean(classes[scores.argmax(axis=1)] == validation_labels)),
                "validation_rmse": float(np.sqrt(residual / observed.size)),
                "validation_r2": float(1 - residual / np.sum((observed-observed.mean(axis=0))**2)),
                "readout_seconds": solve_seconds,
                "weights": weights.tolist() if method in ("batch", "stream") else None,
                "scores": scores.tolist() if method in ("batch", "stream") else None,
            })
            readouts.append(weights)
    chosen = min(range(len(grid)), key=lambda i: (
        -grid[i]["validation_accuracy"], grid[i]["validation_rmse"],
        grid[i]["alpha"], grid[i]["intercept"],
    ))
    fit_seconds = time.perf_counter() - start_total
    fit_memory = memory()
    weights = readouts[chosen]
    intercept = grid[chosen]["intercept"]

    def predict():
        return np.vstack([
            predict_features(transform(validation[i:i + 256]), weights, intercept, method)
            for i in range(0, len(validation), 256)
        ])
    predict()
    timings = []
    for _ in range(cfg["repeats"]):
        start = time.perf_counter()
        predict()
        timings.append(time.perf_counter()-start)
    start = time.perf_counter()
    diagnostic_features = transform(train)
    rank = int(np.linalg.matrix_rank(diagnostic_features))
    kernel_error = None
    if gamma is not None:
        oracle = rbf_kernel(train, gamma=gamma)
        reconstructed = oracle if method == "rbf" else diagnostic_features @ diagnostic_features.T
        kernel_error = float(np.linalg.norm(oracle-reconstructed)/np.linalg.norm(oracle))
    readout_bytes = _kernel_readout_bytes(weights) if method == "rbf" else weights.nbytes
    return {
        "method": method, "seed": seed, "grid": grid, "selected_index": chosen,
        "selection": asdict(selection) if selection else None,
        "before_oracle": before_oracle, "after_oracle": after_oracle, "after_fit": fit_memory,
        "after_diagnostics": memory(), "diagnostic_seconds": time.perf_counter()-start,
        "fit_seconds": fit_seconds, "oracle_seconds": oracle_seconds, "map_seconds": map_seconds,
        "inference_seconds": timings, "rank": rank, "feature_budget": diagnostic_features.shape[1],
        "kernel_reconstruction_error": kernel_error, "retained_train_samples": retained,
        "model_array_bytes": int(sum(a.nbytes for a in stored) + readout_bytes),
        "training_feature_passes": 8 if method == "stream" else 1,
        "test_status": "not_evaluated", "test_accuracy": None, "test_rmse": None, "test_r2": None,
    }


def predict_features(features, weights, intercept, method):
    if method == "rbf":
        return _predict_kernel(features, weights)
    return weights[0] + features @ weights[1:] if intercept else features @ weights


def worker(dataset, seed, method, cfg, base):
    spec = next(s for s in base["datasets"] if s["name"] == dataset)
    X, y, _ = load_audit_dataset(spec)
    train, validation, excluded = stratified_train_validation_test_split(
        y, seed=seed, train_fraction=0.6, validation_fraction=0.2,
    )
    row = evaluate(X[train], y[train], X[validation], y[validation], seed, method, cfg, base)
    row.update(dataset=dataset, dataset_sha256=hashlib.sha256(X.tobytes()+y.tobytes()).hexdigest(),
               train_indices=train.tolist(), validation_indices=validation.tolist(),
               excluded_indices=excluded.tolist())
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--dataset")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--method")
    parser.add_argument("--output", type=Path, default=Path("results/dns05_bm_end_to_end.json"))
    args = parser.parse_args()
    cfg = json.loads(CONFIG.read_text())
    base = json.loads(Path(cfg["base_config"]).read_text())
    if args.worker:
        print(json.dumps(worker(args.dataset, args.seed, args.method, cfg, base)))
        return
    import psutil
    from threadpoolctl import threadpool_info

    env = dict(os.environ)
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        env[name] = str(cfg["threads"])
    record = {
        "config": cfg, "base_config": base, "rows": [], "status": "running",
        "commit_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": subprocess.list2cmdline([sys.executable, *sys.argv]),
        "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
                        "cpu": platform.processor(), "ram": psutil.virtual_memory().total,
                        "parent_threadpools": threadpool_info(), "psutil": psutil.__version__},
    }
    args.output.parent.mkdir(exist_ok=True, parents=True)
    for spec in base["datasets"]:
        for index, seed in enumerate(spec["split_seeds"]):
            methods = cfg["methods"] if index % 2 == 0 else cfg["methods"][::-1]
            for method in methods:
                import tempfile
                start = time.monotonic()
                with tempfile.TemporaryFile(mode="w+t") as stdout, tempfile.TemporaryFile(mode="w+t") as stderr:
                    process = subprocess.Popen(
                        [sys.executable, "-m", "experiments.run_dns05_bm_end_to_end", "--worker",
                         "--dataset", spec["name"], "--seed", str(seed), "--method", method],
                        env=env, stdout=stdout, stderr=stderr,
                    )
                    error = None
                    while process.poll() is None:
                        try:
                            rss = psutil.Process(process.pid).memory_info().rss
                        except psutil.NoSuchProcess:
                            break
                        if rss > cfg["memory_limit_bytes"] or time.monotonic()-start > cfg["timeout_seconds"]:
                            error = "memory_or_time_limit"
                            process.kill()
                            break
                        time.sleep(0.05)
                    process.wait()
                    stdout.seek(0)
                    stderr.seek(0)
                    try:
                        if error or process.returncode:
                            raise RuntimeError(error or stderr.read())
                        row = json.load(stdout)
                    except (ValueError, RuntimeError) as exc:
                        row = {"dataset": spec["name"], "seed": seed, "method": method, "error": str(exc)}
                record["rows"].append(row)
                args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
                print(f"Completed {spec['name']}/{seed}/{method}: {'error' if 'error' in row else 'ok'}", flush=True)
    record["status"] = "finished_with_errors" if any("error" in r for r in record["rows"]) else "complete"
    args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
