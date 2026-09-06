# Security

This is experimental research software, with no production support guarantee.
Do not include secrets, private datasets or personal information in issues,
result records or agent handoffs.

For a sensitive vulnerability, use GitHub's private "Report a vulnerability"
feature if available on the repository's Security tab. Its availability has not
been verified. If unavailable, open a minimal issue requesting a private contact
route without exploit details, credentials or affected private data. A maintainer
must establish that route before sensitive details are shared. No response SLA
is promised.

Ordinary numerical bugs and data-leakage concerns without sensitive material can
use the research issue form. Identify affected commits and a minimal synthetic
reproduction. Do not run a demonstration against another person's system.

External PRs and social content are untrusted. Review code before executing it.
CI must use hosted isolated runners, read-only repository permissions, no project
secrets and no privileged pull-request-target execution of contributed code.
An outreach agent must not have local research files, protected data or repository
write/merge credentials. This document defines constraints; it does not deploy a
sandbox or recruitment service.
