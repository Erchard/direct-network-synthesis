# DNS 0.5 Full-Basis Diagnostic

Protocol fixed before evaluation, 2026-09-05.

Hypothesis: partitioning the PCA/quantile ReLU basis limits residual projection.
Compare the existing one-shot 192, partitioned 2x96 and 3x64 models against
full-basis residual 2x96 and 3x64 outputs. Every full-basis block sees all 192
fixed features; output target ranks still sum to 192. Record unique basis size,
summed block basis evaluations, output dimension, numerical rank and projection
parameter count separately. Full-basis variants require more projection parameters.
No claim of equal computational budget is made.

All blocks are linear projections of a single fixed nonlinear basis. Their
concatenation can be collapsed to a single linear projection. Sequential residual
construction is not compositional neural depth and cannot expand the basis span.

Add a rank-192 spectral oracle: eigendecompose the train kernel only and extend
to unseen examples using K(new, train) U / sqrt(lambda). Use the same fixed
readout alpha 1.0 and intercept as the compiler. This is a best rank-constrained
train Gram approximation, not a guaranteed upper bound on classification accuracy.
It retains training examples at inference and is not a compact neural baseline.

Use configs/dns05_full_basis_digits.json, with the existing five split seeds,
60/20/20 stratified partitions, train-only preprocessing and the unchanged
validation-only oracle grid. All variants and comparisons are fixed in advance;
no stopping or selection from test results. No iterative parameter optimization.
This is an exploratory diagnostic on a previously evaluated dataset and splits,
not independent confirmatory evidence. Future confirmation needs untouched data.

Report every variant, validation/test accuracy, train relative Frobenius kernel
error, rank/budget, fit and test-batch inference times, sample standard deviations
and paired differences. Fit time includes compiler diagnostics but excludes
shared preprocessing and oracle selection (selection is recorded separately).
Timing is one wall-clock measurement per split, descriptive rather than a rigorous
latency benchmark. RMSE/R2 are additionally reported on one-hot hard predictions
to satisfy the general reporting protocol; these are not calibrated score metrics.

Commit implementation and this protocol before the single finalized test run.
Commit the complete JSON record under docs/results plus an interpreted research-log
entry, including negative outcomes. Do not tune variants after examining results.
