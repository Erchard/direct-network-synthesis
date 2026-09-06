"""Frozen synthetic implementation probe; no benchmark or test-set evaluation."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from dns.kernels import rbf_kernel
from dns.synthesis.linear_algebra import solve_primal_ridge, solve_streaming_primal_ridge


def memory():
    """Windows process working set and lifetime peak, including native arrays."""
    class Counters(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("faults", ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in (
                "peak", "working", "peak_paged", "paged", "peak_nonpaged",
                "nonpaged", "pagefile", "peak_pagefile",
            )
        ]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong,
    ]
    if not psapi.GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb,
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    return {"rss_bytes": counters.working, "peak_rss_bytes": counters.peak}


def worker(seed, block):
    rng = np.random.default_rng(seed)
    train = rng.normal(size=(6000, 16))
    validation = rng.normal(size=(1000, 16))
    # Separate generator defines a fixed label rule, shared by both partitions.
    rule = np.random.default_rng(81001).normal(size=(16, 3))
    targets = np.eye(3)[(train @ rule).argmax(axis=1)]
    labels = (validation @ rule).argmax(axis=1)
    centers = train[rng.choice(len(train), 192, replace=False)].copy()
    before = memory()
    start = time.perf_counter()
    values, vectors = np.linalg.eigh(rbf_kernel(centers, gamma=0.03))
    inverse = (vectors * (1 / np.sqrt(np.maximum(values, 1e-10)))) @ vectors.T
    center_seconds = time.perf_counter() - start
    start = time.perf_counter()
    if block == 0:
        features = rbf_kernel(train, centers, gamma=0.03) @ inverse
        weights = solve_primal_ridge(features, targets, alpha=0.1)
    else:
        weights = solve_streaming_primal_ridge(
            (rbf_kernel(train[i:i + block], centers, gamma=0.03) @ inverse
             for i in range(0, len(train), block)),
            (targets[i:i + block] for i in range(0, len(train), block)),
            alpha=0.1,
        )
    fit_seconds = time.perf_counter() - start
    after_fit = memory()

    def predict():
        return np.vstack([
            weights[0] + (rbf_kernel(validation[i:i + 256], centers, gamma=0.03)
                          @ inverse) @ weights[1:]
            for i in range(0, len(validation), 256)
        ])

    scores = predict()
    times = []
    for _ in range(5):
        start = time.perf_counter()
        predict()
        times.append(time.perf_counter() - start)
    return {
        "seed": seed, "block_size": block, "before": before, "after_fit": after_fit,
        "center_seconds": center_seconds, "fit_seconds": fit_seconds,
        "inference_seconds": times, "validation_accuracy": float(np.mean(
            scores.argmax(axis=1) == labels)),
        "weights": weights.tolist(), "scores": scores.tolist(),
        "model_array_bytes": centers.nbytes + inverse.nbytes + weights.nbytes,
        "feature_budget": 192, "test_status": "not_evaluated",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--block", type=int)
    parser.add_argument("--output", type=Path, default=Path("results/streaming_resource_probe.json"))
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.seed, args.block)))
        return
    env = dict(os.environ)
    for key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
        env[key] = "1"
    record = {
        "commit_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": subprocess.list2cmdline([sys.executable, *sys.argv]),
        "python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "seeds": [81101, 81202, 81303, 81404, 81505],
        "blocks": [0, 64, 256, 1024], "threads": 1, "rows": [], "pairs": [],
        "status": "running", "scope": "synthetic fixed-geometry fitting probe",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")

    save()
    for index, seed in enumerate(record["seeds"]):
        order = record["blocks"] if index % 2 == 0 else record["blocks"][::-1]
        group = {}
        for block in order:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "experiments.run_streaming_resource_probe",
                     "--worker", "--seed", str(seed), "--block", str(block)],
                    env=env, capture_output=True, text=True, timeout=120, check=True,
                )
                row = json.loads(result.stdout)
                group[block] = row
                record["rows"].append(row)
            except (subprocess.SubprocessError, ValueError) as exc:
                record["rows"].append({"seed": seed, "block_size": block, "error": str(exc)})
            save()
            print(f"Completed {seed}/{block}", flush=True)
        if 0 in group:
            baseline = group[0]
            for block in (64, 256, 1024):
                if block not in group:
                    continue
                row = group[block]
                record["pairs"].append({
                    "seed": seed, "block_size": block,
                    "weights_match": bool(np.allclose(row["weights"], baseline["weights"],
                                                       rtol=1e-8, atol=1e-10)),
                    "scores_match": bool(np.allclose(row["scores"], baseline["scores"],
                                                      rtol=1e-8, atol=1e-10)),
                    "max_score_difference": float(np.max(np.abs(
                        np.asarray(row["scores"]) - baseline["scores"]))),
                    "accuracy_difference": row["validation_accuracy"] - baseline["validation_accuracy"],
                    "peak_memory_reduction": 1 - row["after_fit"]["peak_rss_bytes"]
                    / baseline["after_fit"]["peak_rss_bytes"],
                    "fit_seconds_difference": row["fit_seconds"] - baseline["fit_seconds"],
                })
        save()
    record["status"] = "finished_with_errors" if any("error" in r for r in record["rows"]) else "complete"
    save()


if __name__ == "__main__":
    main()
