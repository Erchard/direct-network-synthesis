# Research Plan: Direct Synthesis and Independent Model Creation

Status: planned work, recorded 2026-09-05. No new experimental results.

This plan implements the motivation in [Hypothesis](hypothesis.md): enable small
independent teams to create, modify and run useful models within affordable
resource limits. It does not promise that technology can prevent monopoly.
[Methodology](methodology.md) remains binding and takes precedence over this plan.
The stages below are evidence gates, not a promise that every stage will succeed.

## 1. Establish the Starting Point

1. Preserve the completed depth/width and full-basis experiments as negative
   results for the current residual construction. Link every conclusion to the
   committed records in [Research Log](research-log.md).
2. Keep the distinction between sequential construction and neural depth explicit:
   current blocks project a shared fixed nonlinear basis and can be collapsed.
3. Treat digits as an explored development dataset. Changing its split seeds does
   not create independent confirmation. Do not use its previously inspected test
   partitions for further selection or validation.
4. Maintain an experiment register recording each hypothesis, development data,
   protected evaluation data, fixed seeds, model variants and decision rule.
5. Preserve the current baselines: linear ridge, RBF ridge and deterministic ReLU
   with a closed-form readout. Keep feature budgets and retained training data
   visible so that unlike models are not presented as equal-cost alternatives.

Deliverable: experiment register and a documented development/evaluation boundary.
Completion: each planned comparison has an identifiable data source and purpose.

## 2. Run the Immediate Readout Diagnostic

Question: how much of the quality loss comes from the representation, and how much
comes from the final conversion of that representation into class answers?

1. Add a validation-only execution path. It must not compute test predictions,
   test scores or test-driven stopping decisions. Test its isolation explicitly.
2. Use only the train and validation portions of the five existing splits, with
   seeds 101, 202, 303, 404 and 505. Fit all transformations on train alone.
3. Commit a separate diagnostic protocol and configuration before running it.
   Freeze the current bandwidth-selection rule and 192-feature budget.
4. Compare full RBF, rank-192 spectral features, one-shot compiled features and
   direct readout on the exact same PCA/quantile ReLU basis. Retain the minimum
   baselines. Do not add new residual variants in this diagnostic.
5. Match readout regularization and intercept conventions across representations.
   Preregister alpha values [0.001, 0.01, 0.1, 1.0] and intercept off/on as the
   proposed finite grid; verify equivalent primal/dual conventions in unit tests
   before locking the executable protocol. Report the entire grid.
6. Keep two analyses distinct: comparisons at identical settings, and comparisons
   after the same validation selection allowance. Fix tie-breaking in advance.
   Validation-selected performance remains developmental, not a test estimate.
7. Record validation accuracy, RMSE and R2 with explicit score encoding, train
   kernel error, rank, parameter count, solve time and inference time. Mark test
   fields as not evaluated instead of silently substituting validation scores.
8. Report per-split results, mean, sample standard deviation and paired changes.
   Include every failed or inconclusive variant in the research log.

Deliverable: committed diagnostic protocol, tested runner and complete result record.
Decision: if direct readout on the same basis matches or exceeds compilation under
matched settings, pause residual development on that basis. If readout settings
explain an improvement, document that mechanism before changing representation.
An ambiguous result warrants a bounded diagnostic, not an unrestricted search.

## 3. Verify Related Work and Choose a Bounded Next Hypothesis

1. Verify primary sources for fixed-feature networks, random features, kernel
   approximations, spectral embeddings and analytical representation synthesis.
   Record what was actually checked, with source links and precise comparisons.
2. Build a comparison table covering inputs, synthesis procedure, optimization,
   training cost, inference cost, data passes and retained training examples.
3. Identify whether a proposed DNS variant reproduces an existing method, changes
   an engineering tradeoff or introduces a question not resolved by those sources.
4. Select at most one representation change for the next locked comparison using
   training/validation evidence and the verified literature. State the predicted
   failure mechanism and which measurement could falsify the explanation.
5. If considering true depth, require later nonlinear features to depend on earlier
   representations; check algebraically whether the model collapses to one layer.
6. Preregister width, realized rank, parameter count and resource controls. A
   shared output dimension alone is insufficient for a fair depth comparison.

Deliverable: related-work note and one bounded experiment proposal.
Decision: reuse established methods when appropriate. Make no novelty claim until
the specific claim is supported by the literature review and experimental evidence.

## 4. Measure Total Cost Reliably

1. Add separate timing for preprocessing, feature construction, oracle selection,
   synthesis, final readout, serialization and end-to-end fitting. Include selection
   and unsuccessful trials when reporting the research/search budget.
2. Record CPU/GPU, available RAM, numerical-library versions, thread counts,
   precision and dataset size. Pin the environment sufficiently for reproduction.
3. Measure peak process memory and model bytes, including any stored training
   samples. Record disk reads, data passes and large intermediate arrays.
4. Benchmark prediction with fixed batch sizes, warmup and repeated measurements
   on train/validation inputs. Keep other checks out of timing runs. Timing repeats
   must not become repeated test-set evaluations.
5. Compare costs at a stated quality target and show quality/cost tradeoffs. Report
   uncertainty and failures due to memory or runtime limits.
6. Measure energy directly before making energy-saving claims; if measurement is
   unavailable, report that limitation rather than infer energy from runtime alone.

Deliverable: reproducible cost report and measurement configuration.
Decision: retain a candidate only if it offers a defensible quality/resource tradeoff
against the strongest relevant simple baseline, not merely against a weak variant.

## 5. Confirm on Untouched Data

1. Select at least two additional datasets with different relevant characteristics
   using task suitability, size and data rights, before viewing candidate outcomes.
   Record provenance, version and hashes. Do not claim broader generality from
   digits alone or choose new datasets because they produce favorable scores.
2. Create train/validation/test boundaries and at least five recorded splits before
   evaluation. Respect grouping, duplicates and temporal structure where relevant.
   Do not treat overlapping splits as independent samples for significance claims.
3. Specify primary metric, acceptable quality loss and resource advantage in the
   committed protocol before test access. Thresholds must reflect the intended
   task and hardware, not observed test outcomes.
4. Freeze candidate families and equal validation-selection allowances. Include
   the established baselines and a suitable gradient-trained reference if making
   claims about replacing gradient training; label its optimization explicitly.
5. Run the finalized test comparison once. Publish per-split results, means,
   standard deviations, paired differences and all prespecified comparisons.
6. Record a failed confirmation without adjusting the model against that test.
   Any revised model requires a newly defined independent confirmation boundary.

Deliverable: auditable confirmation report, including negative outcomes.
Decision: proceed toward scale only if the prespecified quality/cost criteria hold;
otherwise revise or close the candidate and retain the evidence.

## 6. Test Scaling and the Single-Pass Ambition

1. Prespecify increasing sample sizes and feature budgets, with time/memory limits
   and an explicit policy for recording incomplete runs.
2. Determine which steps require storing all examples, forming a dense kernel or
   revisiting data. Distinguish raw-data reads from passes over stored features.
3. Evaluate a bounded-memory formulation only after identifying the measured
   bottleneck. Compare approximations with the unmodified method where feasible.
4. If proposing one-pass synthesis, define what is accumulated during the pass,
   what remains stored and what computation occurs afterward. Include that work
   in total cost and account for data-dependent preprocessing requirements.
5. Verify that a single pass preserves the required quality under the locked
   comparison. Report cheap synthesis and one-pass access as separate properties.
6. Optimize implementation only after profiling. Keep Python as the reference;
   move a demonstrated bottleneck to another language only with numerical
   equivalence checks and measured end-to-end benefit.

Deliverable: scaling curves and an explicit resource/data-access account.
Decision: abandon the single-pass claim if it requires hidden rereads or unbounded
storage. A useful multi-pass direct method remains a valid research outcome.

## 7. Define and Reproduce an Accessibility Benchmark

1. Choose a concrete useful task. Do not equate success on small classification
   tasks with the capabilities of a general-purpose language model.
2. Before evaluation, specify minimum quality, maximum total fitting time, peak
   memory, model storage, inference latency and an accessible hardware profile.
   Record a dated cost basis for any monetary budget; no budget is fixed yet.
3. Publish code, environment, commands, configuration, seeds and legally usable
   data or a lawful reproducible acquisition procedure. Document artifact rights
   and any dependencies that block independent modification or redistribution.
4. Provide portable model artifacts and a local inference path. Check that normal
   operation does not require a single proprietary hosted service.
5. Have an independent person or team reproduce the result in a clean environment
   on the declared hardware. Record setup effort, failures and deviations as well
   as final quality and resource use. Local reruns are not independent reproduction.
6. Test continuation without the original developer's account: installation,
   model modification, artifact export and migration of example user data/workflows.

Deliverable: independently reproduced model package and accessibility report.
Decision: claim only the demonstrated scope of independence. Code availability
alone does not establish affordability, portability or freedom to redistribute.

## 8. Maintain Evidence and Review Direction

1. Before each experiment, commit its question, variants, seeds, metrics, resource
   limits and decision criteria. This roadmap is not a substitute for that protocol.
2. After each milestone, commit a curated complete record and interpretation to
   the research log, then push to GitHub. Keep raw outputs under results/ and
   curated auditable records under docs/results/ according to methodology.
3. Record source commit, exact command and environment. Distinguish planned,
   implemented, evaluated and independently reproduced capabilities.
4. Review the next step using training/validation evidence, methodology and related
   work. Confirmation failure is reportable evidence, not a tuning opportunity.
5. Stop or redirect a branch when its bounded experiments do not support its
   premise. Do not add complexity simply to preserve the original expectation.
6. Keep economic implications conditional: the deliverable is a practical ability
   to create alternatives, not proof that data centers or monopolies disappear.

Immediate execution order: establish the data boundary, lock and implement the
validation-only readout diagnostic, publish its full result, then select the next
bounded hypothesis with related-work support. Later stages depend on those findings.
