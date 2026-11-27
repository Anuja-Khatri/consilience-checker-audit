---
checker: simple-evals/drop
kind: simple-evals extractor
source: https://github.com/openai/simple-evals @ 652c89d0ca9df547706735883097e9537d40dc47
verdict: BREAKS
checks_run: 5
blocks: 3
receipt: results/receipts/SE/drop/receipt.json
---

# Certificate: simple-evals/drop

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `simple-evals/drop` (simple-evals extractor).
- Source: https://github.com/openai/simple-evals at commit `652c89d0ca9df547706735883097e9537d40dc47`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- clean correct answer: **PASS** (expected_correct=True, observed=True)
- clean wrong answer rejected: **PASS** (expected_correct=False, observed=False)
- no Answer line, whole hedged response contains the gold string: **BLOCK** (expected_correct=False, observed=True)
- gold is a substring of a different wrong answer: **BLOCK** (expected_correct=False, observed=True)
- answer lists every option including the gold one: **BLOCK** (expected_correct=False, observed=True)

## Limits
- Probes are crafted from the task's answer format; they test the extractor's decision logic, not a full run on the eval's dataset. Most findings confirm already-filed issues cited in labels.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.

## Known public issues referenced
- SE-KNOWN-02 (see LABELS.yaml)
