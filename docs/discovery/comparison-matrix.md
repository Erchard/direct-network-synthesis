# Discovery Layer Comparison

Status: static comparison, 2026-09-06. This is a design input, not a platform
recommendation or an interoperability result. Claims below come from the linked
official pages; unknowns remain unknown until a separate access audit.

| Candidate | Main role | How DNS could appear | Identity/authentication | Portability and lock-in | Cost/payment | Safe first pilot |
|---|---|---|---|---|---|---|
| A2A | Open agent-to-agent interaction and capability description | An actual A2A Agent Card at a verified HTTPS endpoint, linking GitHub tasks | Card declares interfaces and security; signing and endpoint controls need implementation | Open specification, but hosting and client compatibility still create operational dependencies | No payment required for a metadata card; endpoint hosting has cost | Static schema validation and synthetic request handling; no remote code execution |
| Agentverse | Platform registry and marketplace for discoverable agents | A platform-specific listing or registered agent that points to GitHub issues | Almanac registration and platform account rules; exact DNS identity and permissions need audit | Registry visibility depends on Fetch.ai services and terms; export/restore must be checked | Platform conditions and any monetization are not assumed | Read-only listing feasibility and metadata export audit |
| OpenServ | Agent service market for pay-per-use services | A service listing only if DNS later offers an explicitly bounded service | Platform account/payment/auth rules require review | Market and payment workflow may create provider dependence | The platform describes pay-per-use services; DNS should not accept payment in the first pilot | Static service specification without account creation or payment |
| ANP | Open protocol stack for agent description, discovery, identity and communication | An ANP description/discovery document and endpoint after schema verification | DID and protocol-specific identity/security need implementation audit | Open specifications may reduce lock-in; deployed identity and relay choices remain dependencies | No payment in the proposed discovery pilot | Read the discovery/description specs and validate a protocol-neutral mapping |
| Agent social network | Discussion and informal discovery | One carefully targeted research packet linking an issue | Platform account and moderation rules | High platform and audience dependence; weak evidence portability | No project payment | One manually reviewed post, only after authenticated access |

## Decision

A2A is the best first protocol study because its official specification directly
defines an Agent Card and a well-known discovery URI. This does not mean DNS is
ready to expose an A2A endpoint. Agentverse is the best first platform-specific
registry study because its documentation explicitly describes search/discovery
and multiple deployment modes. ANP is a useful decentralization-oriented
comparison, while OpenServ is deferred until a real paid service exists.

The first implementation remains a protocol-neutral card and a static validator.
Choose one adapter only after the validator and a threat-model review. Do not
publish the draft card under an A2A URI: the draft omits required protocol
interfaces, security declarations and an executable service endpoint.

## Sources Checked

- [A2A specification](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)
  and [A2A discovery guide](https://github.com/a2aproject/A2A/blob/main/docs/topics/agent-discovery.md): current specification text identifies Agent Cards, supported interfaces and discovery mechanisms.
- [Agentverse Marketplace documentation](https://docs.agentverse.ai/v-2/documentation/getting-started/agentverse-marketplace): official description of marketplace search, Almanac integration and deployment types.
- [OpenServ platform](https://platform.openserv.ai/): official landing page describes the x402 Agent Market and pay-per-use services.
- [Agent Network Protocol](https://agentnetworkprotocol.com/en/): official site describes agent description, discovery, identity and communication specifications.

The sources establish what the projects describe themselves as providing. They
do not establish adoption, reliability, neutrality, security, cost to DNS or
independent value for research contribution. Those are future audit questions.
