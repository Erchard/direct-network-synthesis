# CS-A0: bounded backend audit

2026-09-07. Scope: readiness for DCS-V0 verification fixtures, not novelty review
completion or readiness for C1/L1 learning benchmarks.

| Source inspected | Established capability | Consequence for this project |
|---|---|---|
| [ABC README](https://github.com/berkeley-abc/abc) and installed Yosys `help abc` | AIG rewriting and technology mapping | Standard ABC optimization is a required baseline; use the same AND/NOT library |
| [LogicNets abstract](https://arxiv.org/abs/2004.03021) | Quantized neuron truth-table compilation with fan-in limitations | A small finite conversion is not a new idea; do not extrapolate beyond bounded inputs |
| [Program sketching abstract](https://link.springer.com/article/10.1007/s10009-012-0249-7) | Example-based synthesis with counterexample verification | Generic error-driven synthesis already has precedent; EDCS must establish incremental benefit |
| Exact synthesis paper's indexed abstract from the preceding plan audit | SAT-based circuit synthesis, unpredictable runtime | Bound calls; UNKNOWN is not UNSAT; a full-text encoding comparison remains pending |
| [Z3 repository](https://github.com/Z3Prover/z3), installed Python binding | Open-source SMT backend | Use Z3 rather than a custom solver; record seed and per-size statuses |
| [YoWASP packaging README](https://github.com/YoWASP/yosys), local CLI help | WebAssembly Yosys package and structured JSON export | Windows-compatible adapter; wrapper performance is not native ASIC/FPGA performance |

The original YoWASP repository page is archived; reproducibility here relies on
the exact installed PyPI distribution, not a claim about its current maintenance.
The exact-synthesis full-text PDF remained unavailable in this audit. No claim
is made to implement that paper's optimized encoding or to have surveyed ECO,
automated program repair and incremental synthesis exhaustively. That review
remains mandatory before interpreting EDCS-L1 as a contribution.

Installed in the project virtualenv: yowasp-yosys 0.68.0.0.post1208, Z3 5.1.0.0.
Yosys reports git 38e001a6f. Packaging dependencies: yowasp-runtime 1.96,
wasmtime 47.0.1. `-V` and `help abc; help write_json` succeeded. First WASM
preparation is setup overhead, not a compiler speed result. ABC is invoked
through Yosys `abc -g AND`; NOT is included by that command.

Licensing anchors: [YoWASP/Yosys ISC](https://github.com/YoWASP/yosys/blob/develop/LICENSE.txt),
[Z3 MIT](https://github.com/Z3Prover/z3/blob/master/LICENSE.txt),
[ABC copyright](https://github.com/berkeley-abc/abc/blob/master/copyright.txt).
Third-party packages retain their licenses; project licensing does not relicense
them. The V0 record contains generated fixture artifacts and tool logs.

Decision: backend checks permit the bounded V0 suite after unit tests and a
committed protocol. C1 remains queued; no learned teacher or general Repair
operator is implemented by this milestone.
