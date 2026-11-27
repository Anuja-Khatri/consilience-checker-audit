---
checker: simple-evals/mmlu
kind: simple-evals extractor
source: https://github.com/openai/simple-evals @ 652c89d0ca9df547706735883097e9537d40dc47
verdict: BREAKS
checks_run: 4
blocks: 2
receipt: results/receipts/SE/mmlu/receipt.json
---

# Certificate: simple-evals/mmlu

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `simple-evals/mmlu` (simple-evals extractor).
- Source: https://github.com/openai/simple-evals at commit `652c89d0ca9df547706735883097e9537d40dc47`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- clean correct answer: **PASS** (expected_correct=True, observed=True)
- revised final answer ignored (first match wins): **BLOCK** (expected_correct=True, observed=False)
- hedge across two letters credited as the first: **BLOCK** (expected_correct=False, observed=True)
- boxed-latex correct answer still parsed (normalize_response): **PASS** (expected_correct=True, observed=True)

## Limits
- Probes are crafted from the task's answer format; they test the extractor's decision logic, not a full run on the eval's dataset. Most findings confirm already-filed issues cited in labels.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.

## Known public issues referenced
- SE-KNOWN-03 (see LABELS.yaml)
