# Agent Discovery Strategy

Status: strategy and artifacts prepared, 2026-09-06. No external registry,
marketplace or social account is configured by these files.

The project should be discoverable through several layers. Each layer solves a
different problem and may disappear or change independently:

| Layer | Function for DNS | Current status |
|---|---|---|
| GitHub | Canonical issues, PRs, code and evidence | Active and verified |
| Agent social networks | Human/agent discovery and discussion | No account or post |
| Agent directories/registries | Capability discovery and routing | Research target |
| Agent service markets | Optional paid task execution | Research target; no listing |
| Open agent protocols | Interoperability and machine-readable capability exchange | Research target; no endpoint |

The operational rule is: social platforms and marketplaces are discovery
channels; GitHub remains the source of truth. A registry entry must point to
specific live issues and public artifacts. A protocol endpoint must not imply
that the project can execute arbitrary remote work, accept payments, expose
credentials or access protected evaluation data.

## Candidate Ecosystem

The following claims were checked against primary project sources on 2026-09-06:

- [A2A and Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents): an open agent-to-agent protocol project under Linux Foundation governance. This is interoperability context, not evidence that DNS needs or implements A2A.
- [Agentverse Marketplace](https://docs.agentverse.ai/v-2/documentation/getting-started/agentverse-marketplace): Fetch.ai documentation describes a searchable marketplace/Almanac connection and several deployment modes. This is a platform-specific registry target, not a decentralized guarantee.
- [OpenServ Agent Market](https://platform.openserv.ai/): the platform describes pay-per-use agent services. No DNS listing or account is implied.
- [Agent Network Protocol](https://agentnetworkprotocol.com/en/): the project describes open specifications for agent description, discovery, identity and communication. Its status and compatibility with A2A require separate verification.
- [OpenClaw skills](https://docs.openclaw.ai/tools/skills): skills are markdown instruction files loaded by an OpenClaw environment. Our contributor skill is portable Markdown; runtime loading has not been tested.

Marketing counts, rankings and platform activity are not project evidence.
Before using a platform, verify current terms, authentication, ownership,
moderation and export options. Do not infer decentralization from the existence
of a public directory.

## Capability Card Draft

The [capability-card-draft.json](capability-card-draft.json) is a small
protocol-neutral description for human review and future adapters. It is not an
A2A Agent Card, ANP description, Agentverse manifest or deployed endpoint. Do
not publish it at `/.well-known/agent.json` until the selected protocol schema,
authentication, endpoint hosting, rate limits, data boundary and shutdown path
have been verified.

The card advertises research coordination capabilities and links to GitHub tasks.
It does not promise that DNS can execute a task remotely. Contributors still
work through forks/branches and PRs under the repository rules.

The first static comparison of candidate layers is in
[comparison-matrix.md](comparison-matrix.md). It currently favors studying A2A
as the first protocol adapter and Agentverse as the first platform registry,
subject to separate schema, identity, security and export audits.

Operators who want to connect an external agent should first read the
[operator channel guide](operator-channel-guide-uk.md). A public discovery card
does not automatically create an inbound channel to a Codex session; use the
manual relay first and add an approved connector only after a bounded security
review.

## Promotion Gate

Choose a protocol adapter only after a bounded static audit identifies a real
discovery benefit. Then freeze its schema, endpoint, identity, allowed messages,
authentication, logging, budget and stop conditions in a separate protocol. Test
with synthetic messages and a non-production endpoint first. A listing or card
is successful only if an independent agent can find the exact task, understand
the evidence boundary and return a reviewable GitHub artifact.
