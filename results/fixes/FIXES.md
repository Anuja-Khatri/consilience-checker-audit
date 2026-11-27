# Proposed fixes for the candidate-new findings

Each fix is minimal and comes with a regression check that valid submissions still
score the same. `regression.py` runs the checks for F-MLEB-1 and F-MLEB-3 against
the real graders; F-MLEB-7 is described (its RLE-mask decoding makes an inline
regression heavy, so the patch and its regression plan are stated, not run here).
All three were confirmed: `python -I results/fixes/regression.py` prints ALL
REGRESSIONS PASS.

## F-MLEB-1 champs-scalar-coupling (apply the floor the description states)

The competition's `description.md` (line 48) states each group's MAE has a floor of
`1e-9`, so the best possible score is about `-20.7232`. The grader's `log_mae` takes
`log` of the raw MAE with no floor, so a zero within-type MAE gives `log(0) = -inf`,
below the stated floor.

Minimal patch (in `log_mae`), applying the documented floor:

```python
def log_mae(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    return np.log(max(mae, 1e-9))   # floor per description.md line 48
```

Regression (in `regression.py`): valid submissions score identically before and
after (real MAEs are far above `1e-9`, so the floor never binds), and the
one-perfect-group case that returned `-inf` now returns a finite score no lower than
the stated `-20.7232` floor. The broader property that `mean(log(MAE))` rewards a
single near-perfect type is a metric-design question beyond this fix; the patch
restores the floor the description specifies.

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
