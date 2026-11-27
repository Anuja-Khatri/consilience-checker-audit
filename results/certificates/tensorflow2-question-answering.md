---
checker: tensorflow2-question-answering
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: ABSTAIN
checks_run: 1
blocks: 0
receipt: results/receipts/MLEB/tensorflow2-question-answering/receipt.json
---

# Certificate: tensorflow2-question-answering

**Verdict: ABSTAIN** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `tensorflow2-question-answering` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `reference`: **ABSTAIN**. reference_rejected: the grader returned None on the declared-valid reference submission; the contract cannot be exercised as written

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.
