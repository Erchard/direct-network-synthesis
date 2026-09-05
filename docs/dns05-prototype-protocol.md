# DNS 0.5 Prototype Distillation Diagnostic

Status: locked before development evaluation, 2026-09-05.

Question: can the useful local geometry of Nystrom landmarks be approximated by
synthetic RBF centers computed from train statistics, without retaining real
train examples as inference landmarks? This is validation-only development work
on reused digits splits, not test evidence and not a novelty claim.

1. Use the same digits split seeds 101, 202, 303, 404 and 505 at 60/20/20. Only
   train and validation arrays enter evaluation. Excluded split members are not
   transformed, predicted or scored. Test fields are null.
2. Use train-only standardization and the same shared RBF oracle selection grid:
   gamma multipliers [0.5, 1.0, 2.0] and alpha [0.001, 0.01, 0.1]. Reuse the
   selected gamma for all RBF-derived features in each split.
3. Keep existing references: linear, fixed ReLU 256, PCA ReLU 192, compiled 192,
   RFF 64/128/192, uniform/farthest/class-balanced Nystrom 64/128/192, spectral
   64/128/192 and full RBF.
4. Add two train-sample-free synthetic-center families at budgets 64, 128 and
   192. `prototype_global_pca` uses global train PCA directions and train
   projection quantiles. `prototype_class_pca` allocates centers across classes,
   starts from each class centroid and adds class-local PCA/quantile offsets.
   Both store synthetic centers and a kernel normalizer, not raw train samples.
5. Prototype features use the same explicit map as Nystrom:
   `K(X, C) K(C, C)^(-1/2)`, with `C` equal to synthetic centers and the same
   eigenvalue cutoff rule. Record the number of centers that exactly match a
   train row; this should be interpreted as an audit check, not a selection
   criterion.
6. For every representation evaluate alpha [0.001, 0.01, 0.1, 1.0] and
   intercept [false, true] using the same closed-form readout objective as the
   previous diagnostics. Select by validation accuracy per model/split, then
   smaller alpha, then no intercept.
7. Report validation accuracy, RMSE, R2, train kernel reconstruction error,
   realized rank, feature budget, retained real train samples, prototype count,
   prototype/train exact-match count, solve time and inference time. Report all
   variants, including negative outcomes.
8. Planned selected paired differences: global prototypes 192 minus uniform
   Nystrom 192, class prototypes 192 minus uniform Nystrom 192, class prototypes
   192 minus fixed ReLU 256, class prototypes 192 minus compiled 192, class
   prototypes 192 minus spectral 192 and uniform Nystrom 192 minus spectral 192.
9. Do not adapt prototype formulas, quantiles, budgets, alpha grid or seeds after
   seeing validation outcomes. Any later variant inspired by this run requires a
   separate locked protocol.

Decision: if class-PCA prototypes approach uniform Nystrom while retaining zero
real train samples, continue toward train-sample-free local synthesis. If they
remain far behind Nystrom, treat stored landmarks as the current useful compact
method and do not claim that this experiment solved neural distillation.
