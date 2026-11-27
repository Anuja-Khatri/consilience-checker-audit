# Corrections

Corrections to anything published here, after the fact, newest first. A correction
is logged here and, if it changes a number, the numbers lock and the report are
regenerated and the change noted in `VERIFICATION_LOG.md`.

### 2026-11-27. Five corrections after an external review pass.

1. **Order of events vs the preregistration.** The report did not state, as a deviation, that a pilot attacked the champs and nomad2018 graders about 20 minutes before the contract freeze, and that the contracts carry "expected to hold/break" notes from reading the code first. Corrected: `results/REPORT.md` section 4 now says these findings were found by reading and probing the code, then confirmed with frozen contracts, and names the pilot-before-freeze deviation; `VERIFICATION_LOG.md` logs the deviation explicitly. It is no longer presented as a blind preregistered discovery.
2. **champs severity downgraded from high to medium.** Exploiting it needs an exact match on a whole coupling type, which is unlikely in practice. The accurate point is that the metric `mean(log(MAE_per_type))` loses the floor it states (a zero within-type MAE sends the score to `-inf`). `results/findings.yaml` and `results/REPORT.md` reframed.
3. **`checker-audit verify` ignored the target path.** `verify` used a fixed folder for the OpenAI code while `run-all` accepted `--mleb-root`. Fixed: `verify` now takes and forwards `--mleb-root` (`cli.py`).
4. **Labelling slip.** `results/findings.yaml` and `GRADERS.md` called the simple-evals answer extractors "model-judge"; they are deterministic code. Relabelled "deterministic answer extractors".
5. **Coverage of the 23 "hold" graders.** The report now states clearly that "HOLD" is read with its coverage: the number of applicable checks differs per grader (some were exercised by as few as two), and no live model-judge grader was checked. Each grader's exact check set is in its certificate.

None of these changed a locked count: 30 MLE-bench contracts (23 hold, 6 break, 1 unrunnable), 3 simple-evals extractors break, 10 findings (3 candidate-new, 7 confirmations), 17 of 17 BLOCKs confirmed the independent second way.

### 2026-11-27. Three further corrections (second review pass).

6. **champs floor now cited, and the fix corrected.** The report and `findings.yaml` did not say where the floor comes from. It is in OpenAI's own repo: `mlebench/competitions/champs-scalar-coupling/description.md`, line 48, which states each group's MAE has a floor of `1e-9` (best score about `-20.7232`). The grader does not apply it. The citation is now in `findings.yaml`, `results/REPORT.md` and `DISCLOSURE_NOTE.md`, and the proposed fix is changed from "clamp at a small epsilon" to the stated `max(mae, 1e-9)`. `results/fixes/FIXES.md` and `results/fixes/regression.py` updated to demonstrate that fix (valid scores unchanged; the exploit's `-inf` becomes a finite score no lower than `-20.7232`). This turns the point from opinion into a fact checkable in OpenAI's own file.
7. **`DISCLOSURE_NOTE.md` champs wording** still said "it wins gold" with no floor and no low-exploitability note, contradicting correction 2. Rewritten to match.
8. **nomad2018 severity high -> medium.** It mis-scores a submission by row order but is not a route to a free medal, so medium is more defensible and consistent with the other labels. uw-madison stays high (a short submission really can win gold there).

### 2026-11-27. Two leftovers (third review pass).

9. **`results/fixes/regression.py` now accepts `--mleb-root`** (it previously used a fixed folder, like `verify` did, so a reproducer had to edit the file).
10. **Report no longer overclaims on fixes.** It said worked patches with a regression check exist "for the three candidate-new findings", but uw-madison's fix is only described in `FIXES.md` with no automated regression. The sentence now says champs and nomad2018 have a passing regression and uw-madison's fix is described (its run-length-encoded masks make an inline regression heavier; the fix is the same align-by-id pattern as nomad2018).
