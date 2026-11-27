---
checker: simple-evals/mgsm
kind: simple-evals extractor
source: https://github.com/openai/simple-evals @ 652c89d0ca9df547706735883097e9537d40dc47
verdict: BREAKS
checks_run: 4
blocks: 3
receipt: results/receipts/SE/mgsm/receipt.json
---

# Certificate: simple-evals/mgsm

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `simple-evals/mgsm` (simple-evals extractor).
- Source: https://github.com/openai/simple-evals at commit `652c89d0ca9df547706735883097e9537d40dc47`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- clean correct answer: **PASS** (expected_correct=True, observed=True)
- opposite-sign answer credited (minus sign not captured): **BLOCK** (expected_correct=False, observed=True)
- correct answer marked wrong because a later number wins: **BLOCK** (expected_correct=True, observed=False)
- a trailing aside number overrides the real answer: **BLOCK** (expected_correct=True, observed=False)

## Limits
- Probes are crafted from the task's answer format; they test the extractor's decision logic, not a full run on the eval's dataset. Most findings confirm already-filed issues cited in labels.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.

## Known public issues referenced
- SE-KNOWN-04 (see LABELS.yaml)
