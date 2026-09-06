# DNS05-BM End-to-End Primary-Budget Diagnostic

Locked before evaluation. This bounded stage evaluates only the primary width
192 and stream block 256, not the entire BM budget grid. It follows methodology.
Question: does the measured synthetic fitting-stage saving survive dense oracle
selection on the existing FMSA development boundaries? Failure to reach 25%
median total peak reduction per dataset is a negative resource result here.
No new test partitions or model-family changes are authorized by this protocol.

Use all three datasets and all fifteen split seeds from the unchanged
configs/dns05_failure_scaling_audit.json, including generator seed 62026.
Each worker loads the dataset, preserves the existing split indices, fits only
train preprocessing, and transforms only train and validation. Excluded rows
are never scored. Dataset hashes and split indices are recorded. All parameters
are fixed in configs/dns05_bm_end_to_end.json and the base config.

Each model/split starts in a fresh Windows process with one BLAS thread. Alternate
forward/reverse model execution order by split; cap each worker at 120 seconds
and 8 GiB observed working set. Preserve error/timeout rows. Compare batch and
streaming Nystrom plus linear ridge, fixed seeded ReLU, exact RBF and spectral.
Kernel models use the existing train/validation oracle grid. All models use the
same alpha/intercept grid and existing accuracy, RMSE, alpha, intercept tie rule.
For batch/streaming compare every matched readout, not just the chosen winner.

Store peak working set before and after oracle selection and after fitting;
Windows lifetime peak includes input loading and native-library allocations.
Report total fit wall time and oracle, map, readout and prediction times. Stream
readout time includes block transforms and accumulation; it is not a pure solve
time. Report the eight training-feature passes used by this first streaming grid
implementation. Raw input/label matrices remain resident identically. This is
neither a raw single-pass pipeline nor a claim of minimum possible stream cost.

Repeat complete validation prediction five times after one warmup, with a common
256-row query batch. Measure train rank and train kernel reconstruction after
the fit peak snapshot, in a separate diagnostic phase; dense diagnostics do not
count as fitting savings but their peak and time must also be recorded. Report
model-array bytes separately from interpreter overhead and estimated scalar
metadata. Kernel error for linear/ReLU is contextual, not their training target.

Require all batch/stream readout weights and validation scores to match at
rtol=1e-8, atol=1e-10; record prediction disagreements. Different selected
readouts must be disclosed even if caused by rounding near a tie. Store all grid
metrics and selections, paired differences, per-dataset means/sample SD, solve
and inference timings, rank, state and retained samples. Null test metrics are
mandatory. Do not adjust the protocol after seeing results. A positive result
would justify the larger BM budget grid, not fresh confirmation or a novelty claim.

Command: `python -m experiments.run_dns05_bm_end_to_end`
