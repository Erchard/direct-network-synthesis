import numpy as np

from dns.synthesis import (
    DNS04Config,
    DNS04Synthesizer,
    DNS05CompiledFeatureClassifier,
    DNS05FeatureCompilerConfig,
    DNS05KernelCompiler,
    KernelSpec,
)


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


def test_dns05_compiled_feature_classifier_records_residual_diagnostics():
    rng = np.random.default_rng(55)
    X = rng.normal(size=(36, 6))
    y = (X[:, 0] + 0.5 * X[:, 1] > 0.0).astype(int)
    config = DNS05FeatureCompilerConfig(
        total_feature_count=12,
        block_count=3,
        projection_alpha=1e-5,
        readout_alpha=0.1,
    )

    model = DNS05CompiledFeatureClassifier(gamma=0.25, config=config).fit(X, y)
    predictions = model.predict(X[:5])

    assert predictions.shape == (5,)
    assert len(model.block_diagnostics_) == 3
    assert model.feature_budget_ == 12
    assert model.compiled_rank_ <= 12
    assert np.isfinite(model.kernel_reconstruction_error_)
    assert model.uses_iterative_parameter_optimization is False


def test_full_basis_residuals_keep_output_budget_and_collapse_to_fixed_basis():
    rng = np.random.default_rng(1705)
    X = rng.normal(size=(40, 6))
    y = (X[:, 0] > 0).astype(int)
    model = DNS05CompiledFeatureClassifier(config=DNS05FeatureCompilerConfig(
        total_feature_count=12, block_count=3, full_basis=True,
    )).fit(X, y)
    assert model.train_embedding_.shape[1] <= 12
    assert all(block.feature_indices.size == 12 for block in model.blocks_)
    assert all(block.projection_weights.shape[1] <= 4 for block in model.blocks_)
    new_X = rng.normal(size=(7, 6))
    basis = model.feature_map_.transform_columns(new_X, np.arange(12))
    combined = np.column_stack([block.projection_weights for block in model.blocks_])
    np.testing.assert_allclose(model.transform(new_X), basis @ combined, atol=1e-12)
    np.testing.assert_allclose(model.transform(X), model.train_embedding_, atol=1e-12)
