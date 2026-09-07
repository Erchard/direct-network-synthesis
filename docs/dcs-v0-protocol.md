# DCS-V0: exact finite verification protocol

Recorded before suite evaluation, 2026-09-07. This is the V0 software-verification
gate in [the plan](dcs-edcs-experiment-plan-uk.md), not C1, EDCS or an ML benchmark.
No train/validation/test quality claim. Every finite input is supplied as an
open specification. No datasets or model selection are accessed.

## Fixed design

- Config `configs/dcs_v0.json`: XOR, half-adder, full-adder, majority-3,
  two-data-input MUX, in that order. Binary little-endian inputs; MUX first bit
  is selector. Half/full-adder outputs are sum then carry.
- Teacher fixture: minterm threshold detectors followed by OR, duplicated twice.
  Detector for pattern p is equivalent to requiring every literal of p; the
  implementation expands that fixed identity directly into AND/inverter logic.
  This is deliberately constructed from a complete table, not a trained teacher,
  not a general numeric-neuron compiler, and not compression evidence for LLMs.
- Compare literal expansion, literal + standard ABC, bounded exact AIG synthesis,
  exact synthesis + the same ABC. No task name reaches the synthesizer; it receives
  only input count and output bit table. No hand macro library.
- All fixtures have at most three boundary inputs, so exact synthesis is a
  whole-fixture resynthesis, a degenerate local-region case. This does not
  implement graph decomposition or prove useful local repairs in larger graphs.
- AIG node 0=false; literal 2*i names node i, low bit inverts it. AND nodes may
  reference only previous nodes. Outputs may be constants or inverted nodes.
- Z3 enumerates AND count 0 through 12; 5 seconds per solver check, seed 93007,
  one thread. It stops on the first SAT or UNKNOWN. Minimum-node evidence requires
  UNSAT for all smaller counts. UNKNOWN and size exhaustion remain in the record.
  Ties within a size use the fixed solver, not a claim of minimum depth or canonical
  globally optimal serialization. The full configuration is frozen before execution.
- Both ABC arms use `read_verilog; hierarchy; proc; flatten; techmap; opt;
  abc -g AND; clean; write_json`. Actual full command and JSON netlist are retained.
  The independent importer accepts only AND/NOT cells and fails on unsupported logic.

## Gates and resource policy

Every available output circuit must exactly match all specification rows under
an independent Python interpreter. Flipping the first output bit must be detected.
Unit tests also cover serialization, constants, invalid cycles, unsupported cells
and synthesis failure. Equivalence failure blocks all subsequent model experiments.
Failure to improve over ABC is retained; large reduction versus the deliberately
redundant literal fixture is not sufficient evidence for a new method.

Fresh worker per fixture; 60 seconds per ABC subprocess; 600 seconds total suite;
4 GiB sampled RSS over worker and descendants; preserve failed/not-run fixtures.
The initial WASM compilation cache is warmed by the version check before the suite.
Source hashes, commit, exact command, solver/package versions, all attempted sizes,
raw netlists and tool logs are recorded. No fixture or seed replacement after results.
Report per-fixture nodes, inverted edges, logical AND depth, serialized bytes,
solver-attempt times, ABC wall time and sampled peak RSS. Inverter-edge depth is
not physical delay. Serializing AIG data is not a physical area measurement.

The models are checked on complete finite domains, not five statistical splits.
This is permitted only as a verification suite, not as reportable predictive
evidence under methodology. The planned five-split C1/L1 gates remain separate.

Command: `.venv\Scripts\python.exe -m experiments.run_dcs_v0`.
Dependencies: project optional `circuits` extra plus existing dev dependencies.
No FPGA, energy, novelty, generalization, single-pass or gradient-replacement claim.
