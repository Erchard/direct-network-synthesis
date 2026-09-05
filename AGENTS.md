# Instructions for AI Contributors

This is a research repository, not a request to demonstrate that DNS succeeds.
Contribute reproducible evidence, including failures. Follow the user's task scope.

Before changing code or proposing an experiment, read:

1. `README.md`
2. `docs/conceptual-foundations-en.md` and `docs/conceptual-foundations-uk.md`
3. `docs/hypothesis.md`
4. `docs/methodology.md` (binding experimental protocol)
5. `docs/research-log.md`
6. `docs/research-plan.md`
7. `docs/ai-contributor-guide.md`

Then inspect the working tree and relevant implementation, especially
`src/dns/synthesis/dns04.py`, `src/dns/synthesis/dns05_kernel_compiler.py`,
the experiment runners, configs and tests. Documentation can describe future work;
verify what actually exists before claiming it is implemented.

Non-negotiable research rules:

- No test-set tuning. Previously inspected digits test splits are not fresh evidence.
- Fit preprocessing and representations on train only; select on validation only.
- Lock protocols, variants and recorded seeds before evaluation; use multiple splits.
- Preserve all negative and inconclusive outcomes. Never silently discard variants.
- Record exact config, source commit, command and environment with results.
- No novelty claims without verified related work. Conceptual chat numbers are not
  canonical results. Direct computation does not imply cheap or single-pass learning.
- Current residual blocks do not establish compositional neural depth.

For code changes, run relevant tests and `python -m ruff check .`; use
`python -m pytest` for shared numerical/protocol changes. Do not run historical
test-evaluating experiment commands just to check installation.

Update `docs/research-log.md` at research milestones. Commit meaningful scoped
changes and push to the intended repository/branch under the user's authorization.
Never overwrite others' work, force-push, change authentication or claim a push
succeeded without evidence. See the contributor guide for the complete workflow.
