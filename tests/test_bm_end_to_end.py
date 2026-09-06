import json
from pathlib import Path

import numpy as np

from experiments import run_dns05_bm_end_to_end as runner


def test_batch_stream_grid_equivalence_on_synthetic_inputs(monkeypatch):
    monkeypatch.setattr(runner, "memory", lambda: {"peak_rss_bytes": 1, "rss_bytes": 1})
    cfg = json.loads(runner.CONFIG.read_text())
    cfg.update(feature_budget=7, block_size=9, repeats=1)
    base = json.loads(Path(cfg["base_config"]).read_text())
    rng = np.random.default_rng(82001)
    train, validation = rng.normal(size=(35, 4)), rng.normal(size=(13, 4))
    labels, validation_labels = np.arange(35) % 3, np.arange(13) % 3
    batch = runner.evaluate(train, labels, validation, validation_labels, 82001, "batch", cfg, base)
    stream = runner.evaluate(train, labels, validation, validation_labels, 82001, "stream", cfg, base)
    for left, right in zip(batch["grid"], stream["grid"], strict=True):
        np.testing.assert_allclose(left["weights"], right["weights"], rtol=1e-8, atol=1e-10)
        np.testing.assert_allclose(left["scores"], right["scores"], rtol=1e-8, atol=1e-10)
    assert stream["test_accuracy"] is None
    assert stream["training_feature_passes"] == 8


def test_worker_only_passes_declared_development_rows(monkeypatch):
    cfg = json.loads(runner.CONFIG.read_text())
    base = json.loads(Path(cfg["base_config"]).read_text())
    X = np.arange(60).reshape(20, 3)
    y = np.arange(20) % 2
    monkeypatch.setattr(runner, "load_audit_dataset", lambda _: (X, y, {}))
    monkeypatch.setattr(runner, "stratified_train_validation_test_split",
                        lambda *a, **kw: (np.arange(10), np.arange(10, 15), np.arange(15, 20)))

    def check(train, labels, validation, validation_labels, *args):
        np.testing.assert_array_equal(train, X[:10])
        np.testing.assert_array_equal(validation, X[10:15])
        return {}

    monkeypatch.setattr(runner, "evaluate", check)
    result = runner.worker("sklearn_digits", 101, "stream", cfg, base)
    assert result["excluded_indices"] == list(range(15, 20))
