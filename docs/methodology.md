# Methodology

## Definitions

Closed-form computation means a finite deterministic calculation such as a linear solve,
singular value decomposition, eigendecomposition, kernel construction, or fixed seeded
feature map.

Iterative parameter optimization means repeated parameter updates that use an objective,
loss gradient, coordinate update, evolutionary search, or other feedback loop to improve
model parameters. Gradient descent, backpropagation, Adam, LBFGS, and iterative random search
belong in this category.

DNS experiments must explicitly state which parameters are closed-form, fixed, selected on
validation data, or iteratively optimized.

## Data Separation

Every experiment must use separate train, validation, and test partitions.

- Training data may be used to fit preprocessing, feature synthesis, kernels, and closed-form
  readouts.
- Validation data may be used for model selection, hyperparameter selection, and protocol
  development.
- Test data may be used only once per finalized comparison.
- Test metrics must not be used to choose features, kernels, hyperparameters, seeds,
  preprocessing, model families, or reportable variants.

## Seeds and Reproducibility

Every stochastic or pseudo-random operation must use an explicit recorded seed.

Required seed records:

- dataset generation seed, when synthetic data is used;
- split seeds;
- fixed feature-map seeds;
- any sampling seed used inside a DNS variant.

An experiment result must include the exact configuration, commit SHA, and command used to
produce it before it is treated as reportable.

## Baselines

At minimum, DNS variants must be compared against:

1. linear ridge regression;
2. RBF kernel ridge regression;
3. deterministic ReLU features with closed-form ridge readout.

Additional baselines may be added later, but the minimum set should remain stable so that
regressions are visible.

## Reporting

Report mean and standard deviation across multiple fixed splits. Single-split results may be
used for debugging, but they are not reportable evidence.

For each model, report at least:

- validation RMSE;
- validation R2;
- test RMSE;
- test R2;
- number of splits;
- whether any iterative parameter optimization was used.

## Tuning Rules

Permitted:

- choosing hyperparameters using training and validation data only;
- fixing a hypothesis before running test evaluation;
- reporting negative and inconclusive results.

Not permitted:

- tuning on the test set;
- changing preprocessing after viewing test metrics;
- changing split seeds to improve results;
- hiding failed DNS variants;
- describing a model as closed-form if it uses iterative parameter updates.

## Result Records

Raw result files belong under `results/` and are ignored by Git by default. Curated summaries
may be committed when they include enough protocol detail to be reproduced.
