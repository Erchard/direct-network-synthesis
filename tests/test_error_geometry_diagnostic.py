import numpy as np

from experiments import run_dns05_error_geometry as diagnostic


def test_error_tags_capture_pair_direction():
    predictions = {
        "compiled_192": {"correct": False},
        "spectral_192": {"correct": True},
        "nystrom_uniform_192": {"correct": True},
        "nystrom_farthest_192": {"correct": False},
        "fixed_relu_256": {"correct": True},
        "rbf": {"correct": True},
    }
    tags = diagnostic._tags(predictions)
    assert "compiled_192_miss_spectral_192_hit" in tags
    assert "compiled_192_miss_nystrom_uniform_192_hit" in tags
    assert "compiled_192_miss_fixed_relu_256_hit" in tags
    assert "compiled_192_miss_nystrom_farthest_192_hit" not in tags


def test_error_tags_accept_configured_pairs():
    predictions = {
        "prototype_class_pca_192": {"correct": False},
        "prototype_class_dipole_192": {"correct": True},
        "nystrom_uniform_192": {"correct": True},
    }
    tags = diagnostic._tags(
        predictions,
        [
            ["prototype_class_pca_192", "prototype_class_dipole_192"],
            ["prototype_class_dipole_192", "nystrom_uniform_192"],
        ],
    )
    assert "prototype_class_pca_192_miss_prototype_class_dipole_192_hit" in tags
    assert "prototype_class_dipole_192_miss_nystrom_uniform_192_hit" not in tags


def test_neighbor_records_capture_local_boundary():
    y_train = np.array([0, 0, 1, 1])
    y_validation = np.array([0, 1])
    cross = np.array(
        [
            [0.9, 0.7, 0.8, 0.1],
            [0.2, 0.3, 0.4, 0.95],
        ]
    )
    records = diagnostic._neighbor_records(cross, y_train, y_validation, k=2)
    assert records[0]["nearest_train_label"] == 0
    assert np.isclose(records[0]["same_minus_other_similarity_margin"], 0.1)
    assert records[0]["top_k_true_class_fraction"] == 0.5
    assert records[1]["nearest_train_label"] == 1
    assert np.isclose(records[1]["same_minus_other_similarity_margin"], 0.65)


def test_error_runner_never_passes_excluded_samples_to_evaluation(monkeypatch):
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
        return {"rows": [], "selected_rows": [], "sample_records": []}, {}

    monkeypatch.setattr(diagnostic, "evaluate_development", evaluate)
    monkeypatch.setattr(
        diagnostic,
        "aggregate",
        lambda rows, selected_rows, sample_records, config: {},
    )
    result = diagnostic.run(
        {
            "dataset": {"name": "sklearn_digits"},
            "splits": {"split_seeds": [101], "train_fraction": 0.6, "validation_fraction": 0.2},
        }
    )
    assert calls == [101]
    assert result["test_status"] == "not_evaluated"


def test_synthetic_error_geometry_grid_and_samples():
    rng = np.random.default_rng(29)
    X = rng.normal(size=(72, 5))
    y = np.tile([0, 1, 2, 3], 18)
    config = {
        "alphas": [0.01],
        "analysis_pairs": [["compiled_6", "spectral_6"]],
        "compiled_feature_count": 6,
        "diagnostic_landmark_count": 6,
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
        "neighbor_k": 3,
        "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
        "rff_seed": 2310,
    }
    result, _ = diagnostic.evaluate_development(
        X[:56],
        y[:56],
        X[56:],
        y[56:],
        config,
        29,
    )
    assert len(result["rows"]) == 10
    assert len(result["selected_rows"]) == 10
    assert len(result["sample_records"]) == 16
    assert all(row["test_accuracy"] is None for row in result["rows"])
    sample = result["sample_records"][0]
    assert set(sample["predictions"]) == set(config["models"])
    assert "same_minus_other_similarity_margin" in sample
    assert set(sample["landmark_coverage"]) == {
        "nystrom_class_farthest_6",
        "nystrom_farthest_6",
        "nystrom_uniform_6",
    }


def test_error_geometry_can_audit_prototypes():
    rng = np.random.default_rng(31)
    X = rng.normal(size=(72, 5))
    y = np.tile([0, 1, 2, 3], 18)
    config = {
        "alphas": [0.01],
        "analysis_pairs": [["prototype_class_pca_6", "prototype_class_dipole_6"]],
        "compiled_feature_count": 6,
        "diagnostic_landmark_count": 6,
        "dipole_shift_fraction": 0.25,
        "fixed_relu_hidden_units": 6,
        "fixed_relu_seed": 1705,
        "include_dipole_prototypes": True,
        "include_prototype_representations": True,
        "intercepts": [False],
        "landmark_counts": [6],
        "landmark_seed": 2309,
        "models": [
            "linear",
            "fixed_relu_11",
            "prototype_class_pca_6",
            "prototype_class_dipole_6",
            "nystrom_uniform_6",
            "rbf",
        ],
        "neighbor_k": 3,
        "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
        "prototype_quantiles": [0.25, 0.5, 0.75],
        "rff_seed": 2310,
    }
    result, _ = diagnostic.evaluate_development(
        X[:56],
        y[:56],
        X[56:],
        y[56:],
        config,
        31,
    )
    assert len(result["rows"]) == 6
    assert len(result["selected_rows"]) == 6
    assert len(result["sample_records"]) == 16
    sample = result["sample_records"][0]
    assert "prototype_class_pca_6" in sample["predictions"]
    assert "prototype_class_dipole_6" in sample["predictions"]
    dipole_row = next(
        row for row in result["selected_rows"] if row["model"] == "prototype_class_dipole_6"
    )
    assert dipole_row["prototype_count"] == 6
    assert dipole_row["prototype_train_exact_match_count"] == 0
