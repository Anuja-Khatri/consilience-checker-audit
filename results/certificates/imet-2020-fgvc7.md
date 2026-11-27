---
checker: imet-2020-fgvc7
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: HOLDS
checks_run: 2
blocks: 0
receipt: results/receipts/MLEB/imet-2020-fgvc7/receipt.json
---

# Certificate: imet-2020-fgvc7

**Verdict: HOLDS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `imet-2020-fgvc7` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `order_invariance`: **PASS**. score unchanged (1.0) under row permutation
- `reject_wrong_length`: **PASS**. short submission (5 of 6 rows) rejected

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.
