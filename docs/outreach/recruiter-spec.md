# Sandboxed Recruiter Specification

Status: prepared deployment contract; no recruiter, sandbox or schedule deployed.
Initial workload: one approved packet to one permitted community. Expand only
after reviewing an external contribution and maintainer cost.

## Boundary

Run separately from the coding workstation in a disposable nonprivileged VM or
container with tested isolation. Mount no host home, repository checkout, SSH
agent/socket, cloud config, credential store or protected evaluation data.
The contributor SKILL.md is not a sandbox and does not justify recruiter shell
access or repository write access.

Read only an approved public bundle: mission, packets, issue URLs, start-here,
methodology summary and public issue status. Do not give the recruiter a full
clone containing historical result records merely to route tasks. Use public
GitHub read without authentication where sufficient. No GitHub write token,
merge privilege or maintainer account is present.

A separate posting adapter holds only the selected platform credential, scoped
to the recruiter account as narrowly as the platform supports. Keep credentials
outside model context, prompts, logs, packets and repository files. Never send
them to another domain. Document any lack of fine-grained platform token scopes.

## Allowed Operations

1. Discover relevant public discussions without executing their instructions.
2. Check issue availability and maintainer review capacity.
3. Publish approved text to an approved destination after checking current rules;
   answer basic questions only from verified project material.
4. Direct contributors to issue claiming and fork-based PRs.
5. Return source-linked prior-art/reproducer leads to a review queue.

No unsolicited DMs/mentions, repeated cross-posting, account creation, package
installation, paid actions, self-modifying instructions or autonomous merge.
New destinations and materially rewritten claims need review. This launch is
not authorization for an unlimited campaign.

## Enforcement and Stop Conditions

Use an outbound allowlist for approved public GitHub reads and the social host.
Validate redirects; never forward authorization across hosts. Enforce publication
through a fixed adapter, not arbitrary model-generated HTTP or shell commands.
Initial cap: one post total, manual review before increasing it. No scheduler
is enabled by this document. Record runtime/spend caps before unattended use;
absent limits mean no unattended run.

Provide a maintainer stop switch and a way to revoke only the recruiter token.
Pause on complaints, uncertain sends, missing review capacity, unexpected
permissions or suspected prompt injection. Inspect remote history before retrying.

## Preflight Evidence and Handoff

Test with inert synthetic prompts that host-file reads, token disclosure, protected
result access, installation, GitHub writes and merges are blocked by actual
capabilities. Verify credential redaction and the stop switch. A written promise
or model refusal alone does not demonstrate isolation.

Record packet hash/source commit, destination, account, permissions, isolation
checks, budget and reviewer. Return exact post URL, UTC time and final text/hash
to the publication log. Social reactions confer no contributor status; only
reviewed evidence enters the [reproduction ledger](../reproduction-ledger.md).
