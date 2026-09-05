# Direct Network Synthesis

This repository is a reproducible research codebase for studying whether useful neural
network parameters or representations can be computed directly, without gradient-descent
weight updates.

The working phrase "Direct Network Synthesis" is a project label. This repository does not
claim novelty. Its purpose is to make the hypotheses, baselines, experiment protocol, and
negative results explicit enough to audit.

## Conceptual Foundations

The full reasoning history behind the project — from market price discovery, evolution, and
engineering design to the DNS 0.1–0.5 research program — is documented in Ukrainian in
[docs/conceptual-foundations-uk.md](docs/conceptual-foundations-uk.md).

That document preserves the evolution of the hypotheses, exploratory chat results, negative
results, epistemic status of claims, and the immediate DNS 0.5 Kernel Compiler experiment.
It is the project's long-form conceptual memory; `docs/hypothesis.md` and
`docs/methodology.md` remain the concise normative documents.

## Research Question

Can a neural model obtain competitive predictive performance when its hidden features,
kernels, or output weights are synthesized by deterministic or closed-form computations
rather than optimized by iterative backpropagation?

The first target is supervised regression on controlled benchmark problems. Classification
and larger datasets should be added only after the protocol is stable and baseline behavior
is understood.

## Current Hypotheses

1. Closed-form output layers over fixed or synthesized representations can be competitive on
   some structured problems.
2. Kernelized closed-form solvers provide a strong reference point for any DNS variant.
3. A DNS variant is only interesting if it improves over simple ridge, RBF kernel ridge, and
   deterministic ReLU-feature baselines under the same split and reporting rules.
4. Failures are useful results when they identify which part of the direct synthesis pipeline
   does not generalize.

## Experiment Protocol

The strict protocol lives in [docs/methodology.md](docs/methodology.md). The short version:

- Keep train, validation, and test data separate for every run.
- Use fixed, recorded seeds for data generation, splitting, and deterministic feature maps.
- Do not tune model choices, hyperparameters, preprocessing, or stopping criteria on the
  test set.
- Report mean and standard deviation across multiple fixed splits.
- Distinguish closed-form computation from iterative parameter optimization in every model
  description.

## Project Layout

```text
direct-network-synthesis/
├── configs/
├── docs/
├── experiments/
├── results/
├── src/
│   └── dns/
│       ├── baselines/
│       ├── features/
│       ├── kernels/
│       ├── metrics/
│       └── synthesis/
└── tests/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Run Checks

```bash
python -m pytest
```

## Run the Starter Experiment

```bash
python -m experiments.run_baselines
```

To write a JSON summary under `results/`:

```bash
python -m experiments.run_baselines --write-results
```

Generated result files are intentionally ignored by Git. Commit only curated summaries,
protocol changes, or result notes that are needed for reproducibility.

## Initial Models

- `LinearRidgeRegressor`: closed-form primal ridge regression.
- `RBFKernelRidgeRegressor`: closed-form dual ridge regression with an RBF kernel and
  train-only median heuristic when `gamma` is not specified.
- `DeterministicReLUBaseline`: fixed seeded ReLU features with a closed-form ridge readout.
- `DNS04Synthesizer`: initial SVD-based direct feature synthesis prototype.
- `DNS05KernelCompiler`: initial weighted kernel compiler for closed-form kernel solvers.

## Research Log

The running log is in [docs/research-log.md](docs/research-log.md). Add short entries for
every experiment, including abandoned ideas and failed hypotheses.
