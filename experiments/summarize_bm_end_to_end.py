"""Summarize an existing BM record without evaluating any data."""

import json
from pathlib import Path

import numpy as np


def main():
    raw = Path("results/dns05_bm_end_to_end.json")
    record = json.loads(raw.read_text())
    summaries, pairs = [], []
    for spec in record["base_config"]["datasets"]:
        dataset = spec["name"]
        for method in record["config"]["methods"]:
            rows = [r for r in record["rows"] if r["dataset"] == dataset and r["method"] == method
                    and "error" not in r]
            metrics = {
                "accuracy": [r["grid"][r["selected_index"]]["validation_accuracy"] for r in rows],
                "rmse": [r["grid"][r["selected_index"]]["validation_rmse"] for r in rows],
                "r2": [r["grid"][r["selected_index"]]["validation_r2"] for r in rows],
                "peak_mib": [r["after_fit"]["peak_rss_bytes"] / 2**20 for r in rows],
                "fit_seconds": [r["fit_seconds"] for r in rows],
                "oracle_seconds": [r["oracle_seconds"] for r in rows],
                "inference_seconds": [np.mean(r["inference_seconds"]) for r in rows],
                "readout_grid_seconds": [sum(g["readout_seconds"] for g in r["grid"]) for r in rows],
                "rank": [r["rank"] for r in rows],
                "model_array_bytes": [r["model_array_bytes"] for r in rows],
                "kernel_error": [r["kernel_reconstruction_error"] for r in rows
                                 if r["kernel_reconstruction_error"] is not None],
            }
            summaries.append({"dataset": dataset, "method": method, "n": len(rows),
                              "metrics": {k: {"mean": float(np.mean(v)),
                                              "sd": float(np.std(v, ddof=1)) if len(v) > 1 else None}
                                          for k, v in metrics.items() if v}})
        for seed in spec["split_seeds"]:
            selected = {r["method"]: r for r in record["rows"]
                        if r["dataset"] == dataset and r["seed"] == seed and "error" not in r}
            if not {"batch", "stream"} <= selected.keys():
                pairs.append({"dataset": dataset, "seed": seed, "error": "missing_pair"})
                continue
            batch, stream = selected["batch"], selected["stream"]
            left, right = batch["grid"], stream["grid"]
            pairs.append({
                "dataset": dataset, "seed": seed,
                "weights_match": all(np.allclose(a["weights"], b["weights"], rtol=1e-8, atol=1e-10)
                                     for a, b in zip(left, right, strict=True)),
                "scores_match": all(np.allclose(a["scores"], b["scores"], rtol=1e-8, atol=1e-10)
                                    for a, b in zip(left, right, strict=True)),
                "prediction_disagreements": sum(int(np.sum(
                    np.argmax(a["scores"], axis=1) != np.argmax(b["scores"], axis=1)))
                    for a, b in zip(left, right, strict=True)),
                "same_selected_index": batch["selected_index"] == stream["selected_index"],
                "accuracy_difference": right[stream["selected_index"]]["validation_accuracy"]
                - left[batch["selected_index"]]["validation_accuracy"],
                "peak_reduction": 1-stream["after_fit"]["peak_rss_bytes"]/batch["after_fit"]["peak_rss_bytes"],
                "fit_difference_seconds": stream["fit_seconds"]-batch["fit_seconds"],
            })
    result = {"source_commit": record["commit_sha"], "status": record["status"],
              "summaries": summaries, "pairs": pairs,
              "errors": [r for r in record["rows"] if "error" in r]}
    result["paired_summaries"] = []
    for spec in record["base_config"]["datasets"]:
        valid = [p for p in pairs if p["dataset"] == spec["name"] and "error" not in p]
        metrics = {}
        for key in ("accuracy_difference", "peak_reduction", "fit_difference_seconds"):
            values = [p[key] for p in valid]
            metrics[key] = {"mean": float(np.mean(values)), "sd": float(np.std(values, ddof=1)),
                            "median": float(np.median(values))} if values else None
        result["paired_summaries"].append({"dataset": spec["name"], "n": len(valid), "metrics": metrics})
    Path("docs/results/dns05_bm_end_to_end_summary.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "errors": result["errors"],
                      "paired": result["paired_summaries"],
                      "all_weights_match": all(p.get("weights_match", False) for p in pairs),
                      "all_scores_match": all(p.get("scores_match", False) for p in pairs),
                      "selection_disagreements": sum(not p.get("same_selected_index", False) for p in pairs),
                      "prediction_disagreements": sum(p.get("prediction_disagreements", 0) for p in pairs)}, indent=2))


if __name__ == "__main__":
    main()
