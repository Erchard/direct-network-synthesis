"""DCS-V0 full-specification verification fixtures, never a learning benchmark."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from dns.synthesis.circuits import AIG, domain, minterm_fixture, optimize_abc, synthesize_exact


def fixture(name):
    if name in ('xor', 'half_adder'):
        rows = domain(2)
        targets = [(a ^ b,) if name == 'xor' else (a ^ b, a & b) for a, b in rows]
        return 2, targets
    rows = domain(3)
    if name == 'full_adder':
        return 3, [(sum(x) % 2, int(sum(x) >= 2)) for x in rows]
    if name == 'majority3':
        return 3, [(int(sum(x) >= 2),) for x in rows]
    if name == 'mux2':
        return 3, [(x[2] if x[0] else x[1],) for x in rows]
    raise ValueError(name)


def run_fixture(name, cfg, backend):
    inputs, targets = fixture(name)
    teacher = minterm_fixture(inputs, targets, cfg['duplicate_copies'])
    rows = domain(inputs)
    if [teacher.evaluate(x) for x in rows] != targets:
        raise RuntimeError('Teacher fixture is incorrect')
    standard, abc = optimize_abc(teacher, backend, timeout_seconds=cfg['backend_timeout_seconds'])
    exact, attempts = synthesize_exact(inputs, targets, max_gates=cfg['max_and_nodes'],
        seed=cfg['solver_seed'], timeout_ms=cfg['solver_timeout_ms'])
    models = {'literal': teacher, 'abc': standard}
    logs = {'abc': abc}
    if exact is not None:
        models['exact'] = exact
        models['exact_abc'], logs['exact_abc'] = optimize_abc(
            exact, backend, timeout_seconds=cfg['backend_timeout_seconds'])
    results = {}
    for label, circuit in models.items():
        outputs = [circuit.evaluate(x) for x in rows]
        corrupted = AIG(inputs, circuit.gates, (circuit.outputs[0] ^ 1, *circuit.outputs[1:]))
        results[label] = {'circuit': asdict(circuit), 'metrics': circuit.metrics(),
                         'equivalence_pass': outputs == targets,
                         'mutation_detected': any(corrupted.evaluate(x) != y
                             for x, y in zip(rows, targets, strict=True))}
    return {'fixture': name, 'inputs': rows, 'targets': targets, 'models': results,
            'solver_attempts': attempts, 'solver_completed': exact is not None,
            'backend_logs': logs, 'test_status': 'not_applicable_verification_fixture'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('results/dcs_v0.json'))
    parser.add_argument('--worker')
    args = parser.parse_args()
    cfg = json.loads(Path('configs/dcs_v0.json').read_text())
    backend = Path(sys.executable).parent / ('yowasp-yosys.exe' if os.name == 'nt' else 'yowasp-yosys')
    if args.worker:
        print(json.dumps(run_fixture(args.worker, cfg, backend)))
        return
    import psutil
    versions = {p: importlib.metadata.version(p) for p in
                ('yowasp-yosys', 'yowasp-runtime', 'wasmtime', 'z3-solver', 'psutil')}
    record = {'config': cfg, 'versions': versions, 'python': sys.version,
        'platform': platform.platform(), 'cpu': platform.processor(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'source_sha256': {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in
            ['src/dns/synthesis/circuits.py', 'experiments/run_dcs_v0.py', 'configs/dcs_v0.json']},
        'command': subprocess.list2cmdline([sys.executable, *sys.argv]),
        'backend_version': subprocess.check_output([str(backend), '-V'], text=True, timeout=60),
        'rows': [], 'status': 'running', 'evidence_type': 'full_specification_verification'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    start_suite = time.monotonic()
    for name in cfg['fixtures']:
        if time.monotonic() - start_suite >= cfg['suite_timeout_seconds']:
            row = {'fixture': name, 'error': 'suite_budget_not_run'}
        else:
            import tempfile
            with tempfile.TemporaryFile(mode='w+t') as out, tempfile.TemporaryFile(mode='w+t') as err:
                env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
                process = subprocess.Popen([sys.executable, '-m', 'experiments.run_dcs_v0',
                    '--worker', name], stdout=out, stderr=err, env=env)
                peak, error = 0, None
                start = time.monotonic()
                while process.poll() is None:
                    try:
                        root = psutil.Process(process.pid)
                        rss = sum(p.memory_info().rss for p in [root, *root.children(recursive=True)]
                                  if p.is_running())
                        peak = max(peak, rss)
                        if rss > cfg['memory_limit_bytes'] or time.monotonic()-start_suite > cfg['suite_timeout_seconds']:
                            error = 'memory_or_suite_timeout'
                            for child in root.children(recursive=True):
                                child.kill()
                            root.kill()
                    except psutil.NoSuchProcess:
                        pass
                    time.sleep(0.05)
                process.wait()
                out.seek(0)
                err.seek(0)
                try:
                    if error or process.returncode:
                        raise RuntimeError(error or err.read())
                    row = json.load(out)
                except (ValueError, RuntimeError) as exc:
                    row = {'fixture': name, 'error': str(exc)}
                row.update(worker_seconds=time.monotonic()-start, sampled_process_tree_peak_bytes=peak)
        record['rows'].append(row)
        args.output.write_text(json.dumps(record, indent=2), encoding='utf-8')
        print(name, {k: v['metrics']['and_nodes'] for k, v in row.get('models', {}).items()},
              row.get('error', ''), flush=True)
    record['status'] = 'complete' if all('error' not in r and r['solver_completed'] and
        all(m['equivalence_pass'] and m['mutation_detected'] for m in r['models'].values())
        for r in record['rows']) else 'incomplete_or_failed'
    args.output.write_text(json.dumps(record, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
