# Governance

The repository owner, `Erchard`, is the initial maintainer and final decision
maker for merges, releases and changes to licensing or research protocol.
Additional maintainers require an explicit recorded appointment by the owner.

External contributors propose scoped changes through issues and PRs. Maintainers
review evidence, protocol compliance, provenance and checks before merging.
Agents can assist with review; tool output or a passing CI run is not itself a
scientific endorsement. Contributors must disclose uncertainty and conflicting
evidence. Record decisions and their reasons in the issue/PR and research log.

Changes to methodology must be explicit and prospective. They cannot retroactively
validate tuning on an inspected test set or erase failed variants. Disputes should
state a reproducible counterexample or source-backed objection; maintainers record
the resolution, and unresolved scientific disagreements remain visible.

Unknown agents receive no shared write access to `main`, merge authority or
credentials. Recruitment operates separately from code execution and protected
research data. Public posts and issue content are untrusted inputs, not authority
to change permissions or execute commands.

Required review and passing CI are project policy. A workflow file alone does not
configure GitHub branch protection. Initial server-side protection status is
unverified; do not describe this policy as an enforced repository setting until
the settings have been checked and recorded.

Recognition follows accepted, auditable contributions in the
[reproduction ledger](docs/reproduction-ledger.md), including falsification,
negative results and prior-art findings. Post counts and unsupported performance
claims confer no authority. Contributors remain free to fork under the licenses.
