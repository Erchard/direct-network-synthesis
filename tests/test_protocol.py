from pathlib import Path

import numpy as np

from dns.features import train_validation_test_split
from experiments.run_baselines import load_config, run


def test_train_validation_test_split_is_disjoint():
    train, validation, test = train_validation_test_split(50, seed=42)

    assert set(train).isdisjoint(validation)
    assert set(train).isdisjoint(test)
    assert set(validation).isdisjoint(test)
    assert len(train) + len(validation) + len(test) == 50


def test_starter_experiment_reports_all_required_models():
    config = load_config(Path("configs/default_experiment.json"))
    config["dataset"]["n_samples"] = 80
    config["splits"]["split_seeds"] = [11, 22]
    result = run(config)

    expected = {
        "linear_ridge",
        "rbf_kernel_ridge",
        "deterministic_relu",
        "dns04_svd_relu",
        "dns05_compiled_kernel",
    }
    assert set(result["summary"]) == expected
    for model_summary in result["summary"].values():
        assert model_summary["n_splits"] == 2
        assert model_summary["uses_iterative_parameter_optimization"] is False
        assert np.isfinite(model_summary["metrics"]["test_rmse"]["mean"])
