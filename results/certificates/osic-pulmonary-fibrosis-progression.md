---
checker: osic-pulmonary-fibrosis-progression
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: BREAKS
checks_run: 4
blocks: 1
receipt: results/receipts/MLEB/osic-pulmonary-fibrosis-progression/receipt.json
---

# Certificate: osic-pulmonary-fibrosis-progression

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `osic-pulmonary-fibrosis-progression` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `reject_nonfinite`: **PASS**. NaN: score=np.float64(nan), medal=none; +inf: score=np.float64(-7.96224), medal=none; -inf: score=np.float64(-7.96224), medal=none
- `order_invariance`: **PASS**. score unchanged (-4.59507) under row permutation
- `reject_wrong_length`: **BLOCK**. short submission accepted and won a silver (score=-4.59507)
- `reject_duplicate_ids`: **PASS**. submission with a duplicate id rejected

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.

## Known public issues referenced
- MLEB-KNOWN-07 (see LABELS.yaml)
