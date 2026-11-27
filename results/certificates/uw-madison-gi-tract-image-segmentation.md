---
checker: uw-madison-gi-tract-image-segmentation
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: BREAKS
checks_run: 2
blocks: 2
receipt: results/receipts/MLEB/uw-madison-gi-tract-image-segmentation/receipt.json
---

# Certificate: uw-madison-gi-tract-image-segmentation

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `uw-madison-gi-tract-image-segmentation` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `order_invariance`: **BLOCK**. reference score 1.0 changed to 0.83667 under a row permutation
- `reject_wrong_length`: **BLOCK**. short submission accepted and won a gold (score=1.0)

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.
