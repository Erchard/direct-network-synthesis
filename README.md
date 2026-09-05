# Direct Network Synthesis

This repository is a reproducible research codebase for studying whether useful neural
network parameters or representations can be computed directly, without gradient-descent
weight updates.

The working phrase "Direct Network Synthesis" is a project label. This repository does not
claim novelty. Its purpose is to make the hypotheses, baselines, experiment protocol, and
negative results explicit enough to audit.

## Conceptual Foundations

The project's long-form reasoning history — from market price discovery, evolution, and
engineering design to the DNS 0.1–0.5 research program — is available in two versions:

- [English: Conceptual Foundations of Direct Network Synthesis](docs/conceptual-foundations-en.md)
- [Українською: Концептуальні засади Direct Network Synthesis](docs/conceptual-foundations-uk.md)

The English document is written as a self-contained introduction for a broad technical
audience. Both versions preserve the evolution of the hypotheses, exploratory chat results,
negative results, epistemic status of claims, and the immediate DNS 0.5 Kernel Compiler
experiment.

These documents are the project's long-form conceptual memory; `docs/hypothesis.md` and
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

The [research plan](docs/research-plan.md) sets out the next DNS diagnostics,
evidence gates, resource measurements and eventual independent reproduction of
an affordable model. It connects the experiments to the long-term accessibility
objective without treating that objective as an established result.

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

## Run the DNS 0.5 Depth-vs-Width Experiment

```bash
python -m experiments.run_dns05_depth_width
```

To write the raw JSON summary under `results/`:

```bash
python -m experiments.run_dns05_depth_width --write-results
```

This `sklearn digits` classification experiment selects the RBF oracle bandwidth and ridge
regularization on validation data for each fixed split, then compares the locked oracle,
closed-form baselines, a one-shot compiled feature model, and residual multi-block compiled
models at the same total feature budget.

## Initial Models

The next preregistered diagnostic is described in
[Full-Basis Protocol](docs/dns05-full-basis-protocol.md). Run it with:

```bash
python -m experiments.run_dns05_depth_width --config configs/dns05_full_basis_digits.json --write-results --output results/dns05_full_basis_digits_summary.json
```

It adds full-basis residual blocks and a rank-192 spectral oracle reference.
Curated complete result records are stored under `docs/results/`.

The matched-readout validation diagnostic is preregistered in
[DNS05 Readout Protocol](docs/dns05-readout-protocol.md) and tracked in
[Experiment Register](docs/experiment-register.md). Run it with:

```bash
python -m experiments.run_dns05_readout --config configs/dns05_readout_digits.json --output results/dns05_readout_digits.json
```

It reuses the digits development splits only, compares six representations under
the same closed-form readout grid, and records null test fields by design.
The complete validation-only record is stored at
`docs/results/dns05_readout_digits.json`.

The next landmark geometry diagnostic is locked in
[DNS05 Landmark Protocol](docs/dns05-landmark-protocol.md), with related-work
notes in [Kernel Approximation Related Work](docs/related-work-kernel-approximations.md).
Run it with:

```bash
python -m experiments.run_dns05_landmark --config configs/dns05_landmark_digits.json --output results/dns05_landmark_digits.json
```

It tests whether uniform, farthest-first, class-balanced farthest-first Nystrom
landmarks or random Fourier features explain the gap between the compiler and the
compact spectral RBF reference. It is validation-only and records null test fields.
The complete validation-only record is stored at
`docs/results/dns05_landmark_digits.json`.

The error geometry diagnostic is locked in
[DNS05 Error Geometry Protocol](docs/dns05-error-geometry-protocol.md). Run it
with:

```bash
python -m experiments.run_dns05_error_geometry --config configs/dns05_error_geometry_digits.json --output results/dns05_error_geometry_digits.json
```

It records per-validation-sample predictions, neighbor geometry and landmark
coverage for already selected development models. It is validation-only and
does not compute test scores.
The complete validation-only record is stored at
`docs/results/dns05_error_geometry_digits.json`.

The cost-accounted compression diagnostic is locked in
[DNS05 Cost Protocol](docs/dns05-cost-protocol.md). Run it with:

```bash
python -m experiments.run_dns05_cost --config configs/dns05_cost_digits.json --output results/dns05_cost_digits.json
```

It records validation-only accuracy together with construction time, readout
selection time, retained samples, approximate model-state bytes and repeated
validation prediction timing. It does not compute test scores or energy use.
The complete validation-only record is stored at
`docs/results/dns05_cost_digits.json`.

- `LinearRidgeRegressor`: closed-form primal ridge regression.
- `RBFKernelRidgeRegressor`: closed-form dual ridge regression with an RBF kernel and
  train-only median heuristic when `gamma` is not specified.
- `DeterministicReLUBaseline`: fixed seeded ReLU features with a closed-form ridge readout.
- `DNS04Synthesizer`: initial SVD-based direct feature synthesis prototype.
- `DNS05KernelCompiler`: initial weighted kernel compiler for closed-form kernel solvers.
- `DNS05CompiledFeatureClassifier`: residual spectral RBF-geometry compiler for the DNS 0.5
  depth-vs-width classification experiment.

## AI Contributors

AI agents joining the project should start with [AGENTS.md](AGENTS.md) and the
[AI contributor guide](docs/ai-contributor-guide.md). These documents explain the
reading order, evidence boundaries, contribution workflow and handoff requirements.

## Research Log

The running log is in [docs/research-log.md](docs/research-log.md). Add short entries for
every experiment, including abandoned ideas and failed hypotheses.
