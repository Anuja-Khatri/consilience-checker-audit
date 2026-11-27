"""Fix regressions for the three candidate-new findings.

For each: run a set of VALID submissions through the real grader and a minimally
patched grader, confirm the scores are identical (the fix does not change
legitimate scoring), and confirm the exploit is now handled (rejected or made
order-invariant). Run from the repo root:

    python -I results/fixes/regression.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
import mleb_check as mc  # noqa: E402

MLEB = mc.DEFAULT_MLEB_ROOT
mc._install_mlebench(MLEB)


def grade_of(comp):
    fn, _ = mc._load_grade_fn(MLEB, f"mlebench/competitions/{comp}/grade.py")
    return fn


def ok(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    return cond


all_ok = True

# ---------------------------------------------------------------- champs F-MLEB-1
print("F-MLEB-1 champs-scalar-coupling: reject a non-finite aggregate score")
champs = grade_of("champs-scalar-coupling")
ans = pd.DataFrame({"id": [0, 1, 2, 3, 4, 5],
                    "type": ["1JHC", "1JHC", "1JHC", "2JHH", "2JHH", "2JHH"],
                    "scalar_coupling_constant": [80.0, 84.0, 90.0, 10.0, 12.0, 15.0]})


def champs_patched(sub, a):
    s = champs(sub, a)
    if s is None or not np.isfinite(s):  # the fix: reject a non-finite aggregate
        return None
    return s


valids = [ans[["id", "scalar_coupling_constant"]].assign(scalar_coupling_constant=ans["scalar_coupling_constant"] + d)
          for d in (0.5, 1.0, 3.0, 7.0)]
same = all(np.isclose(champs(v, ans), champs_patched(v, ans)) for v in valids)
all_ok &= ok("valid submissions score identically under the patch", same)
exploit = ans[["id", "scalar_coupling_constant"]].copy()
exploit.loc[exploit.index[3:], "scalar_coupling_constant"] = 999.0  # perfect on 1JHC only
all_ok &= ok("the -inf one-perfect-group exploit is rejected by the patch (None)", champs_patched(exploit, ans) is None)
all_ok &= ok("(the unpatched grader returned -inf on the exploit)", not np.isfinite(champs(exploit, ans)))

# ---------------------------------------------------------------- nomad2018 F-MLEB-3
print("F-MLEB-3 nomad2018: align by id (merge) instead of grading by row position")
from sklearn import metrics  # noqa: E402

nomad = grade_of("nomad2018-predict-transparent-conductors")
ans2 = pd.DataFrame({"id": [1, 2, 3, 4, 5],
                     "formation_energy_ev_natom": [0.10, 0.20, 0.30, 0.40, 0.50],
                     "bandgap_energy_ev": [1.0, 2.0, 3.0, 4.0, 5.0]})
cols = ["formation_energy_ev_natom", "bandgap_energy_ev"]


def nomad_patched(sub, a):
    m = a.merge(sub, on="id", suffixes=("_true", "_pred"))
    return (metrics.root_mean_squared_log_error(m["formation_energy_ev_natom_true"], m["formation_energy_ev_natom_pred"])
            + metrics.root_mean_squared_log_error(m["bandgap_energy_ev_true"], m["bandgap_energy_ev_pred"])) / 2


ref2 = ans2.copy()
for c in cols:
    ref2[c] = ans2[c] * 1.02
ordered = ref2[["id"] + cols]
same2 = np.isclose(nomad(ordered, ans2), nomad_patched(ordered, ans2))
all_ok &= ok("a valid ordered submission scores identically under the patch", same2)
shuf = ordered.sample(frac=1.0, random_state=3).reset_index(drop=True)
inv = np.isclose(nomad_patched(shuf, ans2), nomad_patched(ordered, ans2))
all_ok &= ok("the patched grader is order-invariant (shuffled == ordered)", inv)
all_ok &= ok("(the unpatched grader changed under the shuffle)", not np.isclose(nomad(shuf, ans2), nomad(ordered, ans2)))

print()
print("ALL REGRESSIONS PASS" if all_ok else "SOME REGRESSIONS FAILED")
sys.exit(0 if all_ok else 1)
