# DNS 0.5 Matched-Readout Diagnostic

Status: locked before development evaluation, 2026-09-05.

Question: do readout settings or representation loss explain the earlier compiler
gap? This is validation-only development, not a new test result or confirmation.
The general methodology's test fields will be explicitly null/not evaluated.

1. Use the original digits splits 101, 202, 303, 404, 505 at 60/20/20. Only train
   and validation arrays enter evaluation. Labels are read for existing stratified
   membership and the dataset is hashed; excluded examples are not transformed,
   fitted, predicted or scored. Splits overlap across repetitions and are not
   independent confirmation. No new protected dataset has been selected.
2. Retain train-only standardization and the existing validation oracle gamma/alpha
   selection grid unchanged. Reuse the selected gamma for all kernel representations.
   This is a shared historical selection allowance, not equal total model-search cost.
3. Evaluate six representations: standardized linear input, seeded 192 ReLU plus
   original input, exact compiler PCA/quantile basis (192), one-shot compiler (192),
   rank-192 spectral oracle and full RBF. No residual variants or basis scaling changes.
4. Compiler settings remain defaults: projection alpha 1e-6, quantiles .1 to .9,
   five knots, spectral epsilon 1e-10. Its initial alpha-1 readout is unused; the
   diagnostic refits the readout. Direct basis features share its exact fitted map.
5. For every representation evaluate alpha [0.001, 0.01, 0.1, 1.0] and intercept
   [false, true]: 48 rows per split, 240 total. Objective is sum squared score error
   plus alpha times weight norm squared; intercept is unpenalized. RBF intercept
   uses train-kernel and target centering with correct cross-kernel centering.
6. Compare identical settings and separately select maximum validation accuracy
   per representation/split, breaking ties by smaller alpha then no intercept.
   Selection results are optimistic development scores, not held-out estimates.
7. Report the entire grid, selected rows, sample SD and paired differences for
   compiled minus direct basis, compiled minus spectral, spectral minus RBF and
   compiled minus fixed ReLU. RMSE/R2 use raw class scores against train-class
   one-hot targets; R2 uses globally summed centered target variation. They differ
   from the earlier hard-prediction encoding and must not be compared as identical.
8. Record train relative Frobenius error where geometry is approximated, realized
   rank, feature budget, readout parameters and retained inference training samples.
   Save split indices, config, command, source SHA, environment and dataset hash.
9. Timings are descriptive single measurements: readout solve and multiplication
   over precomputed validation features; these are NOT end-to-end inference timings.
   Representation time includes train and validation construction. The direct basis
   reuses compiler fitting, spectral reuses kernel construction; these timings are
   not standalone total costs. No speedup or energy claims follow from this run.
10. Run synthetic tests before the committed evaluation. Abort and log numerical
    failure rather than silently omit variants. Do not adjust the grid from results.

Decision: matched and selected development results will determine whether further
residual work on this fixed basis is justified. If direct basis readout matches or
exceeds compilation, pause that direction. Any proposed representation change next
requires related-work verification and a separate bounded protocol. No novelty claim.
