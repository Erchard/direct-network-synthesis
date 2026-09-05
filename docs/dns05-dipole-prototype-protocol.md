# DNS 0.5 Dipole Prototype Diagnostic

Status: locked before development evaluation, 2026-09-05.

Question: can train-sample-free synthetic RBF centers improve when class-local
prototypes are deliberately shifted toward and away from their nearest rival
class under the train-only RBF geometry? This is a validation-only diagnostic on
reused digits development splits. It is not test evidence and not a novelty
claim.

1. Use the same digits split seeds 101, 202, 303, 404 and 505 at 60/20/20. Only
   train and validation arrays enter evaluation. Excluded split members are not
   transformed, predicted or scored. Test fields are null.
2. Use train-only standardization and the same shared RBF oracle selection grid:
   gamma multipliers [0.5, 1.0, 2.0] and alpha [0.001, 0.01, 0.1]. Reuse the
   selected gamma for all RBF-derived features in each split.
3. Reuse the DNS05 prototype runner with the previous references and prototype
   families: linear, fixed ReLU 256, PCA ReLU 192, compiled 192, RFF
   64/128/192, uniform/farthest/class-balanced Nystrom 64/128/192, spectral
   64/128/192, full RBF, global-PCA prototypes and class-PCA prototypes.
4. Add one new train-sample-free family at budgets 64, 128 and 192:
   `prototype_class_dipole`. For each class, allocate the same balanced center
   quota as class-PCA prototypes. The first center is the class centroid. The
   remaining centers use class-local PCA/quantile offsets, but alternate between
   adding and subtracting a fixed boundary shift.
5. The rival class for each class is chosen from train data only as the other
   class with the highest mean cross-class RBF affinity under the selected
   train-only gamma. The fixed boundary shift is 0.25 times the vector from the
   class centroid to that rival centroid. This value is frozen before evaluation
   and is not tuned on validation.
6. Prototype features use the same explicit map as Nystrom:
   `K(X, C) K(C, C)^(-1/2)`, with `C` equal to synthetic centers and the same
   eigenvalue cutoff rule. Record retained real train samples, prototype count
   and exact train-row prototype matches.
7. For every representation evaluate alpha [0.001, 0.01, 0.1, 1.0] and
   intercept [false, true] using the same closed-form readout objective as the
   previous diagnostics. Select by validation accuracy per model/split, then
   smaller alpha, then no intercept.
8. Report validation accuracy, RMSE, R2, train kernel reconstruction error,
   realized rank, feature budget, retained real train samples, prototype count,
   prototype/train exact-match count, solve time and inference time. Report all
   variants, including negative outcomes.
9. Planned selected paired differences: dipole prototypes 192 minus class-PCA
   prototypes 192, dipole prototypes 192 minus uniform Nystrom 192, dipole
   prototypes 192 minus fixed ReLU 256, dipole prototypes 192 minus compiled
   192, dipole prototypes 192 minus spectral 192, class-PCA prototypes 192
   minus uniform Nystrom 192 and uniform Nystrom 192 minus spectral 192.
10. Do not adapt dipole formulas, shift fraction, quantiles, budgets, alpha grid
    or seeds after seeing validation outcomes. Any later variant inspired by
    this run requires a separate locked protocol.

Decision: if dipole prototypes improve over class-PCA prototypes without
retaining train samples, continue developing boundary-aware synthetic center
synthesis. If they underperform, treat explicit boundary shifting as a negative
result and keep unshifted class-PCA prototypes as the train-sample-free candidate.
