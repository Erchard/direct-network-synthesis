# Contributing

Contribute reproducible evidence, including failures. Start with [AGENTS.md](AGENTS.md)
and follow its reading order. [Methodology](docs/methodology.md) is binding.

## One Bounded Contribution

Choose an open task with clear inputs, allowed data, expected output and acceptance
criteria. Use the [task catalog](docs/agent-task-catalog.md) if no issue is ready.
Coordinate ownership in the issue before substantial work. External contributors
use a fork or their own branch and submit a PR; they do not need access to `main`.

An issue is not permission to run an unregistered experiment. Lock new protocols,
variants, seeds and selection rules before evaluation. Historical README commands
can evaluate test data; inspect the runner and protocol before executing them.
Never rerun protected tests merely to verify installation. A new split seed does
not make an explored dataset independent evidence.

## Evidence Package

Every research PR identifies its issue, hypothesis, source commit, exact command,
environment, config, all data inspected, protected data, complete results,
negative outcomes and limitations. Record per-split metrics and paired comparisons
as required by the protocol. State whether parameters were computed, fixed,
validation-selected or optimized iteratively. Link the research-log update.

Describe the human operator or accountable submitting account and any AI tools
used. Do not publish credentials, private conversations or personal information
to prove identity. Report independence honestly: a new agent in the same checkout
is not independent reproduction.

## Checks and Review

From an environment installed with `python -m pip install -e ".[dev]"`, run:

```text
python -m ruff check .
python -m pytest
git diff --check
```

Documentation-only work needs link/diff review; numerical or shared protocol
changes require the full test suite. CI runs lint and tests on PRs. Passing CI
does not validate scientific claims or enforce all data boundaries. Maintainer
review is required by [governance](GOVERNANCE.md); server-side branch protection
must be configured separately before claiming it is technically enforced.

Provide only material you can submit under [the applicable licenses](docs/licensing.md).
Preserve authorship, provenance and third-party terms. Negative or inconclusive
findings are welcome; no contribution is required to support DNS.
