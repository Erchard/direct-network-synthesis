# OAC-03: FMSA Artifact Provenance and Completeness

Status: local owner audit; not an independent reproduction or maintainer
acceptance.

## Scope and allowed data

This audit inspected only the published JSON artifact, its protocol and the
recorded source/config metadata. No benchmark command was run, no test field
was evaluated and no protected partition was loaded.

Artifact: `docs/results/dns05_failure_scaling_audit.json`

Recorded artifact SHA256:

`CF02C55097383D12A36850081CD9ED749601D6F7572CE8C96CE13439D783AEFB`

## Recorded provenance

| Field | Recorded value |
| --- | --- |
| source commit | `c4c0a36f95f7b475506e94ad508ce297067b4993` |
| command | `D:\Projects\direct-network-synthesis\experiments\run_dns05_failure_scaling.py --config configs\dns05_failure_scaling_audit.json --output results\dns05_failure_scaling_audit.json` |
| Python | 3.12.14 |
| NumPy | 2.5.2 |
| scikit-learn | 1.9.0 |
| platform | Windows 10 build 19045 |
| data rows | 1,920 |
| selected rows | 240 |
| paired differences | 45 |
| test status | `not_evaluated` |

The result contains split records with train, validation and excluded indices.
It records three datasets and fifteen declared split seeds:

- `sklearn_digits`: 5 splits, data hash
  `f6d9e39f37dc45d327f6db33428ee58970ccceabb2535a5c179de35886b70443`;
- `sklearn_breast_cancer`: 5 splits, data hash
  `25e2eb7b7a8745b1bde5ba18bc4969983d2e2f403291ecd5bde4a29ef30c3859`;
- `synthetic_multiclass_v1`: 5 splits, data hash
  `a37339bef74130757cc254a1d323793254d63703baa967c76f70d6e495b405bd`.

The row schema includes validation metrics, null test metrics, reconstruction
error, rank, feature budget, timing fields, state-byte estimates and the
recorded `test_status`. The top-level artifact also preserves the config,
selected summaries and paired comparisons.

## Findings and limitations

1. The required hash, 1,920 grid rows, 240 selected rows, 45 paired entries and
   `test_status=not_evaluated` are present and consistent with the locked audit
   description.
2. The artifact records a source commit and environment versions, but the
   original command uses an absolute Windows path. Reproduction should use the
   repository-relative command from the protocol and record its own path.
3. The recorded source-status field was not a complete clean-tree manifest. It
   is therefore insufficient by itself to prove that no uncommitted file
   influenced the original run; a future reproduction must record full status
   and the exact config/artifact hashes.
4. The artifact records estimated intermediate/state bytes, not a process-level
   peak-memory measurement. It must not be used as measured RAM evidence.
5. This owner audit verifies fields and provenance claims in the artifact. It
   does not verify the numerical rows by rerunning the experiment and does not
   award independent-reproducer credit.

## Reproduction handoff

The next independent contributor should use OAC-11's frozen validation-only
command and compare row identities, discrete selections and per-split metrics.
Any mismatch is reportable evidence; no seed, tolerance or candidate may be
changed to make the records agree.

Audit command record: PowerShell `Get-FileHash ... -Algorithm SHA256` and
`ConvertFrom-Json` field inspection. No benchmark execution.
