# Research Log

## 2026-09-05: Error Geometry Diagnostic Result

Protocol/code commit: `c3c8a01593e0d20bc561e10555247d0acc2447a0`.
Worktree was clean at evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_error_geometry --config configs/dns05_error_geometry_digits.json --output results/dns05_error_geometry_digits.json
```

Complete auditable record: `docs/results/dns05_error_geometry_digits.json`.
The run produced 400 validation-only readout rows, 50 selected model/split rows
and 1795 per-validation-sample records. Test fields are null by design; this is
not independent confirmation evidence.

Selected validation accuracy matched the previous landmark diagnostic:
compiled 192 was 0.9638 +/- 0.0044, uniform Nystrom 192 was
0.9833 +/- 0.0048, spectral 192 was 0.9900 +/- 0.0042 and full RBF was
0.9916 +/- 0.0028.

Per-split diagnostic tags:

| Tag | Mean count +/- SD |
|---|---:|
| All selected models correct | 326.0 +/- 4.5 |
| All selected models wrong | 0.8 +/- 0.8 |
| Compiled miss / spectral hit | 10.2 +/- 1.6 |
| Compiled miss / uniform Nystrom hit | 9.6 +/- 2.1 |
| Compiled miss / farthest Nystrom hit | 9.4 +/- 2.3 |
| Compiled miss / fixed ReLU hit | 9.0 +/- 2.0 |
| Compiled hit / spectral miss | 0.8 +/- 0.8 |
| Uniform Nystrom miss / spectral hit | 3.6 +/- 2.2 |
| Spectral miss / RBF hit | 1.0 +/- 1.2 |

Compiler and spectral errors overlapped weakly: compiled averaged 13.0 errors
per split, spectral 3.6, shared errors 2.8 and Jaccard overlap 0.20. Compiler
and uniform Nystrom errors also overlapped weakly: compiled 13.0, uniform
Nystrom 6.0, shared 3.4 and Jaccard 0.22. This supports the claim that the
compiler loses recoverable structure rather than merely failing on the same
ambiguous examples as the stronger compact methods.

For the 51 compiled-miss/spectral-hit examples, the mean same-minus-other RBF
neighbor margin was +0.0202 and the mean top-5 true-class-neighbor fraction was
0.686. For the four all-models-wrong examples, the same values were -0.1443 and
0.150. This separates two regimes: many compiler-only failures still have
useful local class support, while the few universal failures look genuinely
ambiguous under the RBF neighborhood.

Common compiler mistakes among compiled-miss/spectral-hit examples included
9->0, 3->8, 9->7, 4->7, 7->9 and several 8-confusions. These are not used for
test-set tuning; they are development clues for the next representation design.

Interpretation: the current compiler is not primarily limited by impossible
validation samples. It often misses examples that spectral and Nystrom features
recover and that still have same-class local support in the RBF geometry. The
next representation attempt should therefore preserve local neighbor/landmark
structure more directly, or introduce a supervised class-separation geometry,
instead of further residualizing the existing PCA/quantile feature map.

Decision: proceed to a cost-accounted local landmark/spectral compression
protocol before any untouched test evaluation. A useful next candidate should
state whether it stores landmarks, distills landmarks into parameters, or uses
train labels to separate local class neighborhoods.

## 2026-09-05: Error Geometry Diagnostic Preregistered

Locked DNS05-EG before development evaluation. The diagnostic reconstructs the
already studied selected development models and records per-validation-sample
predictions, correctness, score margins, local RBF neighbor geometry and
192-landmark coverage. It reports tag counts, confusion counts and model-pair
error overlap for compiler-vs-spectral, compiler-vs-Nystrom, compiler-vs-fixed
ReLU, Nystrom-vs-spectral and spectral-vs-RBF comparisons.

The runner has no test argument in its evaluator and records null test fields.
Tests cover diagnostic tag direction, local-neighbor geometry, excluded-input
isolation and synthetic grid/sample completeness. No test scores were computed.

## 2026-09-05: Landmark Geometry Diagnostic Result

Protocol/code commit: `0d9213e73c9d2185d507b9830b351c83dc813783`.
Worktree was clean at evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_landmark --config configs/dns05_landmark_digits.json --output results/dns05_landmark_digits.json
```

Complete auditable record: `docs/results/dns05_landmark_digits.json`.
The run produced 800 validation-only rows: five fixed digits development splits,
20 representations, four ridge values and intercept on/off. Test fields are null
by design; this is not independent confirmation evidence.

Selected validation summary:

| Model | Validation accuracy, mean +/- SD | Kernel error, mean | Rank / budget | Retained train samples |
|---|---:|---:|---:|---:|
| Linear | 0.9354 +/- 0.0072 | n/a | 60.2 / 64 | 0 |
| Fixed ReLU 256 | 0.9749 +/- 0.0079 | n/a | 252.2 / 256 | 0 |
| PCA ReLU 192 | 0.9616 +/- 0.0041 | n/a | 184.4 / 192 | 0 |
| Compiled 192 | 0.9638 +/- 0.0044 | 0.032062 | 184.4 / 192 | 0 |
| RFF 192 | 0.9671 +/- 0.0077 | 0.063285 | 192 / 192 | 0 |
| Uniform Nystrom 192 | 0.9833 +/- 0.0048 | 0.004250 | 192 / 192 | 192 |
| Farthest Nystrom 192 | 0.9822 +/- 0.0051 | 0.001291 | 192 / 192 | 192 |
| Class-balanced Nystrom 192 | 0.9827 +/- 0.0046 | 0.001338 | 192 / 192 | 192 |
| Spectral 192 | 0.9900 +/- 0.0042 | 0.000355 | 192 / 192 | 1078 |
| RBF oracle | 0.9916 +/- 0.0028 | 0 | 1078 / 1078 | 1078 |

Width trend:

| Budget | Spectral | Uniform Nystrom | Farthest Nystrom | Class-balanced Nystrom | RFF |
|---:|---:|---:|---:|---:|---:|
| 64 | 0.9515 | 0.9532 | 0.9476 | 0.9493 | 0.9220 |
| 128 | 0.9721 | 0.9772 | 0.9682 | 0.9694 | 0.9604 |
| 192 | 0.9900 | 0.9833 | 0.9822 | 0.9827 | 0.9671 |

Validation-selected paired differences: uniform Nystrom 192 minus spectral 192
was -0.0067 +/- 0.0064 accuracy; farthest Nystrom 192 minus spectral 192 was
-0.0078 +/- 0.0046; class-balanced farthest Nystrom 192 minus spectral 192 was
-0.0072 +/- 0.0064; RFF 192 minus spectral 192 was -0.0228 +/- 0.0036.
Farthest Nystrom 192 beat compiled 192 by +0.0184 +/- 0.0080 accuracy and
reduced train kernel error by about 0.0308. Class-balanced farthest Nystrom 192
beat fixed ReLU 256 by +0.0078 +/- 0.0091, but this is a development-selected
comparison and the interval is not decisive.

Interpretation: simple Nystrom-style landmark features explain much of the
compiler gap. Farthest-first landmarks reconstruct the train kernel better than
uniform landmarks, but uniform landmarks slightly led validation accuracy at
192 features, so Frobenius kernel error is not a complete proxy for class
performance. Class-balanced landmarks did not provide a clear improvement over
unsupervised landmarks. RFF at 192 features was better than compiled but far
behind Nystrom and spectral references. The promising compact path is therefore
explicit kernel-map compression with retained landmarks, not the current DNS05
PCA/quantile compiler.

Decision: stop expanding the current residual compiler. The next technical step
should be a cost-accounted Nystrom/spectral compression protocol: separate
feature construction time, retained model bytes, validation transform cost and
readout cost, then decide whether a landmark-based compact model deserves an
untouched-dataset confirmation run.

## 2026-09-05: Landmark Geometry Diagnostic Preregistered

Added a related-work note for kernel PCA/spectral references, Nystrom kernel
machines, random Fourier features, extreme learning machines and landmark
selection. This confirms that the next diagnostic is a comparison against
established kernel-approximation methods, not a novelty claim.

Locked DNS05-LM before development evaluation. The new validation-only runner
compares spectral ranks 64/128/192, uniform Nystrom landmarks, deterministic
farthest-first Nystrom landmarks, train-label-balanced farthest-first landmarks,
random Fourier features, and the current linear/fixed-ReLU/PCA-ReLU/compiled/RBF
anchors under the same closed-form readout grid. Tests cover Nystrom landmark
kernel reconstruction, deterministic farthest-first selection, excluded-input
isolation and synthetic grid completeness. No test scores were computed.

## 2026-09-05: Matched-Readout Diagnostic Result

Protocol/code commit: `83066851081b773584c067b7c23414b1a5555dc4`.
Worktree was clean at evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_readout --config configs/dns05_readout_digits.json --output results/dns05_readout_digits.json
```

Complete auditable record: `docs/results/dns05_readout_digits.json`.
The run produced 240 validation-only rows: five fixed digits development splits,
six representations, four ridge values and intercept on/off. Test fields are
null by design; this is not independent confirmation evidence.

| Model | Validation accuracy, mean +/- SD | Kernel error, mean +/- SD | Rank / budget | Mean solve s | Mean inference s |
|---|---:|---:|---:|---:|---:|
| Linear | 0.9354 +/- 0.0072 | n/a | 60.2 / 64 | 0.0005 | <0.0001 |
| Fixed ReLU | 0.9749 +/- 0.0079 | n/a | 252.2 / 256 | 0.0065 | 0.0002 |
| PCA ReLU 192 | 0.9616 +/- 0.0041 | n/a | 184.4 / 192 | 0.0030 | 0.0001 |
| Compiled 192 | 0.9638 +/- 0.0044 | 0.0321 +/- 0.0008 | 184.4 / 192 | 0.0036 | 0.0001 |
| Spectral 192 | 0.9900 +/- 0.0042 | 0.000355 +/- 0.000006 | 192 / 192 | 0.0032 | 0.0001 |
| RBF oracle | 0.9916 +/- 0.0028 | 0 | 1078 / 1078 | 0.0389 | 0.0004 |

Validation-selected paired differences: compiled minus PCA ReLU was
+0.0022 +/- 0.0036 accuracy, compiled minus fixed ReLU was -0.0111 +/- 0.0086,
compiled minus spectral was -0.0262 +/- 0.0061, and spectral minus full RBF was
-0.0017 +/- 0.0042. The matched readout removes a previous comparison
confound and shows that a compact spectral representation can nearly preserve
the RBF oracle on this development setup. The current compiled representation
does not yet compile that geometry well enough: its kernel reconstruction error
remains about 0.032, far above the spectral reference, and its validation
accuracy remains below fixed random ReLU despite using fewer features.

Resulting decision: pause residual-depth variants for now. The next justified
step is related-work verification plus a narrower representation hypothesis
focused on why the compiler fails to approximate the spectral oracle, not a
claim that direct synthesis already replaces training.

## 2026-09-05: Matched-Readout Diagnostic Preregistered

Added the experiment register and validation-only DNS05-RO protocol. The new runner
accepts only development arrays in its evaluator and records null test fields.
Six representations receive the identical eight-setting readout grid; paired and
validation-selected analyses are separate. Tests check primal/dual intercept
equivalence, excluded-input isolation and synthetic grid completeness. Digits
remains development data; no confirmation claim or new independent holdout.

## 2026-09-05: AI Contributor Onboarding Added

Added root `AGENTS.md` and `docs/ai-contributor-guide.md`, linked from README.
The guide covers required reading, implementation boundaries, the current evidence
snapshot, test-data protection, experiment preregistration, reporting, Git workflow
and handoff requirements. It explicitly warns that the historical runner evaluates
test data and that joining the project does not authorize executing the entire
roadmap. Documentation only; no new experiments or protocol changes.

## 2026-09-05: Staged Research Plan Recorded

Added `docs/research-plan.md` and linked it from README and the hypothesis document.
The plan starts with validation-only matched-readout controls, then covers related
work, complete resource accounting, untouched-data confirmation, scaling and the
single-pass hypothesis, and independent reproduction under a predefined budget.
Each stage has deliverables and decision criteria, including stopping unsuccessful
branches. No new experiments were run and no future capability is claimed as a
result. The methodology remains binding; individual protocols must still be locked
before execution.

## 2026-09-05: Independent Model Creation Objective Clarified

Integrated a concrete independence objective into the existing accessibility
motivation in `docs/hypothesis.md`: small teams should be able to create, modify,
run and maintain useful models without dependence on one proprietary service.
Connected affordable synthesis to inference cost, reproducible procedures and
legally usable data, modification and redistribution rights, and portability.
Proposed a future benchmark with task, quality, hardware and budget fixed before
evaluation, followed by independent reproduction. These are research and ecosystem
goals, not demonstrated capabilities or a guarantee against monopoly. No changes
to the experimental protocol or reported results.

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
