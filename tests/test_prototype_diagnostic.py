import numpy as np

from experiments import run_dns05_prototype as diagnostic


def test_class_pca_prototypes_have_requested_count_without_raw_samples():
    rng = np.random.default_rng(41)
    X = rng.normal(size=(60, 5))
    y = np.repeat([0, 1, 2], 20)
    centers = diagnostic.class_pca_prototypes(X, y, 18, [0.25, 0.5, 0.75])
    assert centers.shape == (18, 5)
    assert diagnostic._exact_train_match_count(X, centers) == 0


def test_global_pca_prototypes_are_deterministic():
    rng = np.random.default_rng(43)
    X = rng.normal(size=(30, 4))
    first = diagnostic.global_pca_prototypes(X, 12, [0.1, 0.5, 0.9])
    second = diagnostic.global_pca_prototypes(X, 12, [0.1, 0.5, 0.9])
    np.testing.assert_allclose(first, second)


def test_prototype_runner_never_passes_excluded_samples_to_evaluation(monkeypatch):
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


def test_synthetic_prototype_grid_and_metadata():
    rng = np.random.default_rng(47)
    X = rng.normal(size=(72, 5))
    y = np.tile([0, 1, 2, 3], 18)
    rows, _ = diagnostic.evaluate_development(
        X[:56],
        y[:56],
        X[56:],
        y[56:],
        {
            "alphas": [0.01],
            "compiled_feature_count": 6,
            "fixed_relu_hidden_units": 6,
            "fixed_relu_seed": 1705,
            "intercepts": [False],
            "landmark_counts": [6],
            "landmark_seed": 2309,
            "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
            "prototype_quantiles": [0.25, 0.5, 0.75],
            "rff_seed": 2310,
        },
        47,
    )
    assert len(rows) == 12
    models = {row["model"] for row in rows}
    assert "prototype_global_pca_6" in models
    assert "prototype_class_pca_6" in models
    assert all(row["test_status"] == "not_evaluated" for row in rows)
    prototype_rows = [row for row in rows if row["model"].startswith("prototype_")]
    assert all(row["retained_train_samples"] == 0 for row in prototype_rows)
    assert all(row["prototype_count"] == 6 for row in prototype_rows)
