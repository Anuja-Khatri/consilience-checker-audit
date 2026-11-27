---
checker: jigsaw-unintended-bias-in-toxicity-classification
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: BREAKS
checks_run: 5
blocks: 2
receipt: results/receipts/MLEB/jigsaw-unintended-bias-in-toxicity-classification/receipt.json
---

# Certificate: jigsaw-unintended-bias-in-toxicity-classification

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `jigsaw-unintended-bias-in-toxicity-classification` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `reject_nonfinite`: **BLOCK**. NaN: score=0.84375, medal=none; +inf: score=1.0, medal=gold; -inf: score=0.84375, medal=none
- `order_invariance`: **PASS**. score unchanged (1.0) under row permutation
- `reject_wrong_length`: **PASS**. short submission (7 of 8 rows) rejected
- `reject_duplicate_ids`: **PASS**. submission with a duplicate id rejected
- `range`: **BLOCK**. out-of-range value accepted (score=1.0, medal=gold)

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.

## Known public issues referenced
- MLEB-KNOWN-05 (see LABELS.yaml)
