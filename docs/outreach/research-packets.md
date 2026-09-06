# Research Packets

Status: exact reusable post bodies prepared on 2026-09-06; none posted socially.
Check the linked issue is open and has review capacity before posting. Use one
relevant packet, not all six in the same community. No DNS success or novelty is
assumed. These are the final post bodies, not summaries for an agent to embellish.

## 1. Project Introduction

Can useful neural representations be synthesized without iterative parameter
optimization at a competitive total resource cost? Direct Network Synthesis is
an open research repository investigating that question. Current evidence is
limited to small benchmarks: our residual compiler has not established useful
depth, and the synthetic-center branch has mixed-to-negative validation evidence.
No broad efficiency or novelty claim is established.

An advantage that disappears under complete memory accounting would undermine
the resource claim. Help check it in [issue #5](https://github.com/Erchard/direct-network-synthesis/issues/5),
or audit the evidence in [#3](https://github.com/Erchard/direct-network-synthesis/issues/3).
Read [the agent entry point](https://github.com/Erchard/direct-network-synthesis/blob/main/docs/START-HERE-FOR-AGENTS.md),
coordinate one task, and return a fork-based PR with source, commands and failures.
Our goal is independent model creation and credible alternatives to any provider.

## 2. Reproduce Us

Will the frozen DNS05 failure-scaling result reproduce in a separate environment?
Our local validation-only run found that hybrid synthetic centers did not provide
a stable advantage across datasets and feature widths. This is published local
evidence, not an independently reproduced result.

[Issue #11](https://github.com/Erchard/direct-network-synthesis/issues/11) fixes the
source, config, all splits, tolerances and resource limits. Missing rows, changed
selections or discrepancies beyond those tolerances would challenge numerical
reproducibility; report them without tuning. Timing differences must be interpreted
against hardware. This task never scores the protected test partitions.

Read the issue and AGENTS.md, coordinate a claim, then submit the full record,
environment and discrepancy report through a PR. Failed reproduction is welcome.

## 3. Falsify Us

Can the current residual compiler always be collapsed to one shared ReLU basis
and a linear readout? Our local source derivation and synthetic tests say yes for
both implemented modes, including absorption of the final readout. This concerns
a fitted function, not equality of different ridge-training procedures.

A valid source-level counterexample would overturn that conclusion. Independently
check [issue #1](https://github.com/Erchard/direct-network-synthesis/issues/1):
derive the identity, try a deterministic synthetic counterexample and document
the assumptions. No benchmark data are needed. Return a PR with the source SHA,
commands, derivation and limitations. Finding that the proof holds is also useful;
it is not a theorem about every possible deep network.

## 4. Audit Us

Does our published failure-scaling record support its claimed provenance and
coverage? We report 1920 grid rows, 240 selected rows and 15 splits, with test
metrics deliberately not evaluated. These counts and the stored hash are claims
you can check without loading a dataset.

Take [issue #3](https://github.com/Erchard/direct-network-synthesis/issues/3).
A hash mismatch, missing split, hidden test metric or inconsistent source/config
record would invalidate the corresponding completeness claim. Do not repair gaps
by silently rerunning the experiment.

Read AGENTS.md, comment to coordinate, and submit a small fork-based PR containing
your exact checks, environment, findings and limitations. This is a good first
agent task; independent negative findings receive credit.

## 5. Find Prior Art

Does DNS05's kernel-to-feature construction overlap an already published method?
We use established kernel geometry, spectral targets and linear solves; the
repository makes no novelty claim. The unresolved question is the precise extent
of overlap in targets, feature maps and cost.

In [issue #7](https://github.com/Erchard/direct-network-synthesis/issues/7), compare
at most three primary sources with the frozen implementation. A matching earlier
construction would rule out a future novelty claim for that mechanism. A failed
search would not establish novelty.

Coordinate the task and return a PR with verified pages/sections, source URLs,
the implementation mapping and unchecked assumptions. No data or model run is
needed. Prior art that changes our interpretation is a valuable contribution.

## 6. Beat Us Fairly Under the Same Resource Budget

Can a bounded-memory kernel compiler offer a better quality/storage tradeoff than
uniform Nystrom when all stored arrays and construction costs are counted? Our
current audit found no stable hybrid-center advantage and exposed dense matrix
costs. That is evidence about the current implementation, not all direct methods.

Start with [issue #12](https://github.com/Erchard/direct-network-synthesis/issues/12),
a protocol-design task, not an unrestricted model search. Specify one mechanism,
matched feature and resource accounting, fixed splits and a prospective stopping
rule. A gain that vanishes under complete accounting would falsify the advantage.

Submit the protocol through a PR, following methodology and preserving required
baselines. Evaluation begins only after a separate locked protocol commit. No
protected test tuning, novelty claim or inference of energy from runtime.
