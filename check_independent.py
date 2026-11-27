"""Independent second-way verifier for the MLE-bench grader findings.

It imports NOTHING from src/mleb_check.py and nothing from consilience. It
reads each receipt, and for every BLOCK it:
  1. re-loads the real grader with its own loader and re-runs the stored
     counterexample submission (a fresh second execution of the target), and
  2. re-derives the finding with its own arithmetic from the stored data,
     independently of how the grader computed the score.
A disagreement voids the finding (exit non-zero); it must then be resolved
and logged in VERIFICATION_LOG.md.

Usage:
    python -I check_independent.py --receipts results/receipts/MLEB --mleb-root /home/user/openai-targets/mle-bench
"""
from __future__ import annotations

import argparse
import glob
import importlib
import importlib.util
import json
import logging
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd

MEDALS = ("gold", "silver", "bronze")


# --- own grader loader (independent of mleb_check) -------------------------- #
def load_pipeline(mleb_root: str):
    pkg = types.ModuleType("mlebench")
    pkg.__path__ = [str(Path(mleb_root) / "mlebench")]
    sys.modules.setdefault("mlebench", pkg)
    utils = types.ModuleType("mlebench.utils")
    utils.get_logger = lambda name, level=logging.INFO, filename=None: logging.getLogger(name)
    utils.import_fn = lambda s: getattr(importlib.import_module(s.split(":")[0]), s.split(":")[1])
    sys.modules.setdefault("mlebench.utils", utils)
    gh_path = Path(mleb_root) / "mlebench" / "grade_helpers.py"
    spec = importlib.util.spec_from_file_location("mlebench.grade_helpers", gh_path)
    gh = importlib.util.module_from_spec(spec)
    sys.modules["mlebench.grade_helpers"] = gh
    spec.loader.exec_module(gh)
    return gh


def load_grade(mleb_root: str, grade_rel: str):
    path = Path(mleb_root) / grade_rel
    comp_dir = path.parent
    pkgname = "indep_comp_" + comp_dir.name.replace("-", "_").replace(".", "_")
    if pkgname not in sys.modules:
        pkg = types.ModuleType(pkgname)
        pkg.__path__ = [str(comp_dir)]
        pkg.__package__ = pkgname
        sys.modules[pkgname] = pkg
    modname = f"{pkgname}.grade"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkgname
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod.grade


def df_from(d):
    return pd.DataFrame(d)


def num_or_none(x):
    if x is None:
        return None
    if isinstance(x, str):
        if x == "inf":
            return np.inf
        if x == "-inf":
            return -np.inf
        if x == "nan":
            return np.nan
        try:
            return float(x)
        except ValueError:
            return None
    return float(x)


def rerun(gh, grade_fn, submission_dict, answers_dict, leaderboard):
    grader = gh.Grader(name="indep", grade_fn="builtins:len")
    grader.grade_fn = grade_fn
    sub = df_from(submission_dict)
    ans = df_from(answers_dict)
    score = grader(sub, ans)
    lb = pd.DataFrame({"score": list(leaderboard)})
    medal = "none"
    if score is not None:
        r = grader.rank_score(score, lb)
        for m in ("gold_medal", "silver_medal", "bronze_medal"):
            if r[m]:
                medal = m.replace("_medal", "")
    return score, medal, sub, ans


# --- independent re-derivations per check ----------------------------------- #
def verify_block(gh, grade_fn, receipt, check):
    """Return (ok, note). ok True means the finding is independently confirmed."""
    name = check["check"]
    cex = check["counterexample"]
    if cex is None:
        return False, "BLOCK had no stored counterexample"
    answers = receipt["synthetic_answers"]
    lb = receipt["synthetic_leaderboard"]
    pcols = receipt.get("prediction_columns") or []
    idcol = receipt.get("id_column")
    gcol = receipt.get("group_column")

    score, medal, sub, ans = rerun(gh, grade_fn, cex["submission"], answers, lb)

    # 1. the re-run must reproduce the receipt's observed outcome
    obs = num_or_none(cex.get("observed_score"))
    reproduced = (
        (score is None and obs is None)
        or (score is not None and obs is not None and (
            (np.isinf(score) and np.isinf(obs) and np.sign(score) == np.sign(obs))
            or (np.isnan(score) and np.isnan(obs))
            or np.isclose(float(score), float(obs), rtol=1e-6, atol=1e-9)))
    )
    if not reproduced:
        return False, f"re-run score {score} does not match receipt {obs}"

    # 2. independent re-derivation of the finding
    if name == "reject_nonfinite":
        vals = pd.concat([pd.to_numeric(sub[c], errors="coerce") for c in pcols]) if pcols else pd.Series(dtype=float)
        has_nonfinite = bool((~np.isfinite(vals.to_numpy(dtype=float))).any())
        if has_nonfinite and medal in MEDALS:
            return True, f"non-finite prediction accepted and won {medal}"
        return False, f"expected a non-finite prediction winning a medal; got medal={medal}, has_nonfinite={has_nonfinite}"

    if name == "order_invariance":
        # independent: the stored reference and shuffled submissions are the SAME multiset of
        # rows in a different order, yet score differently -> the grader depends on row order.
        s_shuf = score  # re-run of the stored shuffled submission
        ref_sub = cex.get("reference_submission")
        if ref_sub is not None:
            s_ref, _m, _s, _a = rerun(gh, grade_fn, ref_sub, answers, lb)
            rrows = sorted(tuple(map(str, r)) for r in df_from(ref_sub).values.tolist())
            srows = sorted(tuple(map(str, r)) for r in sub.values.tolist())
            is_perm = rrows == srows
            differ = (s_ref is None) != (s_shuf is None) or (
                s_ref is not None and s_shuf is not None and not np.isclose(float(s_ref), float(s_shuf), rtol=1e-9, atol=1e-12))
            if is_perm and differ:
                return True, f"a row permutation changed the score ({s_ref} -> {s_shuf})"
            return False, f"permutation={is_perm}, scores ref={s_ref} shuf={s_shuf}"
        if not idcol:
            return False, "no reference submission stored and no id column"
        sorted_sub = sub.sort_values(idcol).reset_index(drop=True)
        s_sorted, _m, _s, _a = rerun(gh, grade_fn, sorted_sub.to_dict(orient="list"), answers, lb)
        differ = (s_sorted is None) != (s_shuf is None) or (
            s_sorted is not None and s_shuf is not None and not np.isclose(float(s_sorted), float(s_shuf), rtol=1e-9, atol=1e-12))
        if differ:
            return True, f"score depends on row order (sorted={s_sorted}, shuffled={s_shuf})"
        return False, "could not reproduce order dependence"

    if name == "reject_wrong_length":
        shorter = len(sub) < len(ans)
        if shorter and score is not None and medal in MEDALS:
            return True, f"a {len(sub)}-row submission (answers have {len(ans)}) was accepted and won {medal}"
        return False, f"expected a short accepted medal-winning submission; shorter={shorter}, score={score}, medal={medal}"

    if name == "reject_duplicate_ids":
        if not idcol:
            return False, "no id column"
        ids = sub[idcol].tolist()
        has_dup = len(ids) != len(set(ids))
        ref = num_or_none(receipt.get("reference_score"))
        changed = ref is None or (score is not None and not np.isclose(float(score), float(ref), rtol=1e-9, atol=1e-12))
        if has_dup and score is not None and (changed or medal in MEDALS):
            return True, f"duplicate id accepted (score={score}, medal={medal}, changed={changed})"
        return False, f"expected an accepted duplicate id changing the score; got dup={has_dup}, score={score}"

    if name == "range":
        rng = receipt.get("prediction_range")
        vals = pd.concat([pd.to_numeric(sub[c], errors="coerce") for c in pcols]) if pcols else pd.Series(dtype=float)
        out = False
        if rng:
            lo, hi = rng
            arr = vals.to_numpy(dtype=float)
            out = bool(((hi is not None) and (arr > hi).any()) or ((lo is not None) and (arr < lo).any()))
        if out and medal in MEDALS:
            return True, f"out-of-range prediction accepted and won {medal}"
        return False, f"expected an out-of-range prediction winning a medal; got medal={medal}, out_of_range={out}"

    if name == "no_free_gold_subset_perfect":
        if not (gcol and idcol and pcols):
            return False, "missing id/group/prediction columns to re-derive"
        merged = ans.merge(sub[[idcol] + pcols], on=idcol, suffixes=("_true", "_pred"))
        col = pcols[0]
        true_c, pred_c = f"{col}_true", f"{col}_pred"
        if true_c not in merged or pred_c not in merged:
            # single prediction column may keep its name if answers lacks it; recompute by alignment
            merged = ans.merge(sub[[idcol] + pcols].rename(columns={col: col + "_pred"}), on=idcol)
            true_c, pred_c = col, col + "_pred"
        per_group_err = merged.groupby(gcol).apply(
            lambda g: float(np.mean(np.abs(g[true_c].to_numpy(dtype=float) - g[pred_c].to_numpy(dtype=float)))),
            include_groups=False,
        )
        n_zero = int((per_group_err.to_numpy() == 0.0).sum())
        n_large = int((per_group_err.to_numpy() > 1.0).sum())
        if n_zero >= 1 and n_large >= 1 and medal in MEDALS:
            return True, f"perfect on {n_zero} group(s), far off on {n_large}, yet won {medal} (per-group MAE={per_group_err.to_dict()})"
        return False, f"expected one perfect group + one bad group winning a medal; zero={n_zero}, large={n_large}, medal={medal}"

    return False, f"no independent re-derivation implemented for check '{name}'"


def se_verify(se_receipts_glob, contracts_root):
    """Independent re-derivation of the simple-evals extractor findings: load each
    vendored extractor FRESH (a second execution, independent of src/extract_check.py)
    and re-run every BLOCK probe. The vendored functions are pure, so a disagreement
    would mean the receipt was not produced by this code."""
    results = []
    for rp in sorted(glob.glob(se_receipts_glob)):
        receipt = json.loads(Path(rp).read_text())
        eval_name = receipt["eval"]
        ext_path = Path(contracts_root) / "SE" / eval_name / "extractor.py"
        spec = importlib.util.spec_from_file_location(f"indep_se_{eval_name}", ext_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for probe in receipt["probes"]:
            if probe["verdict"] != "BLOCK":
                continue
            observed = bool(mod.decide(probe["response"], probe["gold"]))
            reproduced = observed == probe["observed_correct"]
            is_finding = observed != probe["expected_correct"]
            ok = reproduced and is_finding
            note = (f"re-derived observed={observed} (receipt {probe['observed_correct']}), "
                    f"expected={probe['expected_correct']}")
            results.append((eval_name, probe["label"], ok, note))
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipts", default="results/receipts/MLEB")
    ap.add_argument("--se-receipts", default="results/receipts/SE")
    ap.add_argument("--contracts", default="contracts")
    ap.add_argument("--mleb-root", default="/home/user/openai-targets/mle-bench")
    args = ap.parse_args()

    gh = load_pipeline(args.mleb_root)
    receipts = sorted(glob.glob(f"{args.receipts}/*/receipt.json"))
    total_blocks = confirmed = disagreed = 0
    disagreements = []

    for rp in receipts:
        receipt = json.loads(Path(rp).read_text())
        grade_fn = load_grade(args.mleb_root, receipt["source"]["grade_path"])
        cid = receipt["competition_id"]
        for check in receipt["checks"]:
            if check["verdict"] != "BLOCK":
                continue
            total_blocks += 1
            ok, note = verify_block(gh, grade_fn, receipt, check)
            tag = "CONFIRM" if ok else "DISAGREE"
            print(f"[{tag}] {cid} / {check['check']}: {note}")
            if ok:
                confirmed += 1
            else:
                disagreed += 1
                disagreements.append((cid, check["check"], note))

    for eval_name, label, ok, note in se_verify(f"{args.se_receipts}/*/receipt.json", args.contracts):
        total_blocks += 1
        tag = "CONFIRM" if ok else "DISAGREE"
        print(f"[{tag}] SE/{eval_name} / {label}: {note}")
        if ok:
            confirmed += 1
        else:
            disagreed += 1
            disagreements.append((f"SE/{eval_name}", label, note))

    print(f"\nindependent second way: {confirmed}/{total_blocks} BLOCKs confirmed, {disagreed} disagreements")
    if disagreements:
        print("DISAGREEMENTS (findings voided until resolved and logged):")
        for cid, chk, note in disagreements:
            print(f"  - {cid} / {chk}: {note}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
