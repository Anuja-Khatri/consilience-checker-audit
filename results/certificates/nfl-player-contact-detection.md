---
checker: nfl-player-contact-detection
kind: mle-bench grader
source: https://github.com/openai/mle-bench @ 507f92e1138bb6e40dac5c6ee7a6758e6424bf97
verdict: HOLDS
checks_run: 3
blocks: 0
receipt: results/receipts/MLEB/nfl-player-contact-detection/receipt.json
---

# Certificate: nfl-player-contact-detection

**Verdict: HOLDS** on the checks run. A verdict is read with its coverage below.

## Scope
- Checker: `nfl-player-contact-detection` (mle-bench grader).
- Source: https://github.com/openai/mle-bench at commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`.
- Contract author: model (drafted by an AI assistant, read before use).

## Checks run
- `order_invariance`: **PASS**. score unchanged (1.0) under row permutation
- `reject_wrong_length`: **PASS**. short submission (5 of 6 rows) rejected
- `reject_duplicate_ids`: **PASS**. submission with a duplicate id rejected

## Limits
- Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. A HOLDS is evidence on the checks run, not a proof of correctness.
- A HOLDS is evidence on the checks run at this commit, not a proof of correctness.
