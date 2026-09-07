# Experiment Register

The methodology is binding. Status describes execution, not success.

## Structural-Synthesis Queue, 2026-09-07

All entries refer to [DCS/EDCS experimental plan](dcs-edcs-experiment-plan-uk.md).
No runner/config is locked yet; V0 entries are verification checks, not ML results.

| ID | Question | Boundary | Status |
|---|---|---|---|
| CS-A0 | Which established synthesis/repair tools and assumptions apply? | Primary-source and backend audit, no benchmark | V0 backend readiness checked; audits/cs-a0-backend.md; broader novelty audit pending |
| DCS-V0 | Does circuit extraction preserve exact finite behavior? | Fully specified software fixtures | Evaluated: 18 circuits equivalent, one exact-search timeout, no improvement over ABC on four completed pairs; dcs-v0-result.md |
| DCS-C1 | Does extraction beat standard logic optimization? | Five proposed 128/64/64 splits, test sealed during development | Planned, separate protocol required |
| EDCS-V0 | Can generic repair start from constants and preserve seen constraints? | Fully specified software fixtures | Queued |
| EDCS-L1 | Is local repair cheaper than rebuilding with the same examples? | Same proposed split manifest; no test feedback | Planned, separate protocol required |
| EDCS-U2 | Are updates cheap without forgetting unchanged behavior? | New update protocol/boundary required | Conditional on L1 |
| CS-S3 | Does a retained mechanism survive larger domains and state? | New scaling/sequence protocol required | Conditional, not authorized for execution |

## DNS Experiments

| ID | Question | Data boundary | Protocol / evidence | Status |
|---|---|---|---|---|
| DNS05-DW | Does sequential compilation beat equal output width? | Digits five 60/20/20 splits; test already inspected | research-log.md, depth-width config | Completed, negative |
| DNS05-FB | Does full basis remove the residual limitation? | Same digits partitions; exploratory reuse | dns05-full-basis-protocol.md, docs/results full-basis record | Completed, negative vs one-shot |
| DNS05-RO | Readout settings versus representation loss? | Only original train/validation for seeds 101,202,303,404,505 | dns05-readout-protocol.md, docs/results readout record | Completed, mixed/negative for compiler |
| DNS05-LM | Do simple landmark kernel maps explain the compiler gap? | Only original train/validation for seeds 101,202,303,404,505 | dns05-landmark-protocol.md, docs/results landmark record | Completed, landmarks beat compiler but not spectral/RBF |
| DNS05-EG | Which examples expose the compiler gap? | Only original train/validation for seeds 101,202,303,404,505 | dns05-error-geometry-protocol.md, docs/results error-geometry record | Completed, compiler loses recoverable local structure |
| DNS05-CA | Which compact candidate has the best quality/resource tradeoff? | Only original train/validation for seeds 101,202,303,404,505 | dns05-cost-protocol.md, docs/results cost record | Completed, uniform Nystrom 192 is best compact development candidate |
| DNS05-PT | Can synthetic RBF prototypes replace retained landmarks? | Only original train/validation for seeds 101,202,303,404,505 | dns05-prototype-protocol.md, docs/results prototype record | Completed, class-PCA prototypes close to Nystrom without retained train samples; global PCA negative |
| DNS05-DIP | Can boundary-aware synthetic prototypes improve class-local synthesis? | Only original train/validation for seeds 101,202,303,404,505 | dns05-dipole-prototype-protocol.md, docs/results dipole-prototype record | Completed, small gain over class-PCA prototypes but still below uniform Nystrom and spectral/RBF |
| DNS05-DEA | Which examples did dipole prototypes fix or break? | Only original train/validation for seeds 101,202,303,404,505 | dns05-dipole-error-audit-protocol.md, docs/results dipole-error-audit record | Completed, boundary signal is present but mixed; gain is a small error trade |
| DNS05-HYB | Can a fixed hybrid of class-local and boundary synthetic centers improve the train-sample-free candidate? | Only original train/validation for seeds 101,202,303,404,505 | dns05-hybrid-prototype-protocol.md, docs/results hybrid-prototype record | Completed, weak positive over dipole and class-PCA; still below uniform Nystrom, spectral and RBF |
| DNS05-FC1 | Does frozen hybrid prototype synthesis survive fresh non-digits boundaries? | `sklearn_breast_cancer` and fixed synthetic multiclass v1; stratified train/validation/test seeds 1101,1202,1303,1404,1505 | dns05-fresh-confirmation-protocol.md, docs/results fresh-confirmation record | Completed, mixed; hybrid transfers on synthetic multiclass but not clearly on breast cancer, still below RBF/spectral overall |
| DNS05-BM | Can a streaming Nystrom-style RBF map preserve compact quality with lower peak memory? | Existing failure-scaling train/validation boundaries only; no test evaluation | dns05-bm-end-to-end-result.md | Primary-budget diagnostic completed, negative end-to-end memory gate; larger grid paused |

Digits is development data. A sample excluded in one split can belong to another
split's development portion; this is not a globally untouched holdout. The readout
runner excludes test membership within each split and does not produce test scores.
No independent confirmation dataset is reserved yet. Selecting one before future
confirmation is a separate milestone; new digits seeds do not create fresh evidence.
