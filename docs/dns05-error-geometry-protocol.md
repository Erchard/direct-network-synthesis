# DNS 0.5 Error Geometry Diagnostic

Status: locked before development evaluation, 2026-09-05.

Question: which validation examples are solved by RBF/spectral/Nystrom models
but missed by the current compiler, and what simple geometry describes those
examples? This is a diagnostic on reused digits development data, not a new test
result and not independent confirmation.

1. Use the same digits split seeds 101, 202, 303, 404 and 505 at 60/20/20. Only
   train and validation arrays enter evaluation. Excluded split members are not
   transformed, predicted or scored. The runner records null test fields.
2. Use train-only standardization and the same shared RBF oracle selection grid:
   gamma multipliers [0.5, 1.0, 2.0] and alpha [0.001, 0.01, 0.1]. Reuse the
   selected gamma for all RBF-derived representations in that split.
3. Reconstruct these existing representations only: linear, fixed ReLU 256,
   PCA ReLU 192, compiled 192, RFF 192, uniform Nystrom 192, farthest Nystrom
   192, class-balanced farthest Nystrom 192, spectral 192 and full RBF. Do not
   introduce new models or hyperparameter values in this diagnostic.
4. For every model/split, evaluate the same readout grid used previously:
   alpha [0.001, 0.01, 0.1, 1.0] and intercept [false, true]. Select the
   model/split readout by maximum validation accuracy, then smaller alpha, then
   no intercept. This selection is developmental and optimistic.
5. For each validation example, record the selected prediction, correctness,
   score margin, true-class score and predicted score for every model. Store
   sample records separately from aggregate rows.
6. Record local RBF-neighbor geometry for each validation example: nearest train
   label, nearest train similarity, maximum same-class similarity, maximum
   other-class similarity, same-minus-other similarity margin, and the fraction
   of the top five train neighbors sharing the true class.
7. Record landmark coverage for uniform, farthest-first and class-balanced
   farthest-first 192-landmark sets: maximum validation-to-landmark similarity,
   nearest landmark label and whether that label matches the validation label.
8. Report model confusion counts, model-pair error overlap, tag counts and
   geometry summaries for diagnostic tags such as compiler miss / spectral hit,
   compiler miss / Nystrom hit, all-selected correct and all-selected wrong.
9. Do not use these per-example observations to retune models on digits test
   partitions. Any new representation inspired by this diagnostic requires a
   separate locked protocol before evaluation.
10. Save config, source SHA, git status, command, environment, split indices and
    dataset hash with the result. Abort and log numerical failures rather than
    silently omitting examples or models.

Decision: if compiler-specific misses have low same-class neighbor support or
poor landmark coverage, prioritize local/landmark synthesis. If compiler misses
occur even where landmarks cover the example well, prioritize feature-map
normalization or supervised class-separation geometry. If all compact models
miss the same examples, pause model tinkering and inspect data/task ambiguity.
