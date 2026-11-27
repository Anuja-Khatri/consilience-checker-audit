# Verification log

Every deviation from the preregistration, every fix, and every re-check, in time order. The preregistration named the early-warning lines that would appear here if they occurred.

---

## 2026-11-27. Pilot (Phase 3). Early-warning line triggered: the Leg A harness question resolved to the fallback.

The preregistration section 4 listed as an early-warning line: "the Leg A harness question (decision D9) resolving to a fallback adapter rather than the engine directly." It has.

**What was run.** The real grading pipeline of two MLE-bench system-card graders (`Grader.__call__` plus `rank_score` from `grade_helpers.py`, with each competition's real `grade.py`), at commit `507f92e`, on crafted submissions, against synthetic answers and a synthetic leaderboard. `mlebench.utils` was stubbed (logging and `import_fn` only) to avoid data-prep dependencies; the grading logic is the unmodified published code. This was a probe, not a scored contract run; no numbers from it are locked.

**What was found (to be reproduced as scored contracts before anything is reported).**
- champs-scalar-coupling: a submission that predicts one coupling type exactly and garbage elsewhere scored `-inf`, which `rank_score` awarded a gold medal. Cause: the metric is the mean over types of `log(MAE_type)`, with no guard on a zero within-type MAE, so one zero-MAE type sends the mean to negative infinity. Distinct from the known duplicate-id issue #156 (`LABELS.yaml` MLEB-KNOWN-06); to be confirmed not the same mechanism before being called new.
- nomad2018-predict-transparent-conductors: the grader aligns predictions by row position and ignores the `id` column, so the same submission in a different row order scored differently (gold to no-medal). A correctness and robustness flaw.
- On both graders, NaN and `+inf` predictions were rejected through a scikit-learn exception, which `Grader.__call__` turns into `None` (no medal). So the shared helper's missing finiteness guard does not award a medal on these minimise metrics; it is relevant to maximise or unbounded metrics where a favourable non-finite score is not rejected upstream.

**Why `consilience stress` is not used as the attack generator for Leg A.** Its checks attack a geometric construction with invalid input, self-reports, naive search, single-field invariances and record claims. The two flaws above are a metric-aggregation flaw and a positional-alignment flaw; neither is an invalid-input exploit, and the positional flaw needs a joint permutation of the id and value columns, which stress 0.3 does not support. Driving these graders through stress returns PASS and misses the flaws. Decision D12 records the resolution: Leg A uses a contract-driven grader checker that reuses the engine's verdict set, receipt discipline, independent second way and numbers lock, and the new checker type is filed as a proposed engine capability.

**Status.** The pilot findings are not yet scored contracts. They are reproduced as frozen contracts under `contracts/MLEB/`, run after `CONTRACTS.sha256` is frozen, confirmed the independent second way, and cross-checked against `LABELS.yaml`, before any of them appears in `results/REPORT.md`.
