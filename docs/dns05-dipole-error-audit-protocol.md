# DNS 0.5 Dipole Error Audit

Status: locked before development evaluation, 2026-09-06.

Question: which validation examples are fixed or broken by boundary-aware dipole
prototypes relative to unshifted class-PCA prototypes and uniform Nystrom
landmarks? This is a validation-only audit on reused digits development splits.
It is not test evidence and not a new model-selection pass.

1. Use the same digits split seeds 101, 202, 303, 404 and 505 at 60/20/20. Only
   train and validation arrays enter evaluation. Excluded split members are not
   transformed, predicted or scored. Test fields are null.
2. Use train-only standardization and the same shared RBF oracle selection grid:
   gamma multipliers [0.5, 1.0, 2.0] and alpha [0.001, 0.01, 0.1]. Reuse the
   selected gamma for all RBF-derived features in each split.
3. Evaluate only already defined model families: linear, fixed ReLU 256, PCA
   ReLU 192, compiled 192, RFF 192, class-PCA prototypes 192, dipole prototypes
   192, uniform Nystrom 192, spectral 192 and full RBF. Do not add a new
   synthesis formula in this audit.
4. For every representation evaluate alpha [0.001, 0.01, 0.1, 1.0] and
   intercept [false, true] using the same closed-form readout objective as the
   previous diagnostics. Select by validation accuracy per model/split, then
   smaller alpha, then no intercept.
5. Record selected predictions for every validation example. For each example,
   record true label, predicted label, correctness, score margin, true-class
   score and predicted-class score for each selected model.
6. Record train-only RBF neighbor geometry for each validation example:
   nearest train label, nearest-train similarity, maximum same-class similarity,
   maximum other-class similarity, same-minus-other similarity margin and top-5
   true-class neighbor fraction.
7. Planned pair tags: class-PCA miss/dipole hit, class-PCA hit/dipole miss,
   dipole miss/uniform Nystrom hit, dipole hit/uniform Nystrom miss, class-PCA
   miss/uniform Nystrom hit, dipole miss/spectral hit, dipole miss/RBF hit,
   dipole versus fixed ReLU, dipole versus compiled and uniform Nystrom versus
   spectral.
8. Report tag counts, per-split means, pair error overlaps and tag-conditional
   neighbor geometry. Keep all negative and ambiguous outcomes.
9. Do not use these examples to retune dipole shift fraction, quantiles, budgets,
   readout grid or split seeds. Any candidate inspired by this audit requires a
   separately locked protocol before evaluation.

Decision: if dipole fixes concentrate on examples with small or negative
same-minus-other neighbor margins, boundary-aware synthesis remains plausible.
If fixes and breaks have similar geometry, the small DNS05-DIP gain is likely a
fragile redistribution of errors rather than a reliable mechanism.
