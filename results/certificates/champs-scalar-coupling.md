---
checker: champs-scalar-coupling
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: BREAKS
checks_run: 5
blocks: 2
receipt: results/receipts/MLEB/champs-scalar-coupling/receipt.json
---

# Certificate: champs-scalar-coupling

**Verdict: BREAKS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `champs-scalar-coupling` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `reject_nonfinite`: **PASS**. NaN: score=None, medal=none; +inf: score=None, medal=none; -inf: score=None, medal=none
- `order_invariance`: **PASS**. score unchanged (1.09861) under row permutation
- `reject_wrong_length`: **PASS**. short submission (5 of 6 rows) rejected
- `reject_duplicate_ids`: **BLOCK**. duplicate id accepted (score=3.316, medal=none, changed=True)
- `no_free_gold_subset_perfect`: **BLOCK**. a submission perfect on one group only won a gold (score=-inf)

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.

## Known public issues referenced
- MLEB-KNOWN-06 (see LABELS.yaml)
