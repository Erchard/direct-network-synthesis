# Experiment Register

The methodology is binding. Status describes execution, not success.

| ID | Question | Data boundary | Protocol / evidence | Status |
|---|---|---|---|---|
| DNS05-DW | Does sequential compilation beat equal output width? | Digits five 60/20/20 splits; test already inspected | research-log.md, depth-width config | Completed, negative |
| DNS05-FB | Does full basis remove the residual limitation? | Same digits partitions; exploratory reuse | dns05-full-basis-protocol.md, docs/results full-basis record | Completed, negative vs one-shot |
| DNS05-RO | Readout settings versus representation loss? | Only original train/validation for seeds 101,202,303,404,505 | dns05-readout-protocol.md, docs/results readout record | Completed, mixed/negative for compiler |
| DNS05-LM | Do simple landmark kernel maps explain the compiler gap? | Only original train/validation for seeds 101,202,303,404,505 | dns05-landmark-protocol.md, docs/results landmark record | Completed, landmarks beat compiler but not spectral/RBF |
| DNS05-EG | Which examples expose the compiler gap? | Only original train/validation for seeds 101,202,303,404,505 | dns05-error-geometry-protocol.md, docs/results error-geometry record | Completed, compiler loses recoverable local structure |
| DNS05-CA | Which compact candidate has the best quality/resource tradeoff? | Only original train/validation for seeds 101,202,303,404,505 | dns05-cost-protocol.md, docs/results cost record | Completed, uniform Nystrom 192 is best compact development candidate |
| DNS05-PT | Can synthetic RBF prototypes replace retained landmarks? | Only original train/validation for seeds 101,202,303,404,505 | dns05-prototype-protocol.md, configs/dns05_prototype_digits.json | Preregistered |

Digits is development data. A sample excluded in one split can belong to another
split's development portion; this is not a globally untouched holdout. The readout
runner excludes test membership within each split and does not produce test scores.
No independent confirmation dataset is reserved yet. Selecting one before future
confirmation is a separate milestone; new digits seeds do not create fresh evidence.
