# Proposed fixes for the candidate-new findings

Each fix is minimal and comes with a regression check that valid submissions still
score the same. `regression.py` runs the checks for F-MLEB-1 and F-MLEB-3 against
the real graders; F-MLEB-7 is described (its RLE-mask decoding makes an inline
regression heavy, so the patch and its regression plan are stated, not run here).
All three were confirmed: `python -I results/fixes/regression.py` prints ALL
REGRESSIONS PASS.

## F-MLEB-1 champs-scalar-coupling (reject a non-finite aggregate score)

The metric is `mean(log(MAE_per_type))`. A submission perfect on one type gives
that type MAE 0, so `log(0) = -inf` and the mean is `-inf`, which wins gold.

Minimal patch (in `grade`, after computing `score`):

```python
score = np.mean(log_maes)
if not np.isfinite(score):
    raise InvalidSubmissionError("non-finite score (a zero within-type MAE)")
return score
```

Regression (in `regression.py`): four valid submissions score identically before
and after; the one-perfect-group exploit, which returned `-inf` and won gold, is
now rejected. The broader property that `mean(log(MAE))` over-rewards a single
near-perfect type is a metric-design question beyond this validation fix; the
patch closes the exact `-inf` medal path that the check demonstrates.

## F-MLEB-3 nomad2018-predict-transparent-conductors (align by id)

The grader reads the two prediction columns by row position and ignores the id
column. Minimal patch (in `prepare_for_metric`), replace the positional read with
a merge on id:

```python
merged = answers.merge(submission, on="id", suffixes=("_true", "_pred"))
true_labels_formation = merged["formation_energy_ev_natom_true"]
predictions_formation = merged["formation_energy_ev_natom_pred"]
true_labels_bandgap   = merged["bandgap_energy_ev_true"]
predictions_bandgap   = merged["bandgap_energy_ev_pred"]
```

Regression: a valid ordered submission scores identically; the patched grader is
order-invariant (a shuffled submission scores the same as the ordered one), while
the unpatched grader changed under the shuffle.

## F-MLEB-7 uw-madison-gi-tract-image-segmentation (align by id; check coverage)

The Dice term pairs submission and answer masks by row position with `zip`, and
checks neither length nor the id set. Minimal patch (in `prepare_for_metric`):

1. require the submission id set to equal the answer id set, and the lengths to
   match (as other graders do), raising `InvalidSubmissionError` otherwise;
2. build the mask pairs by merging on the id column rather than `zip` over two
   independently ordered lists.

Regression plan: a valid submission scores identically; a row-permuted submission
scores the same (order-invariant); a submission missing rows is rejected rather
than silently truncated. The receipt already shows both exploit paths
(order dependence and truncation-to-gold) on the unpatched grader.
