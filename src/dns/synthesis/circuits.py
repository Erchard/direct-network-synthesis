"""Small finite AIG fixtures and bounded synthesis; not a learned DNS model."""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AIG:
    """Literal 2*i is node i, xor 1 inverts it; node zero is false."""

    inputs: int
    gates: tuple[tuple[int, int], ...]
    outputs: tuple[int, ...]

    def __post_init__(self):
        if self.inputs < 1 or not self.outputs:
            raise ValueError("Positive input and output counts required.")
        for index, pair in enumerate(self.gates):
            if len(pair) != 2 or any(v < 0 or v // 2 > self.inputs + index for v in pair):
                raise ValueError("Invalid or cyclic gate literal.")
        if any(v < 0 or v // 2 > self.inputs + len(self.gates) for v in self.outputs):
            raise ValueError("Invalid output literal.")

    def evaluate(self, row):
        if len(row) != self.inputs or any(v not in (0, 1) for v in row):
            raise ValueError("Expected one bit per input.")
        values = [0, *row]
        for a, b in self.gates:
            values.append((values[a // 2] ^ (a & 1)) & (values[b // 2] ^ (b & 1)))
        return tuple(values[v // 2] ^ (v & 1) for v in self.outputs)

    def metrics(self):
        depths = [0] * (self.inputs + 1)
        for a, b in self.gates:
            depths.append(1 + max(depths[a // 2], depths[b // 2]))
        return {
            "and_nodes": len(self.gates),
            "depth": max(depths[v // 2] for v in self.outputs),
            "inverted_edges": sum(v & 1 for pair in self.gates for v in pair)
            + sum(v & 1 for v in self.outputs),
            "serialized_bytes": len(json.dumps(asdict(self), separators=(",", ":")).encode()),
        }

    def verilog(self):
        def lit(v):
            return ("~" if v & 1 else "") + ("1'b0" if v // 2 == 0 else f"n{v // 2}")
        lines = [(f"module top(input [{self.inputs-1}:0] x, "
                  f"output [{len(self.outputs)-1}:0] y);")]
        lines.extend(f"wire n{i+1} = x[{i}];" for i in range(self.inputs))
        lines.extend(f"wire n{self.inputs+i+1} = {lit(a)} & {lit(b)};"
                     for i, (a, b) in enumerate(self.gates))
        lines.extend(f"assign y[{i}] = {lit(v)};" for i, v in enumerate(self.outputs))
        return "\n".join([*lines, "endmodule"])


def domain(inputs):
    if not 1 <= inputs <= 8:
        raise ValueError("Fixture enumeration is restricted to 1..8 bits.")
    return [tuple((i >> bit) & 1 for bit in range(inputs)) for i in range(2**inputs)]


def minterm_fixture(inputs, targets, copies=2):
    """Expand minterm threshold detectors and OR readouts without simplification."""
    rows = domain(inputs)
    if len(targets) != len(rows) or copies < 1:
        raise ValueError("Complete truth table and positive copies required.")
    width = len(targets[0])
    if width < 1 or any(len(t) != width or any(v not in (0, 1) for v in t) for t in targets):
        raise ValueError("Targets must be equally wide bit vectors.")
    gates = []

    def conjunction(a, b):
        gates.append((a, b))
        return 2 * (inputs + len(gates))

    outputs = []
    for column in range(width):
        output = 0
        for row, target in zip(rows, targets, strict=True):
            if target[column]:
                for _ in range(copies):
                    term = 1
                    for bit, value in enumerate(row):
                        term = conjunction(term, 2 * (bit + 1) ^ (1 - value))
                    output = conjunction(output ^ 1, term ^ 1) ^ 1
        outputs.append(output)
    return AIG(inputs, tuple(gates), tuple(outputs))


def synthesize_exact(inputs, targets, *, max_gates, seed, timeout_ms):
    """Find minimum AND count in a bounded AIG language using Z3, not gradients.

    UNSAT at every smaller size is necessary for a minimality claim. UNKNOWN
    stops the search. This consumes the complete specification, not a holdout.
    """
    import z3

    minterm_fixture(inputs, targets, copies=1)  # Validate the complete bit contract.
    if max_gates < 0 or timeout_ms <= 0 or seed < 0:
        raise ValueError("Invalid synthesis budget or seed.")
    rows = domain(inputs)
    bits = len(rows)
    signatures = [0] + [sum(row[j] << i for i, row in enumerate(rows))
                        for j in range(inputs)]
    expected = [sum(row[j] << i for i, row in enumerate(targets))
                for j in range(len(targets[0]))]
    attempts = []
    for count in range(max_gates + 1):
        start = time.perf_counter()
        solver = z3.Solver()
        solver.set(timeout=timeout_ms, random_seed=seed, threads=1)
        values = [z3.BitVecVal(s, bits) for s in signatures]

        def select(name, choices, solver=solver):
            index = z3.Int(name)
            solver.add(index >= 0, index < 2 * len(choices))
            literals = [v for choice in choices for v in (choice, ~choice)]
            result = literals[-1]
            for i in reversed(range(len(literals) - 1)):
                result = z3.If(index == i, literals[i], result)
            return index, result

        selectors = []
        for gate in range(count):
            a, av = select(f"a{gate}", values)
            b, bv = select(f"b{gate}", values)
            solver.add(a <= b)
            value = z3.BitVec(f"v{gate}", bits)
            solver.add(value == av & bv)
            values.append(value)
            selectors.append((a, b))
        outputs = []
        for column, target in enumerate(expected):
            index, value = select(f"o{column}", values)
            solver.add(value == z3.BitVecVal(target, bits))
            outputs.append(index)
        status = solver.check()
        attempts.append({"gates": count, "status": str(status),
                         "seconds": time.perf_counter() - start,
                         "reason": solver.reason_unknown() if status == z3.unknown else None})
        if status == z3.sat:
            model = solver.model()
            circuit = AIG(inputs, tuple((model[a].as_long(), model[b].as_long())
                                        for a, b in selectors),
                          tuple(model[o].as_long() for o in outputs))
            if [circuit.evaluate(row) for row in rows] != [tuple(t) for t in targets]:
                raise RuntimeError("Independent evaluator rejected synthesis.")
            return circuit, attempts
        if status == z3.unknown:
            return None, attempts
    return None, attempts


def from_yosys(record):
    """Read the restricted AND/NOT JSON output; reject all unknown gate types."""
    module = record["modules"]["top"]
    ports = module["ports"]
    inputs = len(ports["x"]["bits"])
    literals = {"0": 0, "1": 1}
    literals.update({wire: 2*(i+1) for i, wire in enumerate(ports["x"]["bits"])})
    pending = list(module["cells"].values())
    gates = []
    while pending:
        remaining = []
        for cell in pending:
            kind, connections = cell["type"], cell["connections"]
            if kind not in ("$_AND_", "$_NOT_"):
                raise ValueError(f"Unsupported mapped cell: {kind}")
            names = ("A", "B") if kind == "$_AND_" else ("A",)
            if any(len(connections[name]) != 1 for name in (*names, "Y")):
                raise ValueError("Expected one-bit ports.")
            if any(connections[name][0] not in literals for name in names):
                remaining.append(cell)
                continue
            a = literals[connections["A"][0]]
            if kind == "$_NOT_":
                value = a ^ 1
            else:
                gates.append((a, literals[connections["B"][0]]))
                value = 2*(inputs+len(gates))
            output = connections["Y"][0]
            if output in literals:
                raise ValueError("Multiple drivers.")
            literals[output] = value
        if len(remaining) == len(pending):
            raise ValueError("Undriven or cyclic netlist.")
        pending = remaining
    return AIG(inputs, tuple(gates), tuple(literals[w] for w in ports["y"]["bits"]))


def optimize_abc(circuit, executable, *, timeout_seconds=60):
    script = ("read_verilog input.v; hierarchy -top top; proc; flatten; "
              "techmap; opt; abc -g AND; clean; write_json mapped.json")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "input.v").write_text(circuit.verilog(), encoding="ascii")
        start = time.perf_counter()
        result = subprocess.run([str(executable), "-Q", "-T", "-p", script], cwd=root,
                                capture_output=True, text=True, timeout=timeout_seconds, check=False)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        record = json.loads((root / "mapped.json").read_text())
        mapped = from_yosys(record)
    return mapped, {"seconds": time.perf_counter()-start, "script": script,
                    "stdout": result.stdout, "stderr": result.stderr,
                    "netlist": record}
