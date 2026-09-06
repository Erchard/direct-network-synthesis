# Guide for AI Contributors

This guide is for language models and coding agents joining Direct Network
Synthesis (DNS). Read the root [AGENTS.md](../AGENTS.md) first. The goal is to help
the next contributor continue from evidence rather than restart from speculation.

## 1. Understand the Project

We investigate whether useful neural representations and weights can be computed
by deterministic construction and linear algebra without iterative parameter
optimization. DNS 0.5 attempts to compile a strong RBF kernel's geometry into a
compact representation. Success is an open question, not an assumption.

The longer-term motivation is affordable independent model creation. Reducing
training costs could lower barriers to participation; it does not prove that data
centers become unnecessary or that monopoly becomes impossible. Read
[Hypothesis](hypothesis.md) for these distinctions.

## 2. Establish Context Before Acting

1. Follow the reading order in AGENTS.md. Both conceptual-foundations documents
   preserve reasoning history; their exploratory numbers are not repository evidence.
2. Read [Methodology](methodology.md) as the binding protocol. The
   [research plan](research-plan.md) orders future work but does not replace a
   locked experiment-specific protocol.
3. Read recent [research-log](research-log.md) entries and the cited result records.
   Check commits and timestamps; this guide's snapshot may become stale.
4. Inspect `git status --short`, the current branch, recent commits and configured
   remotes. Preserve uncommitted work and do not assume you are on `main`.
5. Inspect the code, configs and tests for the requested task. Report the difference
   between implemented behavior and proposed behavior before extending the system.
6. Choose one bounded contribution within the user's request. Do not automatically
   execute the entire roadmap or launch expensive experiments merely by joining.

## 3. Navigate the Implementation

| Location | Purpose |
|---|---|
| `src/dns/synthesis/dns04.py` | SVD-derived ReLU features and ridge readout |
| `src/dns/synthesis/dns05_kernel_compiler.py` | Kernel combiner and residual feature compiler |
| `src/dns/synthesis/linear_algebra.py` | Shared solves and shape handling |
| `src/dns/features/` | Preprocessing and feature construction |
| `src/dns/baselines/` | Linear, kernel and fixed-feature reference models |
| `experiments/run_dns05_depth_width.py` | Digits comparisons, selection and reporting |
| `configs/` | Recorded experiment settings and seeds |
| `tests/` | Numerical behavior and data-separation checks |
| `results/` | Ignored generated experiment outputs |
| `docs/results/` | Curated committed evidence |

Do not confuse `DNS05KernelCompiler`, the weighted kernel combiner, with
`DNS05CompiledFeatureClassifier`, the actual feature compiler.

## 4. Know the Current Evidence

Snapshot as of 2026-09-06 after DNS05-FMSA and collaboration launch; verify newer log entries before
relying on it:

1. The 192-feature compiler and partitioned/full-basis residual variants have been
   evaluated on five digits splits. Residual construction did not outperform the
   one-shot model. Full-basis access improved reconstruction relative to partitioning.
2. Every current block projects the same fixed nonlinear basis. Concatenated
   projections can collapse to one projection; block count is not neural depth.
3. Matched-readout, landmark, cost and error-geometry diagnostics have been
   completed on validation-only digits development splits. Full RBF and spectral
   remain strong references; uniform Nystrom 192 is the best observed compact
   candidate if retaining 192 train-derived landmarks is acceptable.
4. Train-sample-free synthetic centers remain interesting but are not confirmed.
   Class-PCA prototypes nearly matched uniform Nystrom without retaining train
   rows; dipole and hybrid variants improved development numbers slightly. The
   fresh DNS05-FC1 confirmation was mixed: hybrid prototypes did not clearly
   transfer on `sklearn_breast_cancer`, beat uniform Nystrom on the fixed
   synthetic multiclass task, and remained below spectral/full RBF references.
5. The follow-up failure/scaling audit is now complete; its mixed-to-negative
   results are in the research log. Center-formula tweaking on inspected
   boundaries remains paused. The [operational task index](outreach/README.md)
   now provides live issues for independent audit/reproduction. A local
   residual-collapse proof has synthetic checks but awaits independent review.
   Proposed new mechanisms remain bounded-memory maps or genuine nonlinear
   composition, each requiring a separate locked protocol.
6. Complete records live under `docs/results/`. Use those records for exact
   values and uncertainty rather than conversational rounding.

## 5. Protect the Experimental Boundary

1. Train data may fit preprocessing, kernels, representations and weights.
   Validation may select among preregistered options. Test data evaluates the final
   locked comparison once and must not guide subsequent model selection.
2. Existing digits test partitions have already been inspected. Reusing them or
   changing split seeds does not establish independent confirmation. Development
   work must respect the documented train/validation boundary.
3. Verify that validation-only runs do not compute test predictions or metrics.
   Missing test fields must be explicit, not replaced by validation values.
4. Record every seed, including splits, feature maps, synthetic data and sampling.
   Do not try seeds until a favorable result appears.
5. Keep mandatory baselines and a fair selection allowance. Label iterative
   optimization honestly when adding a gradient-trained reference.
6. Never alter model choices after examining test outcomes to rescue a result.
   Record failures and define an independent evaluation boundary for revised work.
7. Do not change methodology quietly to fit an implementation. Identify a mismatch
   explicitly and resolve it before treating results as reportable evidence.

## 6. Carry an Experiment Through to a Reviewable Result

1. Write the question, predicted mechanism and falsifying outcome.
2. Freeze datasets, splits, seeds, variants, selection/tie rules, primary metrics,
   resource limits and stopping conditions in a protocol and config.
3. Implement the smallest relevant change using existing helpers. Test numerical
   equivalence, train-only fitting and unseen-input behavior where those are at risk.
4. Use synthetic or train/validation-only checks for debugging. A one-split smoke
   run is not reportable evidence, and a test-evaluating run is not a harmless smoke check.
5. Commit code and protocol before the finalized evaluation. Prefer a clean
   worktree; disclose any deviations and preserve the exact source state.
6. Run all locked variants across the recorded splits. Do not stop when the first
   favorable number appears. Record failures, exhausted resources and partial runs.
7. Preserve config, source SHA, exact command, dependency versions and hardware.
   Keep full per-split measurements and enough detail to reproduce selections.
8. Report mean, sample standard deviation and paired differences. Distinguish
   output dimension, realized rank, basis size, parameter count and stored samples.
   Do not equate overlapping splits with independent statistical observations.
9. Include validation/test RMSE and R2 as required by methodology and task-specific
   accuracy for classification; state whether metrics use scores or hard labels.
   Report kernel error's domain (train or held-out), solve and inference costs.
10. Explain supported conclusions, confounds and negative outcomes. Separate
    measured evidence from proposed explanations and future experiments.
11. Update the research log, commit curated records and push the milestone. Give
    the user a short outcome, limitations, verification and commit reference.

## 7. Use the Environment and Git Carefully

The project requires Python 3.11 or newer. Use the existing environment when it is
available; otherwise follow the README setup instructions. Do not assume a bare
`python` command resolves to a working interpreter on Windows.

Typical checks from the repository root in PowerShell:

```powershell
& '.venv/Scripts/python.exe' -m ruff check .
& '.venv/Scripts/python.exe' -m pytest
git diff --check
```

Run checks appropriate to the change; documentation-only edits do not require
training or test-set evaluation. Do not run checks concurrently with timed benchmarks.
Historical experiment commands in README can access test data: inspect their
behavior and the protocol before execution.

Before committing, review the diff and stage only the intended files. Do not
overwrite concurrent work, reset the worktree or force-push. When sharing a
checkout, coordinate ownership; an isolated branch/worktree can avoid collisions.

The repository is `Erchard/direct-network-synthesis`. Verify the intended remote
and branch before pushing. The owner has requested that meaningful milestones be
pushed, but follow any newer instruction limiting publication. Existing credentials
should be used through normal Git authentication. Do not invent a need for new keys
or expose secrets. If authentication fails, report the actual error and use only
authorized alternatives; do not change account or remote configuration silently.
Confirm success from Git's response and report any remaining blocker honestly.

## 8. Leave a Useful Handoff

At a pause or completed milestone, leave the following in the research log or an
appropriate linked note so another agent can continue without guessing:

- Objective and current status: planned, implemented, evaluated or independently reproduced.
- Relevant branch/commits, changed files and any uncommitted work.
- Tests/checks run, commands, outcomes and known failures.
- Protocol/config/result paths, data already inspected and protected evaluation data.
- Main finding, uncertainty, rejected explanations and negative variants.
- Exact next bounded action and any running process or external blocker.
- Push status, including the destination and confirmed commit.

Be candid and concise with the user. The contribution is valuable when another
person or agent can audit it, reproduce it and disagree with its interpretation.
