# DNS05-BM: end-to-end resource gate failed

Analysis date 2026-09-07; evaluation source
`1b0b5608571a9b8666d0270eb79b1172384240dc`, executed 2026-09-06.
Protocol: [locked diagnostic](dns05-bm-end-to-end.md).
All 90 workers completed (three datasets, five splits, six methods).
No test metrics were computed. The existing record was summarized, not rerun.

| Dataset | Batch/stream validation accuracy, mean +/- sample SD | Median peak reduction | Mean stream-minus-batch fit seconds |
|---|---|---|---|
| Digits | 0.983287 +/- 0.004825 | 0.1394% | +0.121231 |
| Breast cancer | 0.971681 +/- 0.021128 | -0.0671% | +0.020645 |
| Synthetic multiclass v1 | 0.687029 +/- 0.018094 | 0.0544% | +0.028147 |

All 15 paired grids matched weights/scores at rtol=1e-8, atol=1e-10;
no prediction or readout-selection disagreements. Paired accuracy differences
were exactly zero. All three datasets fail the preregistered 25% median peak
reduction gate. Streaming was slower on average in this implementation.

In all 30 batch/stream workers, the lifetime peak after fitting equals the
peak already observed after oracle selection. Streaming the later readout cannot
lower that earlier peak. Small signed peak differences are not meaningful savings.
This preserves the positive fixed-geometry result but rejects extrapolation to
bounded-memory full fitting with this dense oracle. Do not launch the larger BM
budget grid on the strength of the earlier synthetic result. Pause this mechanism;
a future oracle-free method needs its own protocol, not post-hoc parameter tuning.

## Reproducibility

- [Complete original record, gzip](results/dns05_bm_end_to_end.json.gz),
  including all grid weights/scores, config, indices, timings and environment.
- Uncompressed SHA256: `ca4b4460f7c08b534e5c80958d176ccd31c8c89e184c198c4447303d7bdd2979`.
- [Summary](results/dns05_bm_end_to_end_summary.json): per-method means/sample
  SDs, paired differences and error records; all mandatory baselines retained.
- [Environment/source hashes](results/dns05_bm_end_to_end_environment.json).
- Recorded evaluation command is preserved verbatim in the full record.
  Summary command: `.venv\Scripts\python.exe experiments/summarize_bm_end_to_end.py`.
- To reanalyze without datasets, decompress the full record to
  `results/dns05_bm_end_to_end.json` and run the summarizer. No new evaluation needed.

Limitations: development splits, not independent confirmation; one timed fit
per model/split, Windows working set, eight streamed feature passes. Dense
post-fit reconstruction diagnostics are separately recorded and not excluded
from the artifact. Timing is not energy. No novelty or large-model claim.
