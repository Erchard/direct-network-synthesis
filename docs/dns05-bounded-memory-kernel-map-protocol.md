# DNS05 Bounded-Memory Kernel-Map Protocol

Status: protocol draft, not evaluated. Numerical equivalence is the first gate;
the resource experiment requires a committed runner and measurement protocol.

This is the next single primary mechanism after the DNS05 failure-scaling audit.
It tests a resource hypothesis, not a new neural-depth claim. The method is a
streaming Nystrom-style RBF map with a closed-form primal readout. Nystrom,
kernel eigenfeatures and closed-form readouts are established related work; any
positive result belongs first to that literature rather than to a novelty claim.

## Question

Can a deterministic compact RBF feature map reach the same validation quality as
the current uniform Nystrom baseline while avoiding storage of the full
`n x b` train-feature matrix during fitting and the full `n x m` train-to-center
kernel matrix?

The proposed implementation must accumulate the regularized normal equations in
fixed row blocks:

`A = sum(Phi_block.T @ Phi_block)`

`B = sum(Phi_block.T @ Y_block)`

and solve the final readout once after the stream. The center kernel and its
inverse-root are retained; train rows are not retained solely for fitting.

## Locked boundary

This is a train/validation-only development experiment. It uses the already
declared failure-scaling datasets and seeds only to diagnose the measured
bottleneck; it does not create fresh confirmation evidence:

- `sklearn_digits`, seeds `101, 202, 303, 404, 505`;
- `sklearn_breast_cancer`, seeds `1101, 1202, 1303, 1404, 1505`;
- `synthetic_multiclass_v1`, generator seed `62026`, split seeds
  `2101, 2202, 2303, 2404, 2505`;
- stratified `60% / 20% / 20%` train/validation/excluded partitions;
- feature budgets `32, 64, 128, 192, 256`;
- uniform deterministic landmark seed arithmetic from
  `configs/dns05_failure_scaling_audit.json`;
- oracle gamma and readout alpha grids exactly as in that config;
- fixed row-block sizes `64, 256, 1024`, all reported without quality selection;
  `256` is the primary size declared before evaluation;
- `intercept` values exactly `false` and `true` under the existing tie-break;
- no test transforms, predictions, scores or test-based selection.

The row-block size is an implementation/resource variant, not a new quality
variant. It must be selected before any test confirmation and reported for every
run.

## Comparators

1. Existing `nystrom_uniform` runner, same landmarks, gamma, feature budget and
   readout grid.
2. Closed-form primal linear ridge on the standardized input.
3. Existing spectral RBF reference at matching requested rank, when available
   under the same development protocol.
4. Exact RBF kernel ridge as the oracle geometry reference, not a compact model.
5. Deterministic ReLU features with closed-form ridge, required by methodology.

The streaming candidate must use the same center construction as comparator 1.
Changing landmark selection, gamma, readout alpha, preprocessing or feature
budget is a separate experiment.

## Required measurements

For every dataset, split, budget and block size, record:

- validation accuracy, RMSE and R2;
- test fields as null with `test_status=not_evaluated`;
- actual rank and feature budget;
- kernel reconstruction error, computed blockwise without retaining all train
  features;
- model-state bytes, retained train samples and peak process memory;
- center-kernel/inverse-root construction time;
- streamed train feature time and normal-equation accumulation time;
- solve time, validation transform time and repeated validation inference time;
- number of raw-data passes and largest block allocation;
- mean and standard deviation across the five paired splits for each dataset;
- paired differences against ordinary Nystrom for quality, peak memory, state
  bytes and fit time.

Timings use one warmup and five fixed validation inference repeats, as in the
existing audit. Peak memory must be measured at process level, including native
allocations where the selected tool permits; an estimate must be labeled as an
estimate and cannot be presented as measured RAM.

## Deterministic implementation rules

1. Fit the standardizer on train only and apply it unchanged to validation.
2. Select gamma and alpha on train/validation only, using the existing fixed
   grids and tie-breaks.
3. Select landmark indices with the existing deterministic seed formula.
4. Visit train rows in original split-index order and use the same block size for
   every candidate in a run.
5. Accumulate `A` and `B` in `float64`; symmetrize `A` before solving.
6. Use the repository's existing stable closed-form solver. No gradient updates,
   iterative parameter search or adaptive early stopping are allowed.
7. Do not retain train features, train-to-center kernels or train labels after
   they are no longer required by the declared accumulation step.
8. Preserve failed, timed-out and out-of-memory variants in the result record.

## Falsification and decision rule

The bounded-memory hypothesis is not supported if the streaming implementation
has no meaningful peak-memory reduction at matched quality, or if it loses more
than the predeclared validation tolerance against ordinary Nystrom while not
improving total fit cost. Before resource evaluation, paired batch and streaming
weights and validation scores must agree with `rtol=1e-8, atol=1e-10` at identical
landmarks, gamma, alpha and intercept. Record every prediction disagreement and
its score margin; do not accept an accuracy-loss allowance for this algebraically
equivalent implementation. Failure of numerical equivalence blocks promotion
and requires a numerical diagnosis. The proposed resource target is at least
`25%` median peak-process
memory reduction at the selected budget; a state-byte reduction alone does not
count. A failure caused by a bug or missing measurement is inconclusive and
must be repaired or reported separately.

Advance to fresh confirmation only if one fixed streaming variant matches the
ordinary Nystrom quality within the locked tolerance and shows a measured
resource advantage on the paired development splits. Otherwise close this
mechanism as negative and preserve the ordinary Nystrom result as the compact
development baseline.

## Deliverable

Produce one complete JSON record, one environment manifest, one curated summary
under `docs/results/`, and a research-log entry containing source commit, exact
command, config hash, seeds, all variants, failures and the decision. No result
from this draft may be described as independent confirmation or evidence of
energy savings.

## Measurement lock prerequisites

Before benchmark execution, commit an executable config and runner that define
fresh child processes per method, fixed BLAS thread counts, OS peak working-set
measurement, identical input-loading overhead, and separate timing of oracle
selection, fitting and diagnostic passes. Dense oracle selection still has
quadratic memory cost and must be included in end-to-end reporting. A reduction
in readout-stage memory alone does not establish a bounded-memory full pipeline.
Record raw data retention, preprocessing passes and diagnostic rereads explicitly.
