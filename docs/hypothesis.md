# Hypothesis

## Research Intent

This project investigates direct, non-iterative synthesis of neural network parameters and
representations. In this repository, "direct" means that trainable quantities are produced
by deterministic feature construction, kernel construction, decomposition, or closed-form
linear algebra rather than by iterative gradient-descent weight updates.

The goal is not to prove novelty. The goal is to test a clearly stated research program
against strong simple baselines and to keep enough evidence that later conclusions can be
audited.

## Primary Question

Can directly synthesized representations or parameters generalize well enough to be useful
when compared under the same protocol against linear ridge regression, RBF kernel ridge
regression, and deterministic ReLU-feature ridge regression?

## Working Hypotheses

1. Some useful nonlinear behavior can be obtained by fixed or closed-form feature maps with
   only a closed-form output solve.
2. Kernel methods are a necessary reference point because they already perform non-iterative
   fitting through a dual closed-form solve.
3. DNS variants should be evaluated as synthesis procedures, not as trained neural networks,
   unless an experiment explicitly introduces iterative optimization.
4. A DNS result is not persuasive unless it is stable across multiple fixed splits and is
   compared to simple baselines.

## Long-Term Motivation: Accessible Model Creation

**Status: research motivation and unverified hypotheses, not experimental results.**

Iterative gradient updates are not required by every neural model: restricted
constructions can use fixed hidden features and directly computed output weights.
The stronger question is whether useful weights throughout a powerful model can
be computed directly, potentially after a single pass over its training data.
This is an aspiration to test, not an established property of arbitrary networks
or a capability demonstrated by the current DNS compiler.

If such a method preserved model quality while substantially reducing total
computation, memory and energy costs, it could make strong model creation
accessible to smaller teams and individuals. This could weaken a source of
corporate concentration: the capital required for large training infrastructure.
Broadening access to model creation is a long-term motivation for DNS.

The proposed chain of implications must be tested one step at a time:

1. Direct weight computation can produce useful representations.
2. It can preserve competitive quality on demanding tasks and at larger scales.
3. It reduces total resource costs, including preprocessing and matrix solves.
4. Those savings lower practical barriers to independent model creation.

A single data pass does not imply a cheap computation: expensive work and large
stored intermediate representations may remain after the pass. Direct synthesis,
single-pass data access and low total cost are separate properties. The current
compiler constructs a dense training kernel and performs decompositions; it does
not demonstrate cheap single-pass learning.

Even a successful synthesis method would not by itself eliminate inference costs,
data processing, storage or the need for data centers. Nor would it make corporate
monopoly impossible: access to data, distribution and users can remain advantages.
Claims about infrastructure becoming unnecessary or corporate concentration
disappearing are therefore not conclusions of this project.

Evidence for the technical ambition would require matched-quality comparisons
with strong alternatives, measuring total computation time, peak memory, data
passes, storage and inference costs, with energy measured before making energy
savings claims. Current digits results establish none of the broader economic
implications. The binding experimental protocol remains `docs/methodology.md`.

## Non-Claims

- No claim of novelty is made by this repository.
- No claim is made that direct synthesis will outperform gradient-trained neural networks.
- No result should be described as successful until it survives the methodology in
  `docs/methodology.md`.
