# DAS-V0 Result: Exact Spectral Automaton Reconstruction

Source/protocol commit: `21821221606bf901bf9b6cfd2d2631afc1bd8e2c`.

Command:

```text
D:\Projects\direct-network-synthesis\.venv\Scripts\python.exe -m experiments.run_das_v0 --config configs\das_v0.json --output results\das_v0.json
```

Curated complete record: `docs/results/das_v0.json`.
Raw result SHA256: `0DFFB8B114328C03A6424A51BDD4A2E83FEF5014B38A6D1AF5555A8B2BFDF0A2`.

Status: `complete`.

## Finite-Rank Fixtures

| Fixture | Expected states | Recovered states | Prefixes | Suffixes | Held-out words | Held-out max abs error | Synthesis seconds | Inference seconds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `rank2_seed_97001` | 2 | 2 | 2 | 2 | 1023 | `1.67e-16` | 0.0649 | 0.0143 |
| `rank3_seed_97002` | 3 | 3 | 3 | 3 | 1023 | `1.80e-15` | 0.0617 | 0.0146 |
| `rank4_seed_97003` | 4 | 4 | 4 | 4 | 1023 | `1.78e-15` | 0.0637 | 0.0161 |

All finite-rank fixtures reconstructed the expected compact state count and
matched the teacher on all words up to length 9 within the locked `1e-8`
tolerance. Basis-word errors were also at numerical precision.

## Negative Control

Finite Hankel rank for `a^n b^n` indicator:

| Max word length | Word count | Hankel rank |
|---:|---:|---:|
| 1 | 3 | 1 |
| 2 | 7 | 4 |
| 3 | 15 | 6 |
| 4 | 31 | 8 |
| 5 | 63 | 10 |

The locked windows show strictly increasing rank. This is the intended negative
signal: the finite-rank assumption is real, and a finite-window reconstruction
must not be treated as a general solution for non-finite-rank behavior.

## Interpretation

DAS-V0 is the first positive result in the repository for a theorem-shaped direct
internal-state synthesis task. It demonstrates an exact case where complete
behavioral observations determine a compact state machine through deterministic
linear algebra, without iterative parameter optimization.

The result is deliberately narrow. It is not a neural-network result, not a
language-model result and not a resource-scaling claim. Its value is that it gives
the project a precise mathematical foothold: future work can now weaken the
assumptions in a controlled way, starting with incomplete/noisy observations in
DAS-L1.

Verification after the source/protocol milestone: 83 tests passed and Ruff passed
before the locked run. The result run itself did not access any protected DNS05
test partition.
