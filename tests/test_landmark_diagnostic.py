import numpy as np

from experiments import run_dns05_landmark as diagnostic


def test_nystrom_reconstructs_landmark_kernel():
    rng = np.random.default_rng(13)
    X = rng.normal(size=(18, 4))
    indices = np.array([0, 3, 6, 9, 12, 15])
    features, rank = diagnostic.nystrom_features(X, X[indices], gamma=0.2)
    landmark_approx = features[indices] @ features[indices].T
    np.testing.assert_allclose(
        landmark_approx,
        diagnostic.rbf_kernel(X[indices], gamma=0.2),
        atol=1e-10,
    )
    assert rank == len(indices)


def test_farthest_first_is_deterministic_and_unique():
    X = np.array([[0.0], [1.0], [2.0], [10.0], [11.0], [12.0]])
    first = diagnostic.farthest_first_indices(X, 4)
    second = diagnostic.farthest_first_indices(X, 4)
    np.testing.assert_array_equal(first, second)
    assert len(np.unique(first)) == 4


def test_landmark_runner_never_passes_excluded_samples_to_evaluation(monkeypatch):
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
        return [], {}

    monkeypatch.setattr(diagnostic, "evaluate_development", evaluate)
    monkeypatch.setattr(diagnostic, "aggregate", lambda rows, pair_specs: {})
    result = diagnostic.run(
        {
            "dataset": {"name": "sklearn_digits"},
            "paired_models": [],
            "splits": {"split_seeds": [101], "train_fraction": 0.6, "validation_fraction": 0.2},
        }
    )
    assert calls == [101]
    assert result["test_status"] == "not_evaluated"


def test_synthetic_landmark_grid_and_test_fields():
    rng = np.random.default_rng(17)
    X = rng.normal(size=(64, 5))
    y = np.tile([0, 1, 2, 3], 16)
    rows, _ = diagnostic.evaluate_development(
        X[:48],
        y[:48],
        X[48:],
        y[48:],
        {
            "alphas": [0.01],
            "compiled_feature_count": 6,
            "fixed_relu_hidden_units": 6,
            "intercepts": [False],
            "landmark_counts": [6],
            "landmark_seed": 2309,
            "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
            "rff_seed": 2310,
        },
        17,
    )
    assert len(rows) == 10
    assert {r["model"] for r in rows} == {
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
    }
    assert all(r["test_accuracy"] is None and r["test_status"] == "not_evaluated" for r in rows)
    class_rows = [r for r in rows if r["model"] == "nystrom_class_farthest_6"]
    assert class_rows[0]["uses_train_labels_for_representation"]
