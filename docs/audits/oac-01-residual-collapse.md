# OAC-01: Residual Compiler Collapse Audit

Status: local implementation audit; independent review pending.
Date: 2026-09-06.
Audited source: `57e529b6663b8340f3e524d781e76d726b6ffbf8`.
Task: OAC-01 in [Agent Task Catalog](../agent-task-catalog.md).
Operator: owner-authorized local coding agent; not an independent reproducer.

## Question and Boundary

Can the fitted `DNS05CompiledFeatureClassifier` be represented exactly by one
fixed nonlinear feature map and a linear readout, for both partitioned and
full-basis residual blocks?

Allowed inputs are source, documentation and synthetic unit fixtures. No benchmark
dataset or experimental train/validation/test partition was loaded or scored.
The fixtures below check algebra, not predictive performance. This audit does not
introduce a new model variant or rerun an experimental comparison.

## Source Mapping

In [dns05_kernel_compiler.py](../../src/dns/synthesis/dns05_kernel_compiler.py):

- `fit` builds `_PCAQuantileReLUFeatureMap` once, before the residual loop.
- `_interleaved_feature_partitions` selects columns of that map. `full_basis`
  replaces each selection with all its columns, without changing the map.
- Each `_CompiledResidualBlock` stores only column indices and projection weights.
- `transform` applies each stored projection directly to columns computed from
  the original input, then concatenates the outputs. It does not feed a block's
  output through a new nonlinear feature map for the next block.
- `decision_function` appends an intercept and applies a linear readout.

The existing `test_full_basis_residuals_keep_output_budget_and_collapse_to_fixed_basis`
already checked one full-basis embedding case. It did not cover partitioned bases,
uneven partitions, absorption of the final readout or zero-rank blocks.

## Derivation

Fix a fitted model and write its shared nonlinear feature row as `phi(x)`, of
width `m`. Preprocessing, PCA directions and thresholds are fixed at inference.
Let `S_b` select the columns for block `b`, and let its stored projection be
`P_b`. If the block emits `r_b` columns, `S_b P_b` has shape `m x r_b`.

```text
z_b(x) = phi(x) S_b P_b
C = [S_1 P_1 | S_2 P_2 | ... | S_B P_B]
z(x) = [z_1(x) | ... | z_B(x)] = phi(x) C
```

For full-basis blocks, `S_b` is the identity. For partitioned blocks it is a
column-selection matrix. Uneven partitions and zero-column block outputs do not
change the identity. With readout bias `a` and non-intercept weights `W`:

```text
scores(x) = a + z(x) W = a + phi(x) (C W)
```

Thus the block projections and readout can be absorbed into one matrix `C W`.
This holds for every admissible input of the fitted model in exact arithmetic,
not only its training rows. Floating-point evaluation can differ by rounding;
near tied scores, exact class-label equality is not guaranteed by an approximate
numeric comparison. The proof concerns score functions in exact arithmetic.

The compiled Gram matrix is also confined to the fixed basis:

```text
Z Z^T = Phi C C^T Phi^T
rank(Z) <= min(rank(Phi), sum_b r_b)
```

Residual synthesis chooses a positive-semidefinite metric `C C^T` within that
basis. Sequential construction can change this metric and fitted coefficients,
but it does not add a downstream nonlinear transformation.

## What This Does Not Prove

Absorbing a fitted readout is not the same operation as fitting a new ridge
readout directly on `Phi`. Ridge penalties on `W` and on `C W` generally differ,
and a rank-deficient `C` restricts attainable coefficients. The audit therefore
does not predict equality between one-shot and residual training outcomes or
claim equal validation accuracy. It establishes representational collapse of
the current fitted architecture.

The argument also does not show that every deep network collapses, that any
alternative compiler is cheap, or that gradients are necessary. It makes no
novelty claim. A proposed new architecture must be checked separately; dependence
of a later block on an earlier output alone is insufficient if all intervening
maps remain linear or simplify to a shared fixed basis.

## Verification Procedure

Tests in [test_synthesis.py](../../tests/test_synthesis.py) use recorded seeds
`260906` and `260907`, fixed before execution. Six cases cover both basis modes
and block counts 1, 3 and 5 at width 14, including uneven partitions. They compare
embeddings and final scores on fit inputs and separately generated query inputs,
using `rtol=1e-10`, `atol=1e-12`. Two further cases force an empty spectral target
with `eigensolver_eps=1e6` and check the resulting intercept-only behavior. This
deliberately extreme threshold is an edge fixture, not a recommended setting.

Commands from the repository root, using its existing virtual environment:

```text
.venv/Scripts/python.exe -m pytest tests/test_synthesis.py
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m ruff check .
git diff --check
```

Acceptance: source derivation and numeric checks agree for both implemented modes;
any discrepancy is reported before changing the model. All 12 synthesis tests
passed, including the eight new cases; the full suite passed all 50 tests, and
ruff passed. Environment: Windows 10 build 19045, Python 3.12.14 (AMD64),
NumPy 2.5.2, pytest 9.1.1. No discrepancy was observed at the stated tolerances.
No timing or energy claim is made from unit-test duration.

## Decision

Keep the current residual-depth branch paused. Its fitted inference function is
a single shared ReLU basis followed by a linear readout. For a new depth proposal,
require an explicit nonlinear composition mechanism and an algebraic check of
whether that proposal still collapses under the stated resource budget. Ordinary
linear algebra resolves this audit; category theory is not needed to establish
this particular limitation. Next pilot tasks remain provenance (OAC-03) and
deployed-state accounting (OAC-05), with independent review still outstanding.
