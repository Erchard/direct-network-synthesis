import numpy as np

from experiments import run_dns05_confirmation as confirmation


def _small_config():
    return {
        "alphas": [0.01],
        "dipole_shift_fraction": 0.25,
        "feature_count": 6,
        "fixed_relu_seed": 1705,
        "fixed_relu_total_feature_count": 8,
        "hybrid_boundary_pairs_per_class": 1,
        "intercepts": [False],
        "landmark_seed": 2309,
        "models": [
            "fixed_relu_8",
            "linear",
            "nystrom_uniform_6",
            "prototype_class_hybrid_6",
            "rbf",
            "spectral_6",
        ],
        "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
        "paired_models": [["prototype_class_hybrid_6", "nystrom_uniform_6"]],
        "prediction_repeats": 2,
        "prediction_warmups": 1,
        "prototype_quantiles": [0.25, 0.5, 0.75],
        "splits": {"split_seeds": [701], "train_fraction": 0.6, "validation_fraction": 0.2},
    }


def test_confirmation_run_passes_disjoint_train_validation_test(monkeypatch):
    X = np.arange(90).reshape(30, 3).astype(float)
    y = np.repeat([0, 1, 2], 10)
    train, validation, test = np.arange(18), np.arange(18, 24), np.arange(24, 30)
    calls = []

    monkeypatch.setattr(
        confirmation,
        "load_named_dataset",
        lambda spec: (X, y, {"name": spec["name"], "n_samples": len(X)}),
    )
    monkeypatch.setattr(
        confirmation,
        "stratified_train_validation_test_split",
        lambda *a, **kw: (train, validation, test),
    )

    def evaluate(xt, yt, xv, yv, xte, yte, config, seed, dataset_name):
        np.testing.assert_array_equal(xt, X[train])
        np.testing.assert_array_equal(xv, X[validation])
        np.testing.assert_array_equal(xte, X[test])
        np.testing.assert_array_equal(yt, y[train])
        np.testing.assert_array_equal(yv, y[validation])
        np.testing.assert_array_equal(yte, y[test])
        calls.append((dataset_name, seed))
        return {"rows": [], "selected_rows": []}, {"oracle": {}}

    monkeypatch.setattr(confirmation, "evaluate_split", evaluate)
    result = confirmation.run(
        {
            **_small_config(),
            "datasets": [{"name": "dummy_confirmation"}],
        }
    )

    assert calls == [("dummy_confirmation", 701)]
    assert result["test_status"] == "evaluated_after_validation_selection"
    assert result["splits"][0]["test_indices"] == test.tolist()


def test_confirmation_grid_keeps_test_metrics_only_on_selected_rows():
    rng = np.random.default_rng(81)
    X = rng.normal(size=(90, 5))
    y = np.tile([0, 1, 2], 30)
    result, _ = confirmation.evaluate_split(
        X[:54],
        y[:54],
        X[54:72],
        y[54:72],
        X[72:],
        y[72:],
        _small_config(),
        81,
        "synthetic_unit",
    )

    assert len(result["rows"]) == 6
    assert len(result["selected_rows"]) == 6
    assert all(row["test_accuracy"] is None for row in result["rows"])
    assert all(row["test_status"] == "not_evaluated_grid_row" for row in result["rows"])
    assert all(np.isfinite(row["test_accuracy"]) for row in result["selected_rows"])
    assert all(
        row["test_status"] == "evaluated_after_validation_selection"
        for row in result["selected_rows"]
    )
    hybrid = next(
        row for row in result["selected_rows"] if row["model"] == "prototype_class_hybrid_6"
    )
    assert hybrid["retained_train_samples"] == 0
    assert hybrid["prototype_count"] == 6
    assert hybrid["prototype_train_exact_match_count"] == 0


def test_confirmation_aggregate_keeps_datasets_separate():
    rows = [
        {
            "dataset": "a",
            "model": "left",
            "split_seed": 1,
            "test_accuracy": 0.8,
            "validation_accuracy": 0.9,
            "model_state_bytes": 50,
            "test_prediction_mean_seconds": 0.5,
        },
        {
            "dataset": "a",
            "model": "rbf",
            "split_seed": 1,
            "test_accuracy": 1.0,
            "validation_accuracy": 1.0,
            "model_state_bytes": 100,
            "test_prediction_mean_seconds": 1.0,
        },
        {
            "dataset": "b",
            "model": "left",
            "split_seed": 1,
            "test_accuracy": 0.4,
            "validation_accuracy": 0.5,
            "model_state_bytes": 25,
            "test_prediction_mean_seconds": 0.25,
        },
        {
            "dataset": "b",
            "model": "rbf",
            "split_seed": 1,
            "test_accuracy": 0.7,
            "validation_accuracy": 0.8,
            "model_state_bytes": 100,
            "test_prediction_mean_seconds": 1.0,
        },
    ]

    report = confirmation.aggregate([], rows, [["left", "rbf"]])

    assert set(report["selected_summary"]) == {"a", "b"}
    assert np.isclose(
        report["paired_differences"]["a:left_minus_rbf"]["test_accuracy"]["mean"],
        -0.2,
    )
    assert np.isclose(
        report["paired_differences"]["b:left_minus_rbf"]["test_accuracy"]["mean"],
        -0.3,
    )
    ratio = report["efficiency_summary"]["a"]["left"]["model_state_bytes_ratio_to_rbf"]
    assert ratio["mean"] == 0.5
