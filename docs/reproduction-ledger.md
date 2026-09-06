# Reproduction Ledger

Status, 2026-09-06: no independently reviewed reproduction is recorded here yet.
Existing local experiment runs are documented in [Research Log](research-log.md).

## Pending Local Contribution

OAC-01: residual-collapse derivation and eight additional synthetic checks,
commit `1193a33760e7367f55fcd2d938a0add0d77c8b20`, produced by the owner-authorized
local Codex agent. [Report](audits/oac-01-residual-collapse.md) includes source,
commands, seeds, tolerances, environment and limitations. All 50 local tests
passed. No benchmark partitions were accessed. Independent review is requested
in [issue #1](https://github.com/Erchard/direct-network-synthesis/issues/1).
Review contact: Erchard; no completed independent review or review date yet.
Status: pending independent review, no Independent Reproducer credit awarded.

## Acceptance Rules

Maintainers mark entries accepted only after review, preserving failures and
disagreements. Pending local submissions above confer no accepted status.
Each entry must contain:

- Contributor/account and declared AI tools, with consent to public attribution.
- Contribution type and issue/PR URL.
- Original source commit and reproduction source commit.
- Protocol/config, exact commands, environment and artifact hash/location.
- Data accessed and independence from original code execution, environment and
  protected evaluation; disclose shared data and overlapping splits.
- Outcome, differences, negative findings and limitations.
- Reviewer, review date and status: pending, accepted, inconclusive or rejected.

An accepted independent reproduction needs a separate execution environment and
an auditable record assessed by a reviewer. Reusing published results, rerunning
in the author's checkout, or changing the model name does not meet that criterion.
Reproduction of the same protocol is not fresh confirmation on untouched data.
