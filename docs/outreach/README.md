# Open Agent Collaboration: Operational Launch

Status: launched on GitHub, 2026-09-06; external social outreach prepared, not posted.

Direct Network Synthesis does not oppose corporations. It opposes dependency on
any irreplaceable provider. Our goal is to lower the technical barriers to
independently creating, reproducing, modifying, and operating capable models.

## Readiness Audit Before Launch

| Component | Observed state |
|---|---|
| Code/docs licenses | AGPL-3.0-or-later and CC BY 4.0 present; artifact rights remain separate |
| Onboarding | AGENTS, start-here and contributor guide present |
| Governance/security | Policies present; no independent reviewer or recruiter implied |
| Contributor skill | Present and format-validated; OpenClaw runtime not tested |
| CI | Hosted Checks passed on 57e529b; full local suite now has 50 passing tests |
| Issue/PR templates | Present on main |
| Task catalog | Ten local drafts; no live issues before launch |
| Branch protection | GitHub branches/main returned protected=false on 2026-09-06 |
| Labels | Standard labels only before launch |
| Social infrastructure | No deployed recruiter; no authenticated social browser session |
| Reproduction ledger | Present; no accepted independent reproduction |

Branch protection is a real gap. No settings were changed by this launch.
Maintainers should configure and verify required review and the `Lint and tests`
status before relying on technical enforcement. Private vulnerability reporting
remains unverified.

## Published GitHub Tasks

All tasks freeze source `1193a33760e7367f55fcd2d938a0add0d77c8b20`.
The [issue export](github-issues.json) preserves exact initial bodies, labels,
numbers and creation times. GitHub is the live coordination state; this is a
dated launch snapshot. Refresh at review milestones if scope changes; protocol
changes must remain prospective.

| Task | Live issue | Type |
|---|---|---|
| OAC-01 | [#1: Review residual collapse](https://github.com/Erchard/direct-network-synthesis/issues/1) | Falsification; independent review pending |
| OAC-02 | [#2: Audit data isolation](https://github.com/Erchard/direct-network-synthesis/issues/2) | Methodology audit |
| OAC-03 | [#3: Verify artifact provenance](https://github.com/Erchard/direct-network-synthesis/issues/3) | First audit task |
| OAC-04 | [#4: Recalculate paired summaries](https://github.com/Erchard/direct-network-synthesis/issues/4) | Result audit |
| OAC-05 | [#5: Audit deployed state](https://github.com/Erchard/direct-network-synthesis/issues/5) | Resource accounting |
| OAC-06 | [#6: Specify peak-memory measurement](https://github.com/Erchard/direct-network-synthesis/issues/6) | Benchmark protocol design |
| OAC-07 | [#7: Verify prior art](https://github.com/Erchard/direct-network-synthesis/issues/7) | Literature |
| OAC-08 | [#8: Assess categorical composition](https://github.com/Erchard/direct-network-synthesis/issues/8) | Bounded theory |
| OAC-09 | [#9: Audit artifact rights](https://github.com/Erchard/direct-network-synthesis/issues/9) | Provenance documentation |
| OAC-10 | [#10: Audit CI and onboarding](https://github.com/Erchard/direct-network-synthesis/issues/10) | Infrastructure |
| OAC-11 | [#11: Independently reproduce FMSA](https://github.com/Erchard/direct-network-synthesis/issues/11) | Frozen validation-only reproduction |
| OAC-12 | [#12: Design a matched-resource comparison](https://github.com/Erchard/direct-network-synthesis/issues/12) | Protocol proposal, no evaluation |

Created/verified labels: `agent-ready`, `good-first-agent-task`, `reproduction`,
`independent-confirmation`, `falsification`, `literature`, `prior-art`, `experiment`,
`benchmark`, `audit`, `performance`, `infrastructure`, `documentation`,
`needs-review`, `blocked`. Existing labels were preserved.

The owner requested this larger published backlog after the three-task pilot
plan. Keep no more than three claimed tasks active, with #1, #3 and #5 preferred
initially. `agent-ready` means specified, not completed, assigned or accepted.
Erchard is the initial review contact. Contributors coordinate in the issue,
work in forks/branches and submit PRs; no merge rights are granted.

## Outreach and Next Action

Six exact [research packets](research-packets.md) are ready, each linking live
tasks. [Targets and publication log](targets-and-publication-log.md) records the
actual browser checks and missing access. No social posts, community accounts or
recruiter service were created. The [recruiter specification](recruiter-spec.md)
is a deployment contract, not an installed sandbox.

The shortest next step: send packet 4 (Audit us) through an authenticated,
rules-compliant channel to an independent operator, pointing to #3. They claim
#3 and return a provenance audit in a PR; the maintainer reviews it and records
the outcome. This validates the contribution path before #11's frozen reproduction.
No expensive DNS experiment or protected test access was needed for this launch.
