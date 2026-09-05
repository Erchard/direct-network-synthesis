# DNS 0.5 Cost-Accounted Compression Diagnostic

Status: locked before development evaluation, 2026-09-05.

Question: among the already studied compact RBF-geometry approximations, which
ones have a defensible quality/resource tradeoff on reused digits development
splits? This is validation-only development evidence, not test evidence and not
an energy claim.

1. Use the same digits split seeds 101, 202, 303, 404 and 505 at 60/20/20. Only
   train and validation arrays enter evaluation. Excluded split members are not
   transformed, predicted or scored. The runner records null test fields.
2. Use train-only standardization and the same shared RBF oracle selection grid:
   gamma multipliers [0.5, 1.0, 2.0] and alpha [0.001, 0.01, 0.1]. Record this
   selection time separately. RBF-derived models get two accounting views:
   model-fit time without the shared oracle selection and model-fit time with
   the shared development selection included.
3. Evaluate only previously studied model families: linear, fixed ReLU 256,
   PCA ReLU 192, compiled 192, RFF 64/128/192, uniform/farthest/class-balanced
   Nystrom 64/128/192, spectral 64/128/192 and full RBF. Do not add new model
   families, widths, alpha values or seeds in this diagnostic.
4. Use the same closed-form readout grid as before: alpha [0.001, 0.01, 0.1,
   1.0] and intercept [false, true]. Select by validation accuracy per
   model/split, breaking ties by smaller alpha and then no intercept. This is
   developmental and optimistic.
5. Record separate timing fields for preprocessing, gamma/oracle selection,
   train feature construction, validation feature transform, readout-grid solve,
   selected readout inference over precomputed validation features and full
   validation prediction as transform plus selected readout inference.
6. Benchmark selected readout inference with two warmups and nine measured
   repeats on validation features only. Repeated timing is for cost measurement;
   it must not alter selection or produce test scores.
7. Record approximate model-state bytes needed for inference, excluding Python
   object overhead but including numerical arrays: standardizer statistics,
   feature-map parameters, landmarks or retained train samples, normalizers,
   spectral extension matrices and selected readout weights/dual coefficients.
   Also record the largest dense intermediate-array byte estimate observed by
   the runner and a `tracemalloc` peak for the representation build. These are
   estimates, not exact operating-system RSS measurements.
8. Record retained train samples. Nystrom stores its landmarks; spectral stores
   the train set for out-of-sample extension; full RBF stores the train set and
   dual coefficients. Linear/fixed ReLU/RFF/PCA-ReLU/compiled store no train
   examples for inference.
9. Report validation accuracy, RMSE, R2, kernel error where applicable, rank,
   feature budget, retained train samples, solve time, inference time, model
   bytes and construction timings. Include paired differences for selected
   Nystrom, spectral, RBF, fixed ReLU and compiled comparisons.
10. Do not infer energy consumption from this diagnostic. Direct energy
    measurement remains unavailable unless a later protocol records it directly.
    Do not use these results to tune any test set.

Decision: a candidate is worth future untouched-data confirmation only if it is
near the full RBF validation accuracy while using clearly less retained state or
prediction work than the full RBF, and it remains competitive with fixed ReLU.
If the best candidate depends mainly on stored landmarks, describe the result as
kernel-map compression, not as a train-sample-free neural synthesis result.
