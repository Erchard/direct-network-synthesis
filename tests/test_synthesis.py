from itertools import pairwise

import numpy as np
import pytest

from dns.synthesis import (
    DNS04Config,
    DNS04Synthesizer,
    DNS05CompiledFeatureClassifier,
    DNS05FeatureCompilerConfig,
    DNS05KernelCompiler,
    KernelSpec,
)
from dns.synthesis.linear_algebra import solve_primal_ridge, solve_streaming_primal_ridge


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


@pytest.mark.parametrize("fit_intercept", [False, True])
def test_streaming_primal_ridge_matches_batch_solution(fit_intercept):
    rng = np.random.default_rng(260908)
    features = rng.normal(size=(23, 5))
    targets = rng.normal(size=(23, 3))
    boundaries = [0, 4, 11, 17, len(features)]
    feature_blocks = (features[start:end] for start, end in pairwise(boundaries))
    target_blocks = (targets[start:end] for start, end in pairwise(boundaries))

    expected = solve_primal_ridge(features, targets, alpha=0.3, fit_intercept=fit_intercept)
    actual = solve_streaming_primal_ridge(
        feature_blocks,
        target_blocks,
        alpha=0.3,
        fit_intercept=fit_intercept,
    )

    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)


def test_streaming_primal_ridge_rejects_mismatched_block_lengths():
    with pytest.raises(ValueError, match="same number of samples"):
        solve_streaming_primal_ridge(
            [np.ones((2, 3))],
            [np.ones((1, 1))],
            alpha=0.1,
        )


@pytest.mark.parametrize("block_size", [1, 7, 64])
@pytest.mark.parametrize("fit_intercept", [False, True])
def test_streaming_ridge_with_singular_features(block_size, fit_intercept):
    rng = np.random.default_rng(260909)
    column = rng.normal(size=(31, 1))
    features = np.column_stack([column, column, np.zeros_like(column)])
    targets = rng.normal(size=31)
    expected = solve_primal_ridge(features, targets, alpha=0, fit_intercept=fit_intercept)
    actual = solve_streaming_primal_ridge(
        (features[i:i + block_size] for i in range(0, 31, block_size)),
        (targets[i:i + block_size] for i in range(0, 31, block_size)),
        alpha=0,
        fit_intercept=fit_intercept,
    )
    np.testing.assert_allclose(actual, expected, rtol=1e-8, atol=1e-10)


def test_streaming_ridge_rejects_unequal_iterator_lengths():
    with pytest.raises(ValueError):
        solve_streaming_primal_ridge([np.ones((2, 3))], [], alpha=0.1)


def test_streaming_ridge_rejects_empty_input():
    with pytest.raises(ValueError, match="non-empty"):
        solve_streaming_primal_ridge([], [], alpha=0.1)


def test_streaming_ridge_rejects_changed_width():
    with pytest.raises(ValueError, match="consistent"):
        solve_streaming_primal_ridge(
            [np.ones((2, 3)), np.ones((2, 4))],
            [np.ones(2), np.ones(2)], alpha=0.1,
        )


@pytest.mark.parametrize("seed", [260910, 260911, 260912, 260913, 260914])
@pytest.mark.parametrize("fit_intercept", [False, True])
def test_streamed_nystrom_blocks_preserve_query_scores(seed, fit_intercept):
    from dns.kernels import rbf_kernel
    from experiments.run_dns05_landmark import _inverse_square_root_psd

    rng = np.random.default_rng(seed)
    train = rng.normal(size=(79, 6))
    query = rng.normal(size=(17, 6))
    targets = np.eye(3)[np.arange(79) % 3]
    centers = train[rng.choice(len(train), 13, replace=False)]
    inverse_root, _ = _inverse_square_root_psd(rbf_kernel(centers, gamma=0.2))
    features = rbf_kernel(train, centers, gamma=0.2) @ inverse_root
    query_features = rbf_kernel(query, centers, gamma=0.2) @ inverse_root
    design = (
        np.column_stack([np.ones(len(query)), query_features])
        if fit_intercept else query_features
    )
    for alpha in [0.001, 0.01, 0.1, 1.0]:
        batch = solve_primal_ridge(features, targets, alpha=alpha, fit_intercept=fit_intercept)
        for block_size in [1, 7, 64, 256]:
            streamed = solve_streaming_primal_ridge(
                (rbf_kernel(train[i:i + block_size], centers, gamma=0.2) @ inverse_root
                 for i in range(0, len(train), block_size)),
                (targets[i:i + block_size] for i in range(0, len(train), block_size)),
                alpha=alpha, fit_intercept=fit_intercept,
            )
            np.testing.assert_allclose(streamed, batch, rtol=1e-8, atol=1e-10)
            np.testing.assert_allclose(design @ streamed, design @ batch, rtol=1e-8, atol=1e-10)


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


@pytest.mark.parametrize("full_basis", [False, True])
@pytest.mark.parametrize("block_count", [1, 3, 5])
def test_residual_blocks_and_readout_collapse_on_unseen_inputs(full_basis, block_count):
    rng = np.random.default_rng(260906)
    train_X = rng.normal(size=(40, 6))
    train_y = (train_X[:, 0] + train_X[:, 1] > 0).astype(int)
    model = DNS05CompiledFeatureClassifier(
        gamma=0.25,
        config=DNS05FeatureCompilerConfig(
            total_feature_count=14,
            block_count=block_count,
            full_basis=full_basis,
            projection_alpha=1e-5,
            readout_alpha=0.1,
        ),
    ).fit(train_X, train_y)

    # Scatter each local projection into the shared basis, including uneven partitions.
    lifted = []
    for block in model.blocks_:
        weights = np.zeros((14, block.projection_weights.shape[1]))
        weights[block.feature_indices] = block.projection_weights
        lifted.append(weights)
    combined = np.column_stack(lifted)
    collapsed_readout = combined @ model.readout_weights_[1:]
    query_X = rng.normal(size=(13, 6))

    for X in (train_X, query_X):
        basis = model.feature_map_.transform_columns(X, np.arange(14))
        np.testing.assert_allclose(
            model.transform(X), basis @ combined, rtol=1e-10, atol=1e-12,
        )
        np.testing.assert_allclose(
            model.decision_function(X),
            model.readout_weights_[0] + basis @ collapsed_readout,
            rtol=1e-10,
            atol=1e-12,
        )


@pytest.mark.parametrize("full_basis", [False, True])
def test_zero_rank_residual_blocks_collapse_to_intercept_only(full_basis):
    rng = np.random.default_rng(260907)
    train_X = rng.normal(size=(20, 4))
    train_y = np.arange(20) % 2
    model = DNS05CompiledFeatureClassifier(
        gamma=0.25,
        config=DNS05FeatureCompilerConfig(
            total_feature_count=7,
            block_count=3,
            full_basis=full_basis,
            eigensolver_eps=1e6,
        ),
    ).fit(train_X, train_y)
    query_X = rng.normal(size=(5, 4))
    assert model.transform(query_X).shape == (5, 0)
    assert model.readout_weights_.shape == (1, 2)
    np.testing.assert_allclose(
        model.decision_function(query_X),
        np.broadcast_to(model.readout_weights_[0], (5, 2)),
        rtol=1e-10,
        atol=1e-12,
    )
