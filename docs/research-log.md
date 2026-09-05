# Research Log

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
