import numpy as np
import pytest

from dns.synthesis.linear_algebra import solve_primal_ridge
from experiments import run_dns05_readout as diagnostic


@pytest.mark.parametrize("intercept", [False, True])
def test_kernel_readout_matches_primal_on_unseen_inputs(intercept):
    rng = np.random.default_rng(71)
    train = rng.normal(size=(23, 7)) + 2
    new = rng.normal(size=(9, 7)) - 1
    targets = rng.normal(size=(23, 3)) + 3
    weights = solve_primal_ridge(train, targets, alpha=0.1, fit_intercept=intercept)
    design = np.column_stack([np.ones(9), new]) if intercept else new
    scores, _, _ = diagnostic.kernel_readout(
        train @ train.T, targets, new @ train.T, 0.1, intercept
    )
    np.testing.assert_allclose(scores, design @ weights, atol=1e-10)


def test_runner_never_passes_excluded_samples_to_evaluation(monkeypatch):
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
    monkeypatch.setattr(diagnostic, "aggregate", lambda rows: {})
    result = diagnostic.run(
        {"splits": {"split_seeds": [101], "train_fraction": 0.6, "validation_fraction": 0.2}}
    )
    assert calls == [101]
    assert result["test_status"] == "not_evaluated"


def test_synthetic_development_grid_and_test_fields():
    rng = np.random.default_rng(79)
    X = rng.normal(size=(42, 5))
    y = (X[:, 0] > 0).astype(int)
    rows, _ = diagnostic.evaluate_development(
        X[:30],
        y[:30],
        X[30:],
        y[30:],
        {
            "feature_count": 8,
            "relu_seed": 1705,
            "alphas": [0.01, 1.0],
            "intercepts": [False, True],
            "oracle_selection": {"gamma_multipliers": [1.0], "alpha_values": [0.01]},
        },
        79,
    )
    assert len(rows) == 24
    assert all(r["test_accuracy"] is None and r["test_rmse"] is None for r in rows)
    report = diagnostic.aggregate(rows)
    assert len(report["selected_rows"]) == 6
    assert all(np.isfinite(r["validation_rmse"]) for r in rows)
