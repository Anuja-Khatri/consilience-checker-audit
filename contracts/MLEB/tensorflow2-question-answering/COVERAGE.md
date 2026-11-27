# Coverage: tensorflow2-question-answering

**Status: unrunnable (ABSTAIN), reference_rejected.**

The grader expects `answers` to be a Python list of nested dicts parsed from
`simplified-nq-train.jsonl` (each with `annotations[0].long_answer`,
`short_answers`, `yes_no_answer`). This checker's synthetic-answers builder
produces a flat pandas DataFrame (id column plus value columns), which the
nested structure cannot be expressed in. The grader iterates `answers` as a
list of dicts and raises before computing a score, so no valid reference
submission is accepted (reference_score is None). The contract is therefore
ABSTAIN, reported as unrunnable, not HOLDS.

By reading the published code at commit 507f92e, this grader is among the
better-validated ones: it checks submission length, the id set, uniqueness and
the answer format, and its metric is bounded in [0, 1]. A fuller check would
need a nested-answer harness, which is out of scope for this build.
