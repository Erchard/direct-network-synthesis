import numpy as np

from dns.baselines import DeterministicReLUBaseline, LinearRidgeRegressor, RBFKernelRidgeRegressor


def test_linear_ridge_recovers_simple_linear_signal():
    X = np.arange(12, dtype=float).reshape(6, 2)
    y = 2.0 * X[:, 0] - 0.5 * X[:, 1] + 1.0

    model = LinearRidgeRegressor(alpha=0.0).fit(X, y)
    predictions = model.predict(X)

    assert np.max(np.abs(predictions - y)) < 1e-10
    assert model.uses_iterative_parameter_optimization is False


def test_rbf_kernel_ridge_predicts_training_shape():
    X = np.linspace(-1.0, 1.0, 8).reshape(-1, 1)
    y = np.sin(X[:, 0])

    model = RBFKernelRidgeRegressor(alpha=1e-6).fit(X, y)
    predictions = model.predict(X)

    assert predictions.shape == y.shape
    assert model.gamma_ > 0.0
    assert model.uses_iterative_parameter_optimization is False


def test_deterministic_relu_baseline_is_repeatable():
    rng = np.random.default_rng(123)
    X = rng.normal(size=(20, 3))
    y = X[:, 0] ** 2 - X[:, 1]

    first = DeterministicReLUBaseline(hidden_units=12, alpha=0.1, seed=7).fit(X, y)
    second = DeterministicReLUBaseline(hidden_units=12, alpha=0.1, seed=7).fit(X, y)

    np.testing.assert_allclose(first.predict(X), second.predict(X))
    assert first.uses_iterative_parameter_optimization is False
