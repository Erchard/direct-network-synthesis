import numpy as np

from dns.synthesis import DNS04Config, DNS04Synthesizer, DNS05KernelCompiler, KernelSpec


def test_dns04_synthesizer_predicts_and_declares_closed_form_rule():
    rng = np.random.default_rng(321)
    X = rng.normal(size=(30, 5))
    y = np.sin(X[:, 0]) + X[:, 1]

    model = DNS04Synthesizer(DNS04Config(feature_count=3, alpha=0.1)).fit(X, y)
    predictions = model.predict(X[:4])

    assert predictions.shape == (4,)
    assert "closed_form" in model.synthesis_rule
    assert model.uses_iterative_parameter_optimization is False


def test_dns05_kernel_compiler_produces_symmetric_train_kernel():
    rng = np.random.default_rng(99)
    X = rng.normal(size=(12, 4))
    compiler = DNS05KernelCompiler(
        [
            KernelSpec("linear", weight=0.25),
            KernelSpec("rbf", weight=0.75),
        ]
    )

    gram = compiler.kernel_matrix(X, X_reference=X)

    assert gram.shape == (12, 12)
    np.testing.assert_allclose(gram, gram.T, atol=1e-12)
    assert np.all(np.diag(gram) > 0.0)
