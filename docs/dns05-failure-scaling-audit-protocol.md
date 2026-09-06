# DNS05 Failure-Mode and Scaling Audit Protocol

Status: locked before evaluation.

This protocol follows `docs/methodology.md`. It is a train/validation-only
diagnostic, not a confirmation experiment. It must not compute test predictions
or use excluded partitions for model choice.

## Objective

The DNS05 fresh-confirmation result was mixed: hybrid synthetic centers helped on
one fresh boundary and slightly trailed on another. The next justified step is
not to tune the hybrid formula against inspected test outcomes. The next step is
to measure failure modes across feature budgets:

- whether synthetic centers lose rank;
- whether they fail to cover train geometry under the selected RBF kernel;
- whether kernel reconstruction error tracks validation accuracy;
- whether dense kernel and inverse-root steps dominate solve and inference cost;
- whether uniform Nystrom or spectral references expose a simpler explanation.

## Locked Inputs

Run command:

```powershell
python -m experiments.run_dns05_failure_scaling --config configs/dns05_failure_scaling_audit.json --output results/dns05_failure_scaling_audit.json
```

Datasets and split seeds are fixed in
`configs/dns05_failure_scaling_audit.json`:

- `sklearn_digits`, seeds `101, 202, 303, 404, 505`;
- `sklearn_breast_cancer`, seeds `1101, 1202, 1303, 1404, 1505`;
- `synthetic_multiclass_v1`, fixed generator seed `90210`, split seeds
  `2101, 2202, 2303, 2404, 2505`.

Each split uses stratified `60% / 20% / 20%` train, validation and excluded
partitions. The excluded partition is recorded but not evaluated.

## Locked Models

For feature budgets `32, 64, 128, 192, 256`, compare:

- `prototype_class_hybrid`: the frozen hybrid synthetic-center construction from
  DNS05-HYB/FC1, with shift fraction `0.25`, two boundary pairs per class and
  fixed PCA quantiles;
- `nystrom_uniform`: uniform train-sample landmarks with fixed seed arithmetic;
- `spectral`: compact spectral RBF reference at the same requested rank.

Include exact `rbf` once per split as an oracle reference, not as a width-matched
compact model.

The RBF gamma is selected using train and validation data only with the fixed
grid in the config. Readout alpha and intercept are selected on validation only.
Tie-breaking is fixed as:

1. higher validation accuracy;
2. lower validation RMSE;
3. lower alpha;
4. `intercept=false` before `intercept=true`.

## Metrics

For every grid row and validation-selected row, record:

- validation accuracy, RMSE and R2;
- null test accuracy, RMSE and R2;
- kernel reconstruction error;
- requested feature count, actual feature budget, rank, rank fraction and
  effective rank;
- basis rank and condition number for center-based representations;
- mean, standard deviation, fifth percentile, median and minimum train-to-basis
  maximum RBF similarity;
- coverage fractions above RBF similarity `0.5` and `0.8`;
- retained train samples and exact train-row center matches;
- model state bytes, intermediate array bytes;
- train feature-construction time, validation feature-transform time, readout
  grid solve time and repeated validation inference time;
- paired differences by dataset, split and requested feature budget.

## Predicted Outcomes

Falsifying or negative outcomes are expected and must be recorded. In particular:

- If hybrid centers trail uniform Nystrom across most budgets while having lower
  coverage or lower rank, the synthetic-center branch is not yet confirmed.
- If hybrid centers match Nystrom only when using train labels, this is a
  development clue, not an architectural breakthrough.
- If dense kernel construction or inverse-root cost dominates, the next method
  should target bounded-memory kernel maps instead of another synthetic-center
  formula.
- If spectral remains much stronger at similar budgets, the residual/depth idea
  needs a new mechanism that actually composes reusable representations.

No novelty, energy, decentralization or large-scale training claims may be drawn
from this audit.
