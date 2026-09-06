import numpy as np

from dns.kernels import rbf_kernel
from experiments import run_dns05_failure_scaling as audit


def _small_config():
    return {
        "alphas": [0.01],
        "dipole_shift_fraction": 0.25,
        "feature_counts": [4, 6],
        "hybrid_boundary_pairs_per_class": 1,
        "include_rbf_reference": True,
        "intercepts": [False],
        "landmark_seed": 2309,
        "model_families": [
            "nystrom_uniform",
            "prototype_class_hybrid",
            "spectral",
        ],
        "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
        "paired_families": [["prototype_class_hybrid", "nystrom_uniform"]],
        "prediction_repeats": 2,
        "prediction_warmups": 1,
        "prototype_quantiles": [0.25, 0.5, 0.75],
        "splits": {"split_seeds": [701], "train_fraction": 0.6, "validation_fraction": 0.2},
    }


def test_run_records_excluded_partition_without_evaluating_it(monkeypatch):
    X = np.arange(90).reshape(30, 3).astype(float)
    y = np.repeat([0, 1, 2], 10)
    train, validation, excluded = np.arange(18), np.arange(18, 24), np.arange(24, 30)
    calls = []

    monkeypatch.setattr(
        audit,
        "load_audit_dataset",
        lambda spec: (X, y, {"name": spec["name"], "n_samples": len(X)}),
    )
    monkeypatch.setattr(
        audit,
        "stratified_train_validation_test_split",
        lambda *a, **kw: (train, validation, excluded),
    )

    def evaluate(xt, yt, xv, yv, config, seed, dataset_name):
        np.testing.assert_array_equal(xt, X[train])
        np.testing.assert_array_equal(xv, X[validation])
        np.testing.assert_array_equal(yt, y[train])
        np.testing.assert_array_equal(yv, y[validation])
        calls.append((dataset_name, seed))
        return {"rows": [], "selected_rows": []}, {"oracle": {}}

    monkeypatch.setattr(audit, "evaluate_development", evaluate)
    result = audit.run({**_small_config(), "datasets": [{"name": "dummy_audit"}]})

    assert calls == [("dummy_audit", 701)]
    assert result["test_status"] == "not_evaluated"
    assert result["splits"][0]["excluded_indices"] == excluded.tolist()


def test_center_metrics_detect_exact_landmarks():
    train = np.array([[0.0], [1.0], [2.0]])
    centers = train[[0, 2]]
    train_to_centers = rbf_kernel(train, centers, gamma=1.0)
    metrics = audit._center_metrics(
        train,
        centers,
        1.0,
        rbf_kernel(centers, gamma=1.0),
        train_to_centers,
    )

    assert metrics["center_exact_train_match_count"] == 2
    assert metrics["mean_max_train_kernel_similarity"] < 1.0
    assert metrics["coverage_fraction_ge_0_5"] == 2 / 3
    assert metrics["basis_condition_number"] is not None


def test_evaluate_development_keeps_test_metrics_null():
    rng = np.random.default_rng(81)
    X = rng.normal(size=(45, 4))
    y = np.tile([0, 1, 2], 15)
    result, _ = audit.evaluate_development(
        X[:27],
        y[:27],
        X[27:36],
        y[27:36],
        _small_config(),
        81,
        "synthetic_unit",
    )

    assert len(result["rows"]) == 7
    assert len(result["selected_rows"]) == 7
    assert all(row["test_accuracy"] is None for row in result["rows"])
    assert all(row["test_accuracy"] is None for row in result["selected_rows"])
    assert all(
        row["test_status"] == "not_evaluated_validation_only_audit"
        for row in result["selected_rows"]
    )
    hybrid = next(
        row
        for row in result["selected_rows"]
        if row["model"] == "prototype_class_hybrid_6"
    )
    nystrom = next(row for row in result["selected_rows"] if row["model"] == "nystrom_uniform_6")
    assert hybrid["retained_train_samples"] == 0
    assert hybrid["basis_count"] == 6
    assert nystrom["retained_train_samples"] == 6
    assert nystrom["center_exact_train_match_count"] == 6
