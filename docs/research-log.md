# Research Log

## 2026-09-06: Research Plan Updated After Dipole Audit

Updated [Research Plan](research-plan.md) and
[AI Contributor Guide](ai-contributor-guide.md) to reflect the completed DNS05
prototype, dipole and dipole-error-audit diagnostics. No new experiment was run
in this milestone.

The plan now treats train-sample-free synthetic centers as the active
development branch, while keeping the original residual compiler branch paused.
It adds a bounded DNS05-HYB direction: one frozen hybrid-center diagnostic that
combines class-local coverage with a predetermined boundary-center allocation.
The plan explicitly forbids tuning dipole shift fractions, quantiles or budgets
from DNS05-DEA examples and keeps digits as development data rather than fresh
confirmation evidence.

## 2026-09-06: Dipole Error Audit Result

Evaluation commit: `9b7baf08e30d6ae715fcade08c045c32625fab0c`.
Worktree was clean at evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_error_geometry --config configs/dns05_dipole_error_audit_digits.json --output results/dns05_dipole_error_audit_digits.json
```

Complete auditable record:
`docs/results/dns05_dipole_error_audit_digits.json`. The run produced 400
validation-only readout rows, 50 selected model/split rows and 1795
per-validation-sample records. Test fields are null by design; this is not
independent confirmation evidence.

Selected validation accuracy matched DNS05-DIP: class-PCA prototypes 192 were
0.9794 +/- 0.0080, dipole prototypes 192 were 0.9811 +/- 0.0060, uniform
Nystrom 192 was 0.9833 +/- 0.0048, spectral 192 was 0.9900 +/- 0.0042 and full
RBF was 0.9916 +/- 0.0028.

Per-split diagnostic tags:

| Tag | Mean count +/- SD | Mean same-minus-other RBF margin | Mean top-5 true-class fraction |
|---|---:|---:|---:|
| All selected models correct | 326.2 +/- 4.7 | +0.0599 | 0.974 |
| All selected models wrong | 0.8 +/- 0.8 | -0.1443 | 0.150 |
| Class-PCA miss / dipole hit | 2.2 +/- 1.6 | +0.0125 | 0.655 |
| Class-PCA hit / dipole miss | 1.6 +/- 1.1 | -0.0010 | 0.450 |
| Dipole miss / uniform Nystrom hit | 3.0 +/- 2.5 | -0.0117 | 0.480 |
| Dipole hit / uniform Nystrom miss | 2.2 +/- 1.8 | +0.0306 | 0.727 |
| Dipole miss / spectral hit | 3.2 +/- 1.5 | -0.0079 | 0.475 |
| Dipole miss / RBF hit | 3.8 +/- 2.5 | -0.0032 | 0.463 |

Error overlap: class-PCA prototypes averaged 7.4 errors per split, dipole
prototypes 6.8, shared errors 5.2, class-PCA-only errors 2.2 and dipole-only
errors 1.6. Against uniform Nystrom, dipole averaged 6.8 errors, uniform Nystrom
6.0, shared errors 3.8, dipole-only errors 3.0 and Nystrom-only errors 2.2.

Interpretation: the boundary hypothesis is only partly supported. Dipole fixes
relative to class-PCA are closer to class boundaries than all-correct examples:
their same-minus-other RBF margin is +0.0125 versus +0.0599 for all-correct
examples. However, the examples broken by dipole are also boundary-like and even
more ambiguous on average, with margin -0.0010 and top-5 true-class fraction
0.450. This means dipole is not a clean boundary repair mechanism; it shifts a
small number of difficult decisions in both directions.

Negative result: dipole still misses examples that uniform Nystrom and spectral
features recover, and dipole-only errors against uniform Nystrom are more
ambiguous on average than dipole-only wins. The small average accuracy gain over
class-PCA prototypes should therefore not justify test confirmation by itself.

Decision: do not tune the dipole shift fraction or quantile layout on these
examples. The next bounded development step should define a frozen
train-sample-free hybrid-center protocol before evaluation: reserve most centers
for class-local coverage and a small, predetermined allocation for boundary
coverage. A later confirmation run should wait until the candidate family is
fixed and an untouched data boundary is selected.

## 2026-09-06: Dipole Error Audit Preregistered

Locked DNS05-DEA before development evaluation. This audit does not add a new
model family. It reuses the already selected class-PCA prototype 192, dipole
prototype 192, uniform Nystrom 192, spectral 192, RBF and required baselines,
then records per-validation-example fixes, breaks and RBF neighbor geometry.

The predicted mechanism is boundary specificity. If dipole prototypes helped
because they cover rival-class boundaries, class-PCA miss/dipole hit examples
should have smaller same-minus-other RBF neighbor margins than examples both
prototype models get correct. The falsifying outcome is that fixed and broken
examples have similar geometry, implying the small DNS05-DIP gain may be a
fragile redistribution of errors. No test scores are computed.

## 2026-09-05: Dipole Prototype Diagnostic Result

Evaluation commit: `dc69292d2a8e029794af38d4baede248230aae8f`.
Worktree was clean at evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_prototype --config configs/dns05_dipole_prototype_digits.json --output results/dns05_dipole_prototype_digits.json
```

Complete auditable record: `docs/results/dns05_dipole_prototype_digits.json`.
The run produced 1160 validation-only rows and 145 selected model/split rows.
Test fields are null by design; this is not independent confirmation evidence.

Selected validation summary:

| Model | Validation accuracy, mean +/- SD | Kernel error | Rank | Retained train samples | Exact train-row prototype matches |
|---|---:|---:|---:|---:|---:|
| Fixed ReLU 256 | 0.9749 +/- 0.0079 | n/a | 252.2 | 0 | n/a |
| Compiled 192 | 0.9638 +/- 0.0044 | 0.032062 | 184.4 | 0 | n/a |
| Class PCA prototypes 192 | 0.9794 +/- 0.0080 | 0.005312 | 192.0 | 0 | 0 |
| Dipole prototypes 64 | 0.9588 +/- 0.0077 | 0.008797 | 64.0 | 0 | 0 |
| Dipole prototypes 128 | 0.9744 +/- 0.0087 | 0.005662 | 128.0 | 0 | 0 |
| Dipole prototypes 192 | 0.9811 +/- 0.0060 | 0.004937 | 192.0 | 0 | 0 |
| Uniform Nystrom 192 | 0.9833 +/- 0.0048 | 0.004250 | 192.0 | 192 | n/a |
| Spectral 192 | 0.9900 +/- 0.0042 | 0.000355 | 192.0 | 1078 | n/a |
| RBF oracle | 0.9916 +/- 0.0028 | 0.000000 | 1078.0 | 1078 | n/a |

Selected paired differences:

| Comparison | Validation accuracy delta, mean +/- SD | Kernel error delta | Retained train samples delta |
|---|---:|---:|---:|
| Dipole prototypes 192 - Class PCA prototypes 192 | +0.00167 +/- 0.00671 | -0.000375 | 0 |
| Dipole prototypes 192 - Uniform Nystrom 192 | -0.00223 +/- 0.00694 | +0.000687 | -192 |
| Dipole prototypes 192 - Fixed ReLU 256 | +0.00613 +/- 0.00305 | n/a | 0 |
| Dipole prototypes 192 - Compiled 192 | +0.01727 +/- 0.00635 | -0.027124 | 0 |
| Dipole prototypes 192 - Spectral 192 | -0.00891 +/- 0.00413 | +0.004582 | -1078 |
| Class PCA prototypes 192 - Uniform Nystrom 192 | -0.00390 +/- 0.00641 | +0.001062 | -192 |
| Uniform Nystrom 192 - Spectral 192 | -0.00669 +/- 0.00641 | +0.003895 | -886 |

Interpretation: the unexpected boundary-aware shift helped slightly. Dipole
prototypes 192 improved over unshifted class-PCA prototypes by 0.00167 validation
accuracy and reduced train-kernel reconstruction error by 0.000375, while still
retaining no real train rows and having no exact train-row center matches. The
gain is small relative to split variation, so it should be treated as a
development clue rather than a confirmed improvement.

Negative result: explicit boundary shifting does not close the gap to stronger
RBF-derived references. Dipole prototypes 192 remain below uniform Nystrom 192
by 0.00223 +/- 0.00694 and below spectral 192 by 0.00891 +/- 0.00413. This
suggests that rival-class boundary information is useful but incomplete; the
remaining gap may require better coverage of within-class manifolds or a
train-only way to synthesize more diverse local centers.

Decision: keep `prototype_class_dipole_192` as the strongest observed
train-sample-free synthetic prototype candidate, but do not proceed directly to
test confirmation from this small validation gain. The next bounded development
step should audit which validation examples are fixed or broken by dipole
prototypes relative to class-PCA prototypes and uniform Nystrom. If the fixed
examples concentrate near rival-class boundaries, a final frozen candidate may
combine class-local coverage with a small boundary-center allocation.

## 2026-09-05: Dipole Prototype Diagnostic Preregistered

Locked DNS05-DIP before development evaluation. The diagnostic keeps the same
validation-only digits development boundary as DNS05-PT and adds one bounded
synthetic-center variant: `prototype_class_dipole` at 64/128/192 centers. The
variant starts from class-local PCA/quantile prototypes but shifts centers
toward and away from the nearest rival class under the train-only RBF geometry.
The shift fraction is fixed at 0.25 before evaluation and is not a validation
grid.

The predicted mechanism is boundary coverage: previous error geometry suggested
that many compact-model misses still have useful local class support. If this
support is organized around class boundaries, a small set of synthetic dipole
centers may outperform unshifted class-PCA prototypes without retaining train
rows. The falsifying outcome is equal or lower validation accuracy than
class-PCA prototypes at the same feature budget, especially if kernel
reconstruction also worsens. No test scores are computed.

## 2026-09-05: Prototype Distillation Diagnostic Result

Evaluation commit: `59fa76deb5a20e1ea06a1e7707c7e08293e1d087`.
The DNS05-PT protocol had already been locked; this commit adds prototype audit
fields to the summaries before the recorded run. Worktree was clean at
evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_prototype --config configs/dns05_prototype_digits.json --output results/dns05_prototype_digits.json
```

Complete auditable record: `docs/results/dns05_prototype_digits.json`.
The run produced 1040 validation-only rows and 130 selected model/split rows.
Test fields are null by design; this is not independent confirmation evidence.

Selected validation summary:

| Model | Validation accuracy, mean +/- SD | Kernel error | Rank | Retained train samples | Exact train-row prototype matches |
|---|---:|---:|---:|---:|---:|
| Fixed ReLU 256 | 0.9749 +/- 0.0079 | n/a | 252.2 | 0 | n/a |
| Compiled 192 | 0.9638 +/- 0.0044 | 0.032062 | 184.4 | 0 | n/a |
| RFF 192 | 0.9671 +/- 0.0077 | 0.063285 | 192.0 | 0 | n/a |
| Uniform Nystrom 192 | 0.9833 +/- 0.0048 | 0.004250 | 192.0 | 192 | n/a |
| Global PCA prototypes 64 | 0.9387 +/- 0.0074 | 0.008324 | 61.2 | 0 | 0 |
| Global PCA prototypes 128 | 0.9599 +/- 0.0042 | 0.006491 | 128.0 | 0 | 0 |
| Global PCA prototypes 192 | 0.9599 +/- 0.0051 | 0.006487 | 119.8 | 0 | 0 |
| Class PCA prototypes 64 | 0.9543 +/- 0.0075 | 0.006700 | 64.0 | 0 | 0 |
| Class PCA prototypes 128 | 0.9733 +/- 0.0051 | 0.005477 | 128.0 | 0 | 0 |
| Class PCA prototypes 192 | 0.9794 +/- 0.0080 | 0.005312 | 192.0 | 0 | 0 |
| Spectral 192 | 0.9900 +/- 0.0042 | 0.000355 | 192.0 | 1078 | n/a |
| RBF oracle | 0.9916 +/- 0.0028 | 0.000000 | 1078.0 | 1078 | n/a |

Selected paired differences:

| Comparison | Validation accuracy delta, mean +/- SD | Kernel error delta | Retained train samples delta |
|---|---:|---:|---:|
| Global PCA prototypes 192 - Uniform Nystrom 192 | -0.02340 +/- 0.00578 | +0.002236 | -192 |
| Class PCA prototypes 192 - Uniform Nystrom 192 | -0.00390 +/- 0.00641 | +0.001062 | -192 |
| Class PCA prototypes 192 - Fixed ReLU 256 | +0.00446 +/- 0.00578 | n/a | 0 |
| Class PCA prototypes 192 - Compiled 192 | +0.01560 +/- 0.01090 | -0.026749 | 0 |
| Class PCA prototypes 192 - Spectral 192 | -0.01058 +/- 0.00773 | +0.004957 | -1078 |
| Uniform Nystrom 192 - Spectral 192 | -0.00669 +/- 0.00641 | +0.003895 | -886 |

Interpretation: synthetic class-PCA RBF prototypes are the strongest
train-sample-free candidate observed so far. At 192 centers they nearly match
uniform Nystrom 192 on reused validation splits while retaining no real train
rows and having no exact train-row prototype matches. They also beat the current
compiled 192 representation and the fixed ReLU 256 baseline in this diagnostic.
This is encouraging for direct synthesis because it suggests that useful RBF
geometry can be represented by explicit synthetic centers rather than by stored
training examples.

Negative result: global PCA prototypes do not preserve enough class-local
structure. Their validation accuracy saturates around 0.9599 at 128/192 centers
and trails uniform Nystrom 192 by 0.0234 +/- 0.0058. This supports the previous
error-geometry result: the missing information is local and class-structured,
not merely a global low-dimensional outline of the data.

Decision: keep class-PCA prototypes as the next compact neural candidate, but
do not treat this as final evidence. The next justified step is a locked
confirmation protocol that compares only a small set of already selected
candidates on a fresh boundary: class-PCA prototypes 192, uniform Nystrom 192,
fixed ReLU 256, spectral 192 and full RBF. If a fresh dataset is chosen, the
candidate set and readout rules must be frozen before test evaluation.

## 2026-09-05: Prototype Distillation Diagnostic Preregistered

Locked DNS05-PT before development evaluation. The diagnostic tests whether
synthetic RBF centers computed from train statistics can retain the useful local
geometry seen in Nystrom landmarks without storing real train examples as
inference landmarks. It adds global-PCA and class-PCA prototype families at
64/128/192 centers, while retaining the previous linear, fixed-ReLU, PCA-ReLU,
compiled, RFF, Nystrom, spectral and full-RBF references under the same
validation-only readout grid.

The related-work note was updated with RBF networks, locally tuned units and
resource-allocating networks. These sources make the novelty boundary explicit:
synthetic RBF centers with an analytical readout are not a new idea by
themselves. Tests cover deterministic prototype construction, absence of raw
train-sample retention, excluded-input isolation and synthetic grid completeness.
No test scores were computed.

## 2026-09-05: Cost-Accounted Compression Diagnostic Result

Protocol/code commit: `dc6a917007ec8048d51af768f1bc6e6f9b114558`.
Worktree was clean at evaluation. Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_dns05_cost --config configs/dns05_cost_digits.json --output results/dns05_cost_digits.json
```

Complete auditable record: `docs/results/dns05_cost_digits.json`.
The run produced 800 validation-only readout rows and 100 selected model/split
rows. Test fields are null by design; this is not independent confirmation
evidence. Cost fields are approximate numerical-array accounting plus descriptive
single-machine timings, not exact OS RSS and not energy measurements.

Selected validation summary for key candidates:

| Model | Validation accuracy, mean +/- SD | Model bytes | Validation prediction s | Fit s without oracle | Fit s with oracle |
|---|---:|---:|---:|---:|---:|
| Fixed ReLU 256 | 0.9749 +/- 0.0079 | 121376 | 0.000879 | 0.0583 | 0.0596 |
| Compiled 192 | 0.9638 +/- 0.0044 | 411168 | 0.001485 | 0.5803 | 1.1462 |
| RFF 192 | 0.9671 +/- 0.0077 | 116256 | 0.001823 | 0.0488 | 0.6147 |
| Uniform Nystrom 192 | 0.9833 +/- 0.0048 | 409600 | 0.002569 | 0.0529 | 0.6188 |
| Farthest Nystrom 192 | 0.9822 +/- 0.0051 | 409600 | 0.002447 | 0.1143 | 0.6802 |
| Class-balanced Nystrom 192 | 0.9827 +/- 0.0046 | 409600 | 0.002542 | 0.0832 | 0.6490 |
| Spectral 192 | 0.9900 +/- 0.0042 | 2224128 | 0.014278 | 0.3447 | 0.9105 |
| RBF oracle | 0.9916 +/- 0.0028 | 639288 | 0.012849 | 0.4206 | 0.9865 |

Mean shared RBF oracle/gamma selection time was 0.5645 s per split. This
dominates the development accounting for RBF-derived compact models. Without
that shared selection, uniform Nystrom 192 used about 0.0529 s for train
features plus the readout grid, compared with 0.4206 s for full RBF and
0.3447 s for spectral 192.

Efficiency relative to full RBF: uniform Nystrom 192 had an accuracy gap of
0.00836 +/- 0.00394, used 0.641x the RBF model-state bytes and 0.201x the RBF
validation prediction time. Spectral 192 had a smaller accuracy gap of
0.00167 +/- 0.00422, but used 3.48x the RBF model-state bytes and 1.13x the RBF
validation prediction time in this implementation. Fixed ReLU 256 was much
smaller and faster than RBF, but its validation accuracy gap was
0.0167 +/- 0.0079.

Width/cost trend:

| Family | 64 acc / bytes / pred s | 128 acc / bytes / pred s | 192 acc / bytes / pred s |
|---|---:|---:|---:|
| Uniform Nystrom | 0.9532 / 71680 / 0.000711 | 0.9772 / 207872 / 0.001683 | 0.9833 / 409600 / 0.002569 |
| RFF | 0.9220 / 39440 / 0.000624 | 0.9604 / 77856 / 0.001246 | 0.9671 / 116256 / 0.001823 |
| Spectral | 0.9515 / 1110032 / 0.013522 | 0.9721 / 1667072 / 0.015108 | 0.9900 / 2224128 / 0.014278 |

Interpretation: on reused digits development splits, uniform Nystrom 192 is the
best observed quality/resource compromise among the compact RBF approximations:
it is less accurate than spectral 192 and full RBF, but substantially cheaper
than both for validation prediction and smaller than spectral state. Farthest
landmarks remain better at kernel reconstruction, but not at validation accuracy
or construction time. Spectral 192 is an excellent quality reference, not a
compact deployment winner in the current implementation. The current compiled
model is worse than uniform Nystrom in accuracy, construction time and model
bytes, so it should not be retained as the next candidate.

Decision: if the goal permits storing 192 train-derived landmarks, the next
candidate for untouched-data confirmation is uniform Nystrom 192 with the fixed
readout-selection rule. If the goal requires a train-sample-free neural artifact,
this result is not sufficient; the next research step should distill landmark
behavior into explicit parameters and compare it against Nystrom directly.

## 2026-09-05: Cost-Accounted Compression Diagnostic Preregistered

Locked DNS05-CA before development evaluation. The diagnostic measures the
already studied compact candidates rather than adding a new model family:
linear, fixed ReLU 256, PCA ReLU 192, compiled 192, RFF 64/128/192,
uniform/farthest/class-balanced Nystrom 64/128/192, spectral 64/128/192 and
full RBF. It preserves the same split seeds, oracle gamma selection grid and
closed-form readout grid used in previous validation-only diagnostics.

The runner records separate preprocessing, oracle selection, train feature
construction, validation feature transform, readout-grid solve and repeated
selected-readout inference timings. It also records approximate numerical
model-state bytes, retained train samples, dense intermediate-array estimates
and `tracemalloc` peaks. These are cost diagnostics, not energy measurements.
Tests cover RBF readout state accounting, excluded-input isolation, synthetic
grid completeness and RBF-referenced efficiency summaries. No test scores were
computed.

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
