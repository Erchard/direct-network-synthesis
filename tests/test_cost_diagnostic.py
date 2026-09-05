import numpy as np

from experiments import run_dns05_cost as diagnostic


def test_kernel_predictor_matches_centered_readout_shape():
    rng = np.random.default_rng(31)
    train = rng.normal(size=(16, 5))
    validation = rng.normal(size=(7, 5))
    targets = rng.normal(size=(16, 3))
    representation = {
        "name": "rbf",
        "features": train @ train.T,
        "validation_features": validation @ train.T,
    }
    scores, readout, _, _, byte_count = diagnostic._kernel_predictor(
        representation,
        targets,
        alpha=0.1,
        intercept=True,
    )
    assert scores.shape == (7, 3)
    assert byte_count >= readout["dual"].nbytes


def test_cost_runner_never_passes_excluded_samples_to_evaluation(monkeypatch):
    X = np.arange(60).reshape(20, 3).astype(float)
    y = np.tile([0, 1], 10)
    train, val, excluded = np.arange(10), np.arange(10, 15), np.arange(15, 20)
    X[excluded] = np.nan
    monkeypatch.setattr(diagnostic, "load_digits_dataset", lambda: (X, y))
    monkeypatch.setattr(
        diagnostic,
        "stratified_train_validation_test_split",
        lambda *a, **kw: (train, val, excluded),
    )
    calls = []

    def evaluate(xt, yt, xv, yv, config, seed):
        assert np.isfinite(xt).all() and np.isfinite(xv).all()
        np.testing.assert_array_equal(xt, X[train])
        np.testing.assert_array_equal(xv, X[val])
        calls.append(seed)
        return {"rows": [], "selected_rows": []}, {}

    monkeypatch.setattr(diagnostic, "evaluate_development", evaluate)
    monkeypatch.setattr(
        diagnostic,
        "aggregate",
        lambda rows, selected_rows, pair_specs: {},
    )
    result = diagnostic.run(
        {
            "dataset": {"name": "sklearn_digits"},
            "paired_models": [],
            "splits": {"split_seeds": [101], "train_fraction": 0.6, "validation_fraction": 0.2},
        }
    )
    assert calls == [101]
    assert result["test_status"] == "not_evaluated"


def test_synthetic_cost_grid_and_selected_cost_fields():
    rng = np.random.default_rng(37)
    X = rng.normal(size=(72, 5))
    y = np.tile([0, 1, 2, 3], 18)
    config = {
        "alphas": [0.01],
        "compiled_feature_count": 6,
        "fixed_relu_hidden_units": 6,
        "fixed_relu_seed": 1705,
        "intercepts": [False],
        "landmark_counts": [6],
        "landmark_seed": 2309,
        "models": [
            "compiled_6",
            "fixed_relu_11",
            "linear",
            "nystrom_class_farthest_6",
            "nystrom_farthest_6",
            "nystrom_uniform_6",
            "pca_relu_6",
            "rbf",
            "rff_6",
            "spectral_6",
        ],
        "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
        "paired_models": [["nystrom_uniform_6", "rbf"]],
        "prediction_repeats": 2,
        "prediction_warmups": 1,
        "rff_seed": 2310,
    }
    result, _ = diagnostic.evaluate_development(
        X[:56],
        y[:56],
        X[56:],
        y[56:],
        config,
        37,
    )
    assert len(result["rows"]) == 10
    assert len(result["selected_rows"]) == 10
    assert all(row["test_accuracy"] is None for row in result["rows"])
    for row in result["selected_rows"]:
        assert row["model_state_bytes"] > 0
        assert (
            row["fit_time_with_oracle_selection_seconds"]
            >= row["fit_time_without_oracle_selection_seconds"]
        )
        assert row["validation_prediction_mean_seconds"] >= 0.0


def test_summary_efficiency_uses_rbf_reference():
    rows = [
        {
            "model": "rbf",
            "split_seed": 1,
            "validation_accuracy": 1.0,
            "validation_rmse": 0.0,
            "validation_r2": 1.0,
            "rank": 10,
            "feature_budget": 10,
            "readout_parameter_count": 20,
            "retained_train_samples": 10,
            "model_state_bytes": 1000,
            "intermediate_array_bytes_estimate": 2000,
            "build_peak_tracemalloc_bytes": 3000,
            "train_feature_construction_time_seconds": 1.0,
            "validation_feature_transform_time_seconds": 1.0,
            "readout_grid_solve_time_seconds": 1.0,
            "selected_readout_inference_mean_seconds": 1.0,
            "validation_prediction_mean_seconds": 2.0,
            "fit_time_without_oracle_selection_seconds": 1.0,
            "fit_time_with_oracle_selection_seconds": 2.0,
            "kernel_reconstruction_error": 0.0,
        },
        {
            "model": "small",
            "split_seed": 1,
            "validation_accuracy": 0.9,
            "validation_rmse": 0.1,
            "validation_r2": 0.8,
            "rank": 5,
            "feature_budget": 5,
            "readout_parameter_count": 10,
            "retained_train_samples": 5,
            "model_state_bytes": 250,
            "intermediate_array_bytes_estimate": 500,
            "build_peak_tracemalloc_bytes": 600,
            "train_feature_construction_time_seconds": 0.5,
            "validation_feature_transform_time_seconds": 0.25,
            "readout_grid_solve_time_seconds": 0.1,
            "selected_readout_inference_mean_seconds": 0.05,
            "validation_prediction_mean_seconds": 0.3,
            "fit_time_without_oracle_selection_seconds": 0.6,
            "fit_time_with_oracle_selection_seconds": 0.7,
            "kernel_reconstruction_error": 0.1,
        },
    ]
    report = diagnostic.aggregate([], rows, [["small", "rbf"]])
    assert np.isclose(report["efficiency_summary"]["small"]["accuracy_gap_to_rbf"]["mean"], 0.1)
    assert report["efficiency_summary"]["small"]["model_state_bytes_ratio_to_rbf"]["mean"] == 0.25
