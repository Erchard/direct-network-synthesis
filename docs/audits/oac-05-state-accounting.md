# OAC-05: DNS05 Deployed-State and Retained-Sample Accounting

Status: local owner audit; static accounting only, not measured peak RAM and
not an independent reproduction.

## Scope

This audit derives stored-array formulas from
`experiments/run_dns05_failure_scaling.py` and compares them with the published
artifact schema. No historical experiment runner was executed and no benchmark
partition was evaluated.

Let `d` be input width, `n` train rows, `v` validation rows, `m` center count,
`r` requested spectral rank, `b` realized feature budget and `c` class count.
All arrays in the runner are NumPy `float64` unless stated otherwise.

## Inference-state accounting

| Representation | Retained data and derived state | Readout state |
| --- | --- | --- |
| uniform Nystrom | scaler `2d`; centers `m*d`; inverse root `m*m` | linear weights `(b+intercept)*c` |
| class hybrid centers | scaler `2d`; synthetic centers `m*d`; inverse root `m*m` | linear weights `(b+intercept)*c` |
| spectral | scaler `2d`; retained train matrix `n*d`; extension `n*r` | linear weights `(b+intercept)*c` |
| exact RBF | scaler `2d`; retained train matrix `n*d` | dual weights `n*c`, plus kernel intercept means when enabled |

The runner's `model_state_base_bytes` matches these stored arrays for the
compact representations. It adds `readout_state_bytes` to produce
`model_state_bytes`. For center models, `retained_train_samples=0` for the
hybrid representation and equals `m` for uniform Nystrom. Spectral and exact
RBF retain all `n` training rows for inference.

The exact RBF dual readout additionally stores target means and, with an
intercept, column means; the helper adds an 8-byte scalar overhead. Thus its
readout is not equivalent to a compact linear readout even when the prediction
formula is algebraically related.

## Construction/intermediate accounting

The runner records estimates, not peak process memory:

- center models: basis kernel `m*m`, train-to-center kernel `n*m` and
  validation-to-center kernel `v*m`;
- spectral: full train kernel `n*n`, eigenvalues `n`, eigenvectors `n*n` and
  validation cross-kernel `v*n`;
- exact RBF: train kernel `n*n` and validation cross-kernel `v*n`.

These terms describe large arrays explicitly constructed by the runner. They
may coexist temporarily, may be reused by numerical libraries, and exclude
allocator/native-library overhead. Therefore they are useful for comparing
scaling formulas but are not a substitute for a bounded peak-memory measure.

## Findings

1. Equal feature budgets do not imply equal deployed state. Center methods can
   be compact at inference but still require `m*m`, `n*m` and `v*m` arrays while
   fitting; spectral and exact RBF retain train-sized state.
2. `basis_is_train_samples` and `retained_train_samples` distinguish synthetic
   centers from train-sample landmarks, but the published row schema does not
   provide a single normalized “bytes per inference sample” field. That should
   be derived in a later report, not inferred from feature width alone.
3. The current accounting cannot establish energy savings or peak-RAM safety.
   A future OAC-06 protocol must include process boundaries, warmup, native
   allocations, timeout/OOM handling and the declared hardware.

## Conclusion

The static formulas support the plan's decision to investigate bounded-memory
kernel maps only after measuring the actual bottleneck. They do not yet justify
claiming a storage advantage for DNS05 residual blocks. This artifact is ready
for independent review, with the limitations above preserved.

