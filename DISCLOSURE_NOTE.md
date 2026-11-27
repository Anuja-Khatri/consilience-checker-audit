# Disclosure note (draft for Anu to send; nothing here is posted by the tool)

A friendly note to the maintainers of `openai/mle-bench` and `openai/simple-evals`.
Anu sends it, through whatever channel she chooses. A grader-correctness bug is an
ordinary bug, not a security vulnerability (see `research/01-system-cards.md`), so
the natural route is an ordinary report to the maintainers. Nothing is posted
publicly before the maintainers have had the time they ask for.

Every statement is about published code at a named commit. Each item has a receipt
that re-runs with `python cli.py verify` in the linked repository, and a proposed
patch with a check that valid submissions still score the same.

---

Hi, and thank you for publishing these graders openly.

I ran a small, reusable integrity checker over the grading code behind the
MLE-bench system-card subset (30 competition graders at commit `507f92e`) and three
simple-evals answer extractors (at commit `652c89d`). The good news first: **23 of
the 30 MLE-bench graders hold on every check I ran** (non-finite input, row order,
length, duplicate ids, range, and a per-group free-medal probe). That is the main
result. The rest of this note is the handful that did not, each with a receipt and
a one-line fix.

## Candidate-new (we did not find these in your issue trackers)

1. **champs-scalar-coupling.** The metric is the mean over coupling types of
   `log(MAE_type)`. A submission that predicts one type exactly and anything
   elsewhere drives that type's MAE to zero, so `log(MAE) = -inf`, the mean is
   `-inf`, and it wins gold. Fix: reject a non-finite aggregate score before
   ranking (patch and regression in `results/fixes/FIXES.md`). This is a different
   mechanism from the known duplicate-id issue #156.

2. **nomad2018-predict-transparent-conductors.** The grader reads the two
   prediction columns by row position and ignores the id column, so the same
   submission in a different row order scores differently. Fix: merge on id before
   computing RMSLE.

3. **uw-madison-gi-tract-image-segmentation.** The Dice term pairs masks by row
   position with `zip` and checks neither length nor the id set, so a row
   permutation changes the score and a submission missing its last rows is
   silently truncated and, being perfect on what it provides, wins gold. Fix:
   align masks by id and require the submission to cover every answer id.

## Already filed (noting them so you know I am not re-filing)

- champs-scalar-coupling accepts duplicate ids (#156).
- osic-pulmonary-fibrosis-progression keeps a medal for a partial submission (#153).
- jigsaw-unintended-bias thresholds predictions at 0.5 without validating them, so
  `+inf` or an out-of-range value keeps the gold medal (#157).
- smartphone-decimeter-2022 pairs within-trip rows by position, not time (#93).
- simple-evals DROP `fuzzy_match` is a bidirectional substring match (#133);
  MGSM `parse_answer` drops the sign and takes the last number (#129, #132);
  MMLU extraction takes the first answer line and credits a hedge (#33).

Everything, including the clean results, is re-runnable from receipts. Happy to
share the checker; it is generic and you can point it at graders you have not
released. Thanks again for the open code.
