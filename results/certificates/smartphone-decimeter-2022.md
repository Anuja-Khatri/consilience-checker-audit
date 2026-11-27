---
checker: smartphone-decimeter-2022
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: BREAKS
checks_run: 4
blocks: 1
receipt: results/receipts/MLEB/smartphone-decimeter-2022/receipt.json
---

# Certificate: smartphone-decimeter-2022

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `smartphone-decimeter-2022` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `reject_nonfinite`: **PASS**. NaN: score=np.float64(nan), medal=none; +inf: score=np.float64(nan), medal=none; -inf: score=np.float64(nan), medal=none
- `order_invariance`: **BLOCK**. reference score 0.0 changed to 63618.88673 under a row permutation
- `reject_wrong_length`: **PASS**. short submission (5 of 6 rows) rejected
- `reject_duplicate_ids`: **PASS**. submission with a duplicate id rejected

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.

## Known public issues referenced
- MLEB-KNOWN-09 (see LABELS.yaml)
