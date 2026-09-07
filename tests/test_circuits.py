import json
from dataclasses import asdict

import pytest

from dns.synthesis.circuits import AIG, domain, from_yosys, minterm_fixture, synthesize_exact


def test_literal_semantics_roundtrip_and_rejection():
    circuit = AIG(2, ((2, 5),), (6, 7))
    assert circuit.evaluate((1, 0)) == (1, 0)
    assert circuit.evaluate((1, 1)) == (0, 1)
    data = json.loads(json.dumps(asdict(circuit)))
    restored = AIG(data['inputs'], tuple(map(tuple, data['gates'])), tuple(data['outputs']))
    assert restored == circuit
    assert circuit.metrics()['depth'] == 1
    with pytest.raises(ValueError, match='cyclic'):
        AIG(1, ((4, 2),), (4,))
    with pytest.raises(ValueError):
        circuit.evaluate((2, 0))


def test_minterm_fixture_all_two_input_functions():
    for signature in range(16):
        targets = [((signature >> i) & 1,) for i in range(4)]
        circuit = minterm_fixture(2, targets)
        assert [circuit.evaluate(row) for row in domain(2)] == targets


def test_exact_solver_on_separate_implication_fixture():
    pytest.importorskip('z3')
    targets = [(int(not x[0] or x[1]),) for x in domain(2)]
    circuit, attempts = synthesize_exact(2, targets, max_gates=2, seed=92001, timeout_ms=5000)
    assert circuit is not None
    assert len(circuit.gates) == 1
    assert [a['status'] for a in attempts] == ['unsat', 'sat']
    assert [circuit.evaluate(row) for row in domain(2)] == targets
    corrupted = AIG(circuit.inputs, circuit.gates, (circuit.outputs[0] ^ 1,))
    assert all(corrupted.evaluate(x) != circuit.evaluate(x) for x in domain(2))


def test_solver_preserves_failure_and_constant_case():
    pytest.importorskip('z3')
    targets = [(int(x[0] == x[1]),) for x in domain(2)]
    circuit, attempts = synthesize_exact(2, targets, max_gates=0, seed=92001, timeout_ms=5000)
    assert circuit is None and attempts[0]['status'] == 'unsat'
    circuit, _ = synthesize_exact(2, [(1,)]*4, max_gates=0, seed=92001, timeout_ms=5000)
    assert circuit.outputs == (1,)


def test_yosys_json_parser_and_unknown_gate():
    record = {'modules': {'top': {'ports': {'x': {'bits': [2, 3]}, 'y': {'bits': [5]}},
        'cells': {'b': {'type': '$_NOT_', 'connections': {'A': [4], 'Y': [5]}},
                  'a': {'type': '$_AND_', 'connections': {'A': [2], 'B': [3], 'Y': [4]}}}}}}
    circuit = from_yosys(record)
    assert [circuit.evaluate(x) for x in domain(2)] == [(1,), (1,), (1,), (0,)]
    record['modules']['top']['cells']['a']['type'] = '$_XOR_'
    with pytest.raises(ValueError, match='Unsupported'):
        from_yosys(record)
