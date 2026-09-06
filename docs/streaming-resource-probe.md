# Streaming Resource Probe

Prespecified synthetic implementation diagnostic, preceding DNS05-BM. No benchmark
dataset is accessed. It measures fixed-geometry fitting only; it cannot promote
DNS05-BM or establish end-to-end savings. No model selection or novelty claim.

Run `python -m experiments.run_streaming_resource_probe` on Windows.
Five generator seeds: 81101, 81202, 81303, 81404, 81505; 6000 train and
1000 separate validation vectors, 16 standard-normal inputs. Three-class labels
come from a fixed linear rule seeded 81001. No test evaluation. Fixed gamma .03,
alpha .1, intercept enabled, 192 uniform train centers, float64. Compare batch
with blocks 64, 256 (primary), 1024. Each run has a fresh process; order reverses
on alternating seeds; BLAS threads fixed to one. Timeout 120 seconds per process.

Windows GetProcessMemoryInfo records lifetime peak working set after fitting,
including input generation and center decomposition. This is measured native
process memory, not an allocation estimate or a resettable fitting-only peak.
Raw train/validation/target arrays remain resident identically in all processes.
Inference uses identical 256-row chunks, one warmup, five timings. All weights
and validation scores are retained in JSON for cross-process equivalence checks.
Require rtol 1e-8, atol 1e-10; report all failures without retuning. Report per-seed
pairs, means and sample SD. The exploratory resource target is 25% median total
peak reduction for block 256; failing it is a negative result for this probe.

Oracle selection, preprocessing, full kernel reconstruction and full-network
training are outside this fixed-geometry probe. It does not replace the mandatory
model baselines or measurements in DNS05-BM. Commit this file and runner before
execution; preserve raw output and a curated complete result.
