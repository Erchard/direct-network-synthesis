# DCS-V0: exactness passed, no added node-count benefit

2026-09-07. Source `2e642ac8164e7942414a4108c65b7a662b10c626`.
Command `.venv\Scripts\python.exe -m experiments.run_dcs_v0`.
[Locked protocol](dcs-v0-protocol.md), [full record](results/dcs_v0.json).
SHA256 of full record: `1ce7518d3e3e0a0629aae4840f391e34721e081d0d1f22042d809ef919b8fe62`.

| Fixture | Literal AND nodes | ABC AND nodes | Exact AND nodes | Exact + ABC | Total exact-search seconds |
|---|---:|---:|---:|---:|---:|
| XOR | 12 | 3 | 3 | 3 | 0.065295 |
| Half-adder | 18 | 3 | 3 | 3 | 0.094595 |
| Full-adder | 64 | 7 | unavailable | unavailable | 6.592110 |
| Majority-3 | 32 | 4 | 4 | 4 | 0.372481 |
| MUX-2 | 32 | 3 | 3 | 3 | 0.101933 |

All 18 produced circuits match every supplied input exactly, and all 18 output
mutations are detected. ABC depth is respectively 2, 2, 4, 3, 2 AND levels.
All completed exact arms have the same node count and depth as ABC. Per-circuit
edge counts, bytes, netlists and every solver attempt remain in the record.

Full-adder exact search reports UNSAT at sizes 0..5, then UNKNOWN due to timeout
at size 6. It did not attempt size 7, as prescribed. Thus this run leaves the
minimum in [6, 7], using ABC's independently evaluated 7-node upper bound. It
does not establish that six nodes are impossible. The record deliberately retains
`incomplete_or_failed`: four exact searches complete, one unresolved, no false
equivalence. No extra seed, larger timeout or substitute fixture was used.

## Interpretation

1. The finite conversion/verifier/backend path works on these fixtures.
2. Standard logic optimization already removes their deliberately introduced
   redundancy. Added exact search offers zero node/depth improvement on all four
   completed pairs; compression against literal expansion alone would exaggerate
   the contribution. The fifth pair remains missing, not a zero difference.
3. Finding a small witness and proving a smaller one impossible are different
   tasks. Here ABC finds a 7-node full-adder, while the simple exact encoding spends
   its check budget on size 6. This suggests testing cost-bounded improvement
   against a known circuit rather than requiring global minimality. It is an
   engineering hypothesis from a tiny diagnostic, not a complexity theorem.

ABC wall times (0.80..1.10 seconds) include the WASM subprocess and parsing;
exact-search times include Python encoding and Z3 checks. They do not establish
an intrinsic solver speed ranking. Each fixture has one run, not five independent
splits; these are verification outcomes, not predictive-performance statistics.
The recorded process-tree sampled peaks are below 180 MiB. No energy measured.

The fixtures were constructed from complete tables; no trained teacher,
generalization, local repair, knowledge acquisition or cheap AI training has
been demonstrated. No C1/L1 test boundaries were opened.

## Decision

Close this V0 run with exactness checked and the solver timeout preserved. Do not
increase its budget until it produces a favorable answer. Do not promote the
current full-table exact method as a better compiler than ABC. Keep C1/L1 queued.
The next bounded action is to specify a cost-bounded, known-upper-bound regional
replacement control and its relevant prior art before any model experiment.
It must address whether useful improvement exists beyond ABC, not merely repeat
these truth tables. EDCS still needs a genuine incremental Repair and equal-data
comparison; relabeling full resynthesis would not satisfy its hypothesis.

Checks before evaluation: Ruff passed; 79 tests passed. Artifact post-check:
five rows, all available circuits equivalent, all negative mutations detected,
one explicit solver timeout. Full source/config hashes and versions are included.
