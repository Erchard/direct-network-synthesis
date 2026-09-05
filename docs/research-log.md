# Research Log

## 2026-09-05: Accessibility Motivation Recorded

Added the long-term motivation to `docs/hypothesis.md`: direct synthesis could
lower the cost of creating strong models and broaden access beyond organizations
able to fund large training infrastructure. Recorded single-pass synthesis as an
unverified ambition and separated it from low total computation and energy cost.
Potential reductions in corporate concentration are conditional implications,
not findings; neither unnecessary data centers nor impossible monopoly follows
from the current evidence. No experiment, protocol change or novelty claim was
introduced by this documentation update.

## 2026-09-05: Full-Basis Diagnostic Result

Code/config/protocol commit: `f48c4edb7a0d32867801546440f84105e9e8454a`.
Worktree was clean at evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_depth_width --config configs/dns05_full_basis_digits.json --write-results --output results/dns05_full_basis_digits_summary.json
```

Complete auditable record: `docs/results/dns05_full_basis_digits_summary.json`.
It preserves all 45 model/split rows, exact configuration, oracle selections,
block diagnostics, sample standard deviations and paired differences for all
reported metrics. Five splits: 101, 202, 303, 404, 505. No parameter optimization.
This is a diagnostic reuse of digits, not an independent confirmation.

| Model | Test accuracy, mean +/- SD | Train kernel error, mean +/- SD | Rank / budget | Mean fit s | Mean inference s |
|---|---:|---:|---:|---:|---:|
| Linear ridge | 0.9328 +/- 0.0107 | n/a | 60.2 / 64 | 0.004 | <0.001 |
| RBF oracle | 0.9856 +/- 0.0077 | 0 | 1078 / 1078 | 0.083 | 0.013 |
| Deterministic ReLU | 0.9728 +/- 0.0084 | n/a | 252.2 / 256 | 0.043 | 0.001 |
| Spectral oracle 192 | 0.9489 +/- 0.0110 | 0.000355 +/- 0.000006 | 192 / 192 | 0.848 | 0.016 |
| One-shot 192 | 0.9389 +/- 0.0102 | 0.0321 +/- 0.0008 | 184.4 / 192 | 0.741 | 0.001 |
| Partitioned 2x96 | 0.9383 +/- 0.0117 | 0.0667 +/- 0.0029 | 184.4 / 192 | 1.054 | 0.004 |
| Partitioned 3x64 | 0.9356 +/- 0.0087 | 0.0904 +/- 0.0035 | 184.4 / 192 | 1.805 | 0.002 |
| Full-basis 2x96 | 0.9372 +/- 0.0099 | 0.0340 +/- 0.0009 | 184.4 / 192 | 1.445 | 0.002 |
| Full-basis 3x64 | 0.9383 +/- 0.0105 | 0.0368 +/- 0.0010 | 184.4 / 192 | 1.407 | 0.003 |

Paired differences (left minus right, mean +/- sample SD):

- Full-basis 2x96 minus one-shot: accuracy -0.001667 +/- 0.002485;
  kernel error +0.001938 +/- 0.000051.
- Full-basis 3x64 minus one-shot: accuracy -0.000556 +/- 0.001242;
  kernel error +0.004729 +/- 0.000125.
- Full-basis 2x96 minus partitioned 2x96: accuracy -0.001111 +/- 0.005760;
  kernel error -0.032676 +/- 0.002607.
- Full-basis 3x64 minus partitioned 3x64: accuracy +0.002778 +/- 0.003402.
- One-shot minus spectral oracle: accuracy -0.010000 +/- 0.005046.

Interpretation and limitations:

- Removing basis partitioning substantially reduces reconstruction error but
  does not outperform one-shot compilation. This is another negative outcome for
  sequential residual compilation with this fixed basis, not a rejection of DNS.
- All compiled variants have the same mean realized rank, 184.4. Full-basis
  projections have 36,864 coefficients, equal to one-shot, versus 18,432 / 12,288
  for partitioned 2 / 3 blocks. Block basis evaluations rise to 384 / 576.
- Spectral reconstruction is much better yet accuracy is only 0.9489 at fixed
  alpha 1.0. The full oracle selected alpha 0.001 or 0.01 and uses no intercept;
  therefore its accuracy gap cannot be attributed solely to truncation. The
  spectral reference is not an accuracy upper bound. Kernel Frobenius error alone
  is insufficient to assess task performance in this comparison.
- Kernel error here is train-only. Spectral inference retains 1,078 training
  examples. Output rank does not describe its storage/inference cost.
- Timings are noisy single measurements, with routine checks overlapping part of
  the run. Do not use these values for speedup claims; complete timing SDs remain
  in the record. No test rerun was used to improve timing numbers.
- Checks: Ruff passed; 10 tests passed, including a new unseen-input equivalence
  check showing that full-basis blocks collapse to one projection of the basis.

Next: preregister a validation-only diagnostic matching spectral/full-kernel
readout regularization and intercept, and compare direct readout on the same
PCA/quantile basis. These controls would separate readout effects from geometry
projection loss. Keep the previously inspected test partitions out of selection;
reserve independent data for any confirmatory claim. No novelty claim is made.

## 2026-09-05: Full-Basis Diagnostic Preregistered

Next comparison is fixed in `docs/dns05-full-basis-protocol.md` and
`configs/dns05_full_basis_digits.json`. Add full-basis residual projection and a
train-only rank-192 spectral reference. Retain all previous baselines and report
all paired outcomes. Code inspection establishes that the current residual blocks
share a fixed nonlinear basis and do not implement compositional neural depth.
This limits the interpretation of the earlier depth result. No novelty claim.

## 2026-09-05: Repository Scaffold

Created the initial reproducible research scaffold for Direct Network Synthesis.

Decisions:

- Use a Python `src/` package layout.
- Track strict train/validation/test separation from the beginning.
- Start with linear ridge, RBF kernel ridge, and deterministic ReLU-feature baselines.
- Add DNS 0.4 as an SVD-based direct feature synthesis prototype.
- Add DNS 0.5 Kernel Compiler as an initial weighted-kernel construction module.
- Avoid claims of novelty until evidence and related-work analysis justify stronger language.

Next experiments:

- Run the starter synthetic nonlinear regression benchmark.
- Add at least one real tabular regression dataset with fixed splits.
- Compare DNS 0.4 and DNS 0.5 against the minimum baseline set across all splits.

## 2026-09-05: Conceptual Foundations Captured

Added `docs/conceptual-foundations-uk.md` as the long-form conceptual memory of the project.

The document records:

- the reasoning path from market price discovery, evolutionary adaptation, and engineering
  design to the direct-synthesis hypothesis;
- the formal distinction between iterative parameter search and direct linear-algebraic
  computation;
- related research directions discussed so far, without making novelty claims;
- the evolution from DNS 0.1 through DNS 0.5, including failed hypotheses and the
  realizability insight;
- exploratory chat results with explicit warnings that they are not canonical until
  reproduced in the repository;
- current beliefs, unresolved questions, scaling criteria, and the immediate DNS 0.5 Kernel
  Compiler experiment plan.

Decision:

- Treat `docs/conceptual-foundations-uk.md` as the narrative research foundation.
- Keep `docs/hypothesis.md` concise and normative.
- Keep `docs/methodology.md` as the binding experimental protocol.
- Continue using this log as the chronological laboratory record.

## 2026-09-05: English Conceptual Foundations Added

Added `docs/conceptual-foundations-en.md` as a self-contained English-language version of the project's conceptual foundation for a broader technical audience.

The English version is not a literal translation. It preserves the same reasoning, epistemic labels, DNS 0.1–0.5 evolution, negative results, exploratory-number warnings, current beliefs, open questions, and the DNS 0.5 Kernel Compiler experiment plan, while using terminology and structure intended to be natural for international ML/engineering readers.

README navigation was updated to link both the English and Ukrainian conceptual documents.

## 2026-09-05: DNS 0.5 Depth-vs-Width Experiment Implemented

Implemented the first repository-native DNS 0.5 Kernel Compiler depth-vs-width experiment.

What is implemented:

- `DNS05CompiledFeatureClassifier`, which uses a train-only RBF oracle, spectral residual
  targets, deterministic PCA/quantile ReLU feature maps, closed-form ridge projections, and a
  closed-form ridge class readout.
- Stratified train/validation/test splitting for classification.
- `sklearn digits` experiment runner at `experiments/run_dns05_depth_width.py`.
- Fixed experiment config at `configs/dns05_depth_width_digits.json`.
- Reporting for validation/test accuracy, kernel reconstruction error, feature budget/rank,
  solve time, inference time, block diagnostics, oracle selections, and paired differences.

Important boundary:

- The earlier `DNS05KernelCompiler` remains only a weighted linear/RBF kernel combiner.
- The new classifier is the first actual residual RBF-geometry compiler in this repository.

Checks:

- `python -m ruff check .`
- `python -m pytest`

## 2026-09-05: DNS 0.5 Depth-vs-Width Result, 192 Features

Ran the first five-split `sklearn digits` DNS 0.5 depth-vs-width comparison.

Reproducibility record:

- Code/config commit: `40d781e4e5ad37cbad36962e0d7b6ad97c1b22e9`
- Config: `configs/dns05_depth_width_digits.json`
- Command: `D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_depth_width --write-results`
- Raw artifact: `results/dns05_depth_width_digits_summary.json` (ignored by Git)
- Split seeds: `101, 202, 303, 404, 505`
- Dataset: `sklearn digits`
- Oracle selection: train-fitted standardization, train-only median gamma base, validation
  grid over gamma multipliers `[0.5, 1.0, 2.0]` and alphas `[0.001, 0.01, 0.1]`
- Iterative parameter optimization: none in the evaluated models

Mean test accuracy across five splits:

| Model | Test accuracy | Kernel error | Rank / feature budget | Solve time | Inference time |
|---|---:|---:|---:|---:|---:|
| Linear ridge classifier | `0.9328 +/- 0.0107` | n/a | `60.2 / 64` | `0.001s` | `0.000s` |
| RBF kernel ridge oracle | `0.9856 +/- 0.0077` | `0.0000 +/- 0.0000` | `1078.0 / 1078` | `0.072s` | `0.012s` |
| Deterministic ReLU classifier | `0.9728 +/- 0.0084` | n/a | `252.2 / 256` | `0.010s` | `0.001s` |
| DNS05 one-shot, 192 features | `0.9389 +/- 0.0102` | `0.0321 +/- 0.0008` | `184.4 / 192` | `0.466s` | `0.001s` |
| DNS05 residual, 2x96 features | `0.9383 +/- 0.0117` | `0.0667 +/- 0.0029` | `184.4 / 192` | `0.757s` | `0.001s` |
| DNS05 residual, 3x64 features | `0.9356 +/- 0.0087` | `0.0904 +/- 0.0035` | `184.4 / 192` | `1.058s` | `0.002s` |

Paired differences:

- `dns05_residual_2x96 - dns05_one_shot_192`: test accuracy `-0.0006 +/- 0.0050`;
  kernel reconstruction error `+0.0346 +/- 0.0026`; solve time `+0.292s +/- 0.032s`.
- `dns05_residual_3x64 - dns05_one_shot_192`: test accuracy `-0.0033 +/- 0.0030`;
  kernel reconstruction error `+0.0583 +/- 0.0041`; solve time `+0.592s +/- 0.024s`.
- `dns05_one_shot_192 - rbf_kernel_ridge_oracle`: test accuracy
  `-0.0467 +/- 0.0087`; feature budget `-886.0`; inference time `-0.0104s`.
- `dns05_residual_3x64 - rbf_kernel_ridge_oracle`: test accuracy
  `-0.0500 +/- 0.0071`; feature budget `-886.0`; inference time `-0.0101s`.

Conclusion:

- This specific residual compiler configuration is a negative result for useful analytical
  depth.
- The one-shot 192-feature compiler reconstructs the RBF oracle kernel better than the
  residual 2-block and 3-block variants at the same total feature budget.
- The 3-block residual variant does not monotonically reduce reconstruction error across
  blocks; in all five splits, the third block increases error relative to the second block.
- Test accuracy does not improve with residual depth and remains far below the RBF oracle and
  deterministic ReLU baseline.
- No novelty or success claim is justified by this run.

Next scientifically justified steps:

- Diagnose whether the residual failure is caused by feature-basis partitioning, residual
  target clipping, projection regularization, or using kernel reconstruction rather than a
  task-weighted geometry objective.
- Add an ablation where each residual block receives the full 192-feature basis while the
  reported feature budget is treated separately from compiled rank, to isolate residual target
  decomposition from feature partitioning.
- Add a low-rank oracle spectral embedding readout upper bound for ranks matching the compiled
  models.
