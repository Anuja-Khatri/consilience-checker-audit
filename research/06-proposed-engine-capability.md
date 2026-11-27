# Proposed engine capability: a tabular-submission-grader harness for consilience stress

Source: the Phase 3 pilot (2026-11-27). This note records what the engine would need to cover eval graders directly, so the gap is proposed upstream rather than forked.

## What the pilot showed

`consilience stress` attacks a geometric construction (arrays, point sets, matrices, graphs) with invalid input, self-reports, naive search, single-field invariances and record claims. Eval graders are a different shape:

- **MLE-bench graders** take an id-keyed submission table and an answer table, raise `InvalidSubmissionError` on a malformed submission, return a metric, and a separate `rank_score` turns the metric into a medal against a leaderboard. The real flaws found (a metric-aggregation flaw that sends a mean log-MAE to negative infinity, and a positional-alignment flaw that ignores the id column) are not invalid-input exploits, and the positional flaw needs a joint permutation of the id and value columns, which stress 0.3 does not support.
- **simple-evals extractors** take a text response and a gold answer. The engine has no text field type.

So the engine's attack generator does not cover these, and this build uses a contract-driven checker in the engine's verdict and receipt vocabulary instead (decision D12).

## The proposed capability

A new harness kind for `consilience stress`, `tabular_grader`, with:

- a candidate that is an id-keyed table (id column plus one or more prediction columns), not only a flat array;
- a fixed, declared answer table and leaderboard, so the grader can be called as published;
- joint permutation of the id and value columns, so "row order must not change the score" becomes a testable invariance;
- a medal or threshold layer, so a verdict can be "an invalid or trivial submission won a medal";
- an aggregation-flaw probe (a submission perfect on one aggregation group only), for metrics that average a per-group transform such as `log(MAE)`.

A text-grader harness (`text_grader`) is a separate proposal: a candidate that is a text response, with leniency probes (hedge, multiple answers, substring, case and sign variants).

## Status

Not implemented in the engine. The checker in `src/mleb_check.py` reuses the engine's `PASS` / `BLOCK` / `ABSTAIN` verdicts, receipt discipline, independent second way and numbers lock, and stands in for the proposed harness until it exists. This keeps the build reuse-first and avoids a fork.
