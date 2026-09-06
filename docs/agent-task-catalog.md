# Agent Task Catalog

Status: version 1 task drafts, 2026-09-06. These are repository-local drafts,
not published GitHub issues or installed labels. A maintainer can turn one into
an issue using the research-task form after assigning a full source commit.
Search existing issues first to avoid duplicates. Label `agent-ready` only after
all inputs, data boundaries, commands and acceptance criteria are filled in.

## Label Taxonomy

| Label | Meaning |
|---|---|
| agent-ready | Bounded, reviewed task with complete inputs and acceptance criteria |
| good-first-agent-task | Small task requiring no new experiment or protected data |
| reproduction | Re-execute a frozen protocol with an auditable environment |
| falsification | Attempt to disprove a specific claim under stated controls |
| literature | Verify primary literature and document its relevance |
| prior-art | Identify a source establishing overlap with a specific method |
| experiment | Requires a separately locked protocol before evaluation |
| benchmark | Measure resource costs under a fixed measurement protocol |
| audit | Check existing code or evidence without altering the candidate |
| security | Report or resolve a security issue using SECURITY.md |
| infrastructure | Improve contributor or execution infrastructure |
| documentation | Correct or clarify documentation against source evidence |
| performance | Investigate a measured implementation bottleneck |
| independent-confirmation | Requires a fresh, explicitly protected evaluation boundary |
| blocked | Required input or external dependency is missing |
| needs-review | Output is ready for maintainer assessment |

## Shared Contract for the Drafts

All ten drafts below are static reviews or synthetic unit checks. No benchmark
dataset may be loaded, transformed or scored; all raw train/validation/test data
and additional test outcomes are outside scope. Published aggregate records may
be read as specified. Do not regenerate them. New experimental work needs a
separate locked protocol.

Record `git rev-parse HEAD` before work. For source inspection use `git show
HEAD:<input-path>` for each listed file. Code checks, where applicable, are
`python -m ruff check .` and `python -m pytest`; installation follows README.
Proposed effort limit is two hours per task; stop with a partial report and
explicit unresolved questions if that limit is reached. No remote compute or
paid services are required. Put the report at the per-task path below, including
source SHA, commands, environment, sources, negative findings and limitations.

Each draft supplies its objective, inputs and output. Acceptance means an
auditable answer, including a negative one; it does not mean confirming DNS.

## Draft Tasks

### OAC-01: Check residual-block collapse

Labels: `falsification`, `good-first-agent-task`.
Input: `src/dns/synthesis/dns05_kernel_compiler.py`, especially `transform` and
`_CompiledResidualBlock`. Explain algebraically whether concatenated projections
of the shared basis can be represented by one map. Output:
`docs/audits/oac-01-residual-collapse.md`. Acceptance: map the derivation to actual
code and identify the assumptions. Stop if a proposed construction requires new
data or architecture changes; record the unresolved case instead.

### OAC-02: Audit validation-only isolation

Labels: `audit`.
Inputs: `experiments/run_dns05_failure_scaling.py`,
`tests/test_failure_scaling_audit.py`, its locked config and protocol. Trace every
split and metric call. Output: `docs/audits/oac-02-data-boundary.md`; a minimal
synthetic unit test is allowed for a concrete uncovered leakage path. Acceptance:
identify protected-data handling by function and line, or a reproducible defect.
Do not execute the benchmark runner.

### OAC-03: Verify FMSA artifact provenance

Labels: `audit`, `good-first-agent-task`.
Inputs: `docs/results/dns05_failure_scaling_audit.json` and its research-log entry.
Parse the JSON and recompute its SHA256 without dataset access. Output:
`docs/audits/oac-03-provenance.md`. Acceptance: check source SHA, config, command,
environment, row counts and absent test metrics; list missing metadata explicitly.
Do not substitute a rerun for a missing provenance field.

### OAC-04: Recalculate paired summaries

Labels: `audit`.
Inputs: the same FMSA result JSON, `docs/research-log.md` and the summary functions
in its runner. Recompute paired means and sample standard deviations from the
published per-split rows. Output: `docs/audits/oac-04-paired-summary.md` with a
reproducible calculation. Acceptance: show split/model alignment and rounding
tolerance for every checked table entry. Fail explicitly on missing pair members;
do not silently drop them or treat overlapping splits as independent samples.

### OAC-05: Audit deployed-state accounting

Labels: `audit`, `performance`.
Inputs: `experiments/run_dns05_failure_scaling.py` and its representation builders.
Trace which arrays survive for inference and which are construction-only.
Output: `docs/audits/oac-05-state-accounting.md`. Acceptance: a parameterized byte
formula per representation, including dense matrices and retained samples,
checked against existing rows. Report estimates separately from peak process RAM.

### OAC-06: Specify a peak-memory measurement protocol

Labels: `benchmark`, `infrastructure`.
Inputs: `docs/dns05-failure-scaling-audit-protocol.md`,
`experiments/run_dns05_failure_scaling.py`, research-plan section 4. Output:
`docs/audits/oac-06-memory-proposal.md`. Acceptance: define process boundaries,
warmup, repeats, platform limitations, resource cap and inclusion of oracle and
selection costs. This is a protocol proposal, not authorization to run it.

### OAC-07: Verify kernel-to-network prior art

Labels: `literature`, `prior-art`.
Inputs: `docs/related-work-kernel-approximations.md` and the DNS05 implementation.
Read primary sources for at most three closely related constructions. Output:
`docs/audits/oac-07-prior-art.md`. Acceptance: bibliographic links, verified pages
or sections, exact overlap, differences and unchecked claims. Mark inaccessible
full text as unverified; do not infer novelty from a failed search.

### OAC-08: Assess categorical composition assumptions

Labels: `literature`, `falsification`.
Inputs: research-plan section 3B, DNS05 source and Fong, Spivak and Tuyeras,
https://arxiv.org/abs/1711.10455. Read the relevant full-text definitions.
Output: `docs/audits/oac-08-composition.md`. Acceptance: identify which assumptions
apply to DNS and supply one precise derivation, counterexample or unresolved
obligation. A categorical description of gradient descent is not evidence of
direct weight synthesis. Stop if no concrete consequence can be established.

### OAC-09: Audit artifact licensing provenance

Labels: `audit`, `documentation`.
Inputs: `docs/licensing.md`, `pyproject.toml`, dataset definitions and existing
result metadata. Output: `docs/audits/oac-09-artifact-rights.md`. Acceptance: a
source-linked inventory of dataset/dependency terms and unresolved redistribution
questions. Do not download raw data, relicense third-party material or treat this
inventory as a legal certification.

### OAC-10: Review untrusted-PR CI execution

Labels: `security`, `infrastructure`.
Inputs: `.github/workflows/checks.yml`, `SECURITY.md`, `GOVERNANCE.md` and relevant
official GitHub documentation. Output: `docs/audits/oac-10-ci-review.md`.
Acceptance: document triggers, permissions, action pins, credential persistence,
runner isolation and the difference between CI and branch-protection enforcement.
Do not request secrets, change repository settings or execute an exploit.

## Promotion to Reproduction

After these drafts, a separate `reproduction` issue can freeze a validation-only
protocol, source SHA, config, environment, data access, runtime cap and output
path. A maintainer must fill those fields before applying `agent-ready`.
Independent execution must be reviewed under the [ledger rules](reproduction-ledger.md).
No task in this catalog authorizes confirmation-test reuse or social posting.
