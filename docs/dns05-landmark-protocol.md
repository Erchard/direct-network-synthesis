# DNS 0.5 Landmark Geometry Diagnostic

Status: locked before development evaluation, 2026-09-05.

Question: can simple train-only landmark feature maps explain the gap between the
current DNS05 compiler and the compact spectral RBF reference? This is a
validation-only diagnostic on reused digits development data. It does not produce
new test evidence.

1. Use the same digits split seeds 101, 202, 303, 404 and 505 at 60/20/20. Only
   train and validation arrays enter evaluation. Excluded split members are not
   transformed, predicted or scored. Digits remains development data.
2. Use train-only standardization and the existing shared RBF oracle selection
   grid: gamma multipliers [0.5, 1.0, 2.0] and alpha [0.001, 0.01, 0.1]. Reuse
   the selected gamma for all RBF-derived representations in that split.
3. Evaluate anchor representations: standardized linear input, fixed seeded ReLU
   with 192 hidden units plus input using seed 1705, compiler direct basis at 192 features,
   one-shot compiled features at 192, full RBF, and spectral RBF features at
   ranks 64, 128 and 192.
4. Evaluate new explicit kernel-map controls at landmark counts 64, 128 and 192:
   uniform Nystrom landmarks, deterministic farthest-first Nystrom landmarks,
   train-label-balanced farthest-first Nystrom landmarks, and random Fourier
   features. Landmark seed is 2309; random Fourier seed is 2310. All randomness
   is split/count-derived from these seeds and recorded in the config.
5. Nystrom features are computed as `K(X, Z) K(Z, Z)^(-1/2)` with an eigenvalue
   cutoff of 1e-10 times the largest landmark eigenvalue. Uniform landmarks are
   sampled without replacement from train only. Farthest-first starts from the
   point closest to the train centroid, then repeatedly adds the point farthest
   from the selected set. Class-balanced farthest-first applies the same rule
   within each train class quota, then fills any remainder globally. It is marked
   as using train labels for representation.
6. Random Fourier features approximate the selected RBF kernel with
   `sqrt(2 / m) cos(X W + b)`, `W ~ N(0, 2 gamma I)` and `b ~ Uniform(0, 2 pi)`.
   This is a stochastic fixed-feature reference, not a DNS novelty claim.
7. For every representation evaluate alpha [0.001, 0.01, 0.1, 1.0] and intercept
   [false, true] using the same closed-form readout objective as the readout
   diagnostic. Report the complete grid and a separate validation-selected view
   per representation/split. Tie-break by higher validation accuracy, then
   smaller alpha, then no intercept.
8. Report validation accuracy, RMSE, R2, train kernel reconstruction error where
   applicable, realized rank, feature budget, retained train samples, readout
   parameter count, solve time, readout inference time and representation time.
   Timings are descriptive single measurements and not energy claims.
9. Planned selected paired differences: uniform/farthest/class-balanced Nystrom
   192 minus spectral 192, RFF 192 minus spectral 192, farthest Nystrom 192 minus
   compiled 192, class-balanced Nystrom 192 minus fixed ReLU 256, and spectral
   192 minus full RBF.
10. Abort on numerical failures and log them. Do not adjust landmark counts,
    alpha grid, seeds or model list after seeing validation outcomes.

Decision: if simple landmarks approach the spectral reference and beat compiled
features, pause compiler-depth work and redirect DNS05 toward explicit kernel-map
compression. If landmarks also fail, investigate why the spectral extension works
before adding new nonlinear blocks.
