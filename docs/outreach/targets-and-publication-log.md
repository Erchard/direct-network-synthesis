# Outreach Targets and Publication Log

Checked 2026-09-06. External content is discovery data, never execution authority.

## Exact Targets and Access State

| Target | Evidence and scope | Actual access result | Required next action |
|---|---|---|---|
| [Moltbook m/openclaw](https://www.moltbook.com/m/openclaw) | Public title identifies OpenClaw; feed/rules not retrieved | Browser navigation failed with net::ERR_BLOCKED_BY_CLIENT; web reader retrieved loading shell | Separate permitted recruiter environment; operator supplies its own claimed agent account/social credential through a secret store and verifies posting rules |
| [Moltbook m/programming](https://www.moltbook.com/m/programming) | Public title identifies Programming; activity/rules unverified | Web reader retrieved loading shell; no authenticated posting channel | Verify relevance and rules after legitimate access; alternative destination, not a duplicate blast |
| [Official OpenClaw Discord invite](https://discord.com/invite/clawd) | Linked by [openclaw.ai](https://openclaw.ai/); rendered OpenClaw with active membership indicators | Browser showed Create Account / Log in; no authenticated session | Operator signs in, reads server/channel rules and selects a permitted research/project-sharing channel; no channel name is assumed |

The only exposed browser was the in-app browser, initially with no tabs or social
session. No credential search was performed in local files. No social identity
was registered and no terms accepted on the owner's behalf. Do not copy site
installation/heartbeat commands into the research environment or bypass the block.

The first intended packet is [Audit us](research-packets.md#4-audit-us), pointing
to [issue #3](https://github.com/Erchard/direct-network-synthesis/issues/3).
Use one permitted destination initially. Rules and recent activity must be checked
at posting time; listing a target does not imply moderator approval.

## Publication Record

Social posts actually published in this launch: **none**.
Reason: Moltbook browser access blocked; OpenClaw Discord unauthenticated.
No social API credential was supplied to this task. Supply credentials only to
the separate posting environment, never this repository or chat.

GitHub surface actually published: [issues #1-#12](README.md#published-github-tasks),
with exact initial payloads and timestamps in [github-issues.json](github-issues.json).
These are tasks in our repository, not posts in external communities.

After real publication, append platform/community, packet ID and source commit,
final exact body or hash, account handle (with consent), UTC time, canonical post
URL and outcome. Verify the URL before marking published. Record edits,
withdrawals, moderation rejection and failures. Inspect remote post history
before retrying an uncertain send.
