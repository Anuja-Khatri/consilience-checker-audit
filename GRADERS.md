# Check your own grader

Nothing in this tool is specific to OpenAI. Point a contract at your own grader and run the same checks. This is the "clone and check yourself" path a lab can run on graders it cannot release.

## 1. Your grader

A grader is any function:

```python
def grade(submission: pandas.DataFrame, answers: pandas.DataFrame) -> float:
    ...
```

It returns a score. It may raise on a malformed submission; the tool treats any exception as a rejection (the submission scored nothing), the same convention `consilience stress` uses. See `examples/byo_grader/my_grader.py`.

## 2. Your contract

Write a `contract.yaml`. The contract states what a valid submission is, from the task, not from the grader. Key fields:

```yaml
harness:
  kind: callable                       # use your own grade function
  grade: "path/to/your_grader.py:grade"  # module:function or file.py:function
  round: 5                             # optional: round the score, as some graders do

id_column: id                          # the column that aligns a submission to the answers (or null)
prediction_columns: [pred]             # the prediction column(s)
submission_extra_columns: []           # other columns the grader reads from the submission
group_column: null                     # set if the metric averages a per-group transform

metric:
  direction: higher_better             # or lower_better; sets which scores win medals
  bounded: [0, 1]                      # the valid score range, or [null, null]
prediction_range: [0, 1]              # if the task bounds predictions (enables the `range` check)

answers:                               # a small synthetic answers table, schema-faithful
  id: [1, 2, 3, 4, 5]
  columns:
    label: [0, 1, 0, 1, 1]
    pred: [0, 1, 0, 1, 1]              # a dummy copy so the reference builder can select the submission schema

leaderboard: [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]   # scores to assign medals against

reference:
  kind: exact                          # a valid submission (copy of answers), or
  # kind: offset                       # offset the predictions by a small amount
  # offset: 2.0

checks:                                # list only the checks your grader's shape supports
  - order_invariance
  - reject_wrong_length
  - reject_duplicate_ids
  - reject_nonfinite
  - range
  - no_free_gold_subset_perfect
```

Synthetic answers are enough for these checks: they test the grader's validation and arithmetic, which do not depend on the real ground-truth values. State in the contract that the answers are synthetic.

## 3. Run it

```bash
checker-audit run path/to/contract.yaml --out results/receipts/mine
checker-audit verify        # independent second-way re-derivation of any BLOCK
```

A `BLOCK` means the grader accepted something the contract rules out, or its score depends on something that must not change it. The receipt stores the exact counterexample so anyone can re-run it.

## 4. The checks, and when each applies

| Check | Applies when | BLOCKs when |
|---|---|---|
| `reject_nonfinite` | numeric prediction column | a NaN or infinite prediction is accepted and wins a medal |
| `order_invariance` | there is an id column | the same rows in a different order score differently |
| `reject_wrong_length` | always | a short submission is accepted and wins a medal |
| `reject_duplicate_ids` | there is an id column | a duplicate id is accepted and changes the score |
| `range` | the task bounds predictions (`prediction_range`) | an out-of-range prediction is accepted and wins a medal |
| `no_free_gold_subset_perfect` | the metric averages a per-group transform (`group_column`) | a submission perfect on one group only wins a medal |

List only the checks your grader's shape supports. A clean grader that holds on every check is a real, reportable result, not an absence of findings.

## 5. Text-answer graders

For a model-judge answer extractor (text in, correct/incorrect out), use the extractor checker instead: vendor the extractor functions and write probes at known validity. See `contracts/SE/drop/` for a worked example.
