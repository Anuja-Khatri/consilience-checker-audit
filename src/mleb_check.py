"""mleb_check: a reusable, contract-driven integrity checker for MLE-bench graders.

It reuses the Consilience verdict set (PASS / BLOCK / ABSTAIN), the receipt
discipline (hash the inputs, store each counterexample, make every verdict
re-checkable) and the independent-second-way discipline. It is not the
consilience stress attack generator: the pilot (VERIFICATION_LOG.md, D12)
showed that stress's attacks do not cover tabular-submission-grader flaws.
A "tabular submission grader" harness is filed as a proposed engine
capability in research/06-proposed-engine-capability.md.

The grader code under test is the real, unmodified published code at the
pinned commit. mlebench.utils is stubbed (logging and import_fn only) to
avoid data-prep dependencies the graders do not use; the grading logic
(grade_helpers.py and each competition's grade.py) is the published code.

Usage:
    python -I src/mleb_check.py contracts/MLEB/<id>/contract.yaml --out results/receipts/MLEB/<id>
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import logging
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

DEFAULT_MLEB_ROOT = "/home/user/openai-targets/mle-bench"
ROOT = Path(__file__).resolve().parent.parent

PASS, BLOCK, ABSTAIN = "PASS", "BLOCK", "ABSTAIN"


# --------------------------------------------------------------------------- #
# Loading the real grader with a stubbed mlebench.utils                        #
# --------------------------------------------------------------------------- #
def _install_mlebench(mleb_root: str):
    """Make `mlebench.grade_helpers` importable using the real file, with a
    stubbed `mlebench.utils` (logging + import_fn only). Returns (Grader,
    InvalidSubmissionError, grade_helpers_path)."""
    import importlib
    import importlib.util

    if "mlebench.grade_helpers" in sys.modules:
        gh = sys.modules["mlebench.grade_helpers"]
        return gh.Grader, gh.InvalidSubmissionError, Path(mleb_root) / "mlebench" / "grade_helpers.py"

    pkg = types.ModuleType("mlebench")
    pkg.__path__ = [str(Path(mleb_root) / "mlebench")]
    sys.modules["mlebench"] = pkg

    utils = types.ModuleType("mlebench.utils")
    utils.get_logger = lambda name, level=logging.INFO, filename=None: logging.getLogger(name)

    def import_fn(s):
        m, f = s.split(":")
        return getattr(importlib.import_module(m), f)

    utils.import_fn = import_fn
    sys.modules["mlebench.utils"] = utils

    gh_path = Path(mleb_root) / "mlebench" / "grade_helpers.py"
    spec = importlib.util.spec_from_file_location("mlebench.grade_helpers", gh_path)
    gh = importlib.util.module_from_spec(spec)
    sys.modules["mlebench.grade_helpers"] = gh
    spec.loader.exec_module(gh)
    return gh.Grader, gh.InvalidSubmissionError, gh_path


def _load_grade_fn(mleb_root: str, grade_rel_path: str):
    import importlib.util

    path = Path(mleb_root) / grade_rel_path
    comp_dir = path.parent
    # Load grade.py inside a package context so relative imports in the real grader
    # (e.g. `from .vocabulary import ...`, `from .notebook import ...`) resolve to the
    # sibling files in the competition directory.
    pkgname = "mleb_comp_" + comp_dir.name.replace("-", "_").replace(".", "_")
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
    return mod.grade, path


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# Pluggable grader adapter: bring your own grader (not OpenAI-specific).        #
# A grader object exposes __call__(submission, answers) -> score|None and       #
# rank_score(score, leaderboard_df) -> {gold_medal, silver_medal, bronze_medal, #
# above_median}. The mlebench harness uses the real mle-bench Grader; the        #
# callable harness wraps any user grade(submission, answers) function.          #
# --------------------------------------------------------------------------- #
class CallableGrader:
    """Adapter for any user grade(submission_df, answers_df) -> float function.
    An exception on a submission counts as a rejection (returns None), the same
    convention consilience stress uses. Medals are assigned from a leaderboard by
    the standard Kaggle percentile rule."""

    def __init__(self, grade_fn, lower_better: bool, round_ndigits=None):
        self.grade_fn = grade_fn
        self.lower_better = lower_better
        self.round_ndigits = round_ndigits

    def __call__(self, submission, answers):
        try:
            score = self.grade_fn(submission, answers)
        except Exception:
            return None
        if score is None:
            return None
        try:
            score = float(score)
        except (TypeError, ValueError):
            return None
        return round(score, self.round_ndigits) if self.round_ndigits is not None else score

    def rank_score(self, score, leaderboard):
        scores = [float(s) for s in leaderboard["score"].tolist()]
        n = len(scores)
        ordered = sorted(scores, reverse=not self.lower_better)  # best first

        def at(pos):
            return ordered[min(max(pos - 1, 0), n - 1)]

        gold_t, silver_t, bronze_t = at(max(1, int(n * 0.1))), at(max(1, int(n * 0.2))), at(max(1, int(n * 0.4)))
        better = (lambda a, b: a <= b) if self.lower_better else (lambda a, b: a >= b)
        gold = better(score, gold_t)
        silver = (not gold) and better(score, silver_t)
        bronze = (not gold) and (not silver) and better(score, bronze_t)
        med = sorted(scores)[n // 2] if n else 0.0
        above = (score < med) if self.lower_better else (score > med)
        return {"gold_medal": gold, "silver_medal": silver, "bronze_medal": bronze, "above_median": above}


def _import_callable(spec_str: str):
    """Load a grade function from 'module:function' or 'path/to/file.py:function'."""
    mod_part, fn_name = spec_str.rsplit(":", 1)
    if mod_part.endswith(".py") or "/" in mod_part:
        path = Path(mod_part)
        if not path.is_absolute():
            path = (ROOT / mod_part).resolve()
        spec = importlib.util.spec_from_file_location("byo_grader_" + path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, fn_name), path
    mod = importlib.import_module(mod_part)
    return getattr(mod, fn_name), (Path(mod.__file__) if getattr(mod, "__file__", None) else None)


# --------------------------------------------------------------------------- #
# Building synthetic data from the contract                                    #
# --------------------------------------------------------------------------- #
def build_answers(contract) -> pd.DataFrame:
    a = contract["answers"]
    data = {contract["id_column"]: list(a["id"])} if contract.get("id_column") else {}
    for col, vals in a["columns"].items():
        data[col] = list(vals)
    return pd.DataFrame(data)


def build_leaderboard(contract) -> pd.DataFrame:
    return pd.DataFrame({"score": list(contract["leaderboard"])})


def build_reference(contract, answers) -> pd.DataFrame:
    """A valid submission. kind: 'exact' (copy answers) or 'offset' (+delta on predictions)."""
    ref = answers.copy()
    spec = contract.get("reference", {"kind": "exact"})
    if spec["kind"] == "offset":
        for col in contract["prediction_columns"]:
            ref[col] = answers[col].astype(float) + float(spec.get("offset", 1.0))
    return _submission_columns(contract, ref)


def _submission_columns(contract, df) -> pd.DataFrame:
    """Keep only the columns a real submission carries: id + prediction columns
    (+ any extra columns the grader reads, e.g. a 'type' column)."""
    cols = []
    if contract.get("id_column"):
        cols.append(contract["id_column"])
    cols += list(contract["prediction_columns"])
    cols += list(contract.get("submission_extra_columns", []))
    return df[cols].copy()


def _medal(grader, score, leaderboard):
    if score is None:
        return "none"
    r = grader.rank_score(score, leaderboard)
    for m in ("gold_medal", "silver_medal", "bronze_medal"):
        if r[m]:
            return m.replace("_medal", "")
    return "above_median" if r["above_median"] else "none"


def _to_jsonable(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="list")
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return str(obj)
    return obj


# --------------------------------------------------------------------------- #
# Checks. Each returns (verdict, detail, counterexample_or_None).              #
# --------------------------------------------------------------------------- #
def check_reject_nonfinite(ctx):
    grader, answers, lb, ref, contract = ctx
    pcols = contract["prediction_columns"]
    try:
        ref[pcols[0]].astype(float)
    except (TypeError, ValueError):
        return ABSTAIN, f"prediction column {pcols[0]!r} is not numeric; non-finite attack not applicable", None
    worst = PASS
    details, cex = [], None
    for val, label in [(np.nan, "NaN"), (np.inf, "+inf"), (-np.inf, "-inf")]:
        sub = ref.copy()
        sub[pcols[0]] = sub[pcols[0]].astype(float)  # allow setting non-finite into an int-typed column
        sub.loc[sub.index[0], pcols[0]] = val
        score = grader(sub, answers)
        medal = _medal(grader, score, lb)
        got_medal = medal in ("gold", "silver", "bronze")
        details.append(f"{label}: score={score!r}, medal={medal}")
        if score is not None and got_medal:
            worst = BLOCK
            cex = {"attack": f"{label} in {pcols[0]}[0]", "submission": _to_jsonable(sub),
                   "observed_score": _to_jsonable(score), "observed_medal": medal}
    return worst, "; ".join(details), cex


def check_order_invariance(ctx):
    grader, answers, lb, ref, contract = ctx
    if not contract.get("id_column"):
        return ABSTAIN, "no id column declared; row order is inherently meaningful", None
    base = grader(ref, answers)
    shuf = ref.sample(frac=1.0, random_state=1).reset_index(drop=True)
    score = grader(shuf, answers)
    if base is None:
        return ABSTAIN, "reference did not score", None
    if score is None or not np.isclose(float(score), float(base), rtol=1e-9, atol=1e-12):
        cex = {"attack": "same submission, rows shuffled (id->value preserved)",
               "submission": _to_jsonable(shuf), "reference_submission": _to_jsonable(ref),
               "reference_score": _to_jsonable(base),
               "observed_score": _to_jsonable(score), "observed_medal": _medal(grader, score, lb)}
        return BLOCK, f"reference score {base} changed to {score} under a row permutation", cex
    return PASS, f"score unchanged ({base}) under row permutation", None


def check_reject_wrong_length(ctx):
    grader, answers, lb, ref, contract = ctx
    sub = ref.iloc[:-1].copy()
    score = grader(sub, answers)
    medal = _medal(grader, score, lb)
    if score is None:
        return PASS, f"short submission ({len(sub)} of {len(ref)} rows) rejected", None
    cex = {"attack": f"short submission ({len(sub)} of {len(ref)} rows)",
           "submission": _to_jsonable(sub), "observed_score": _to_jsonable(score), "observed_medal": medal}
    verdict = BLOCK if medal in ("gold", "silver", "bronze") else PASS
    note = "accepted" + (f" and won a {medal}" if verdict == BLOCK else " but won no medal")
    return verdict, f"short submission {note} (score={score})", (cex if verdict == BLOCK else None)


def check_reject_duplicate_ids(ctx):
    grader, answers, lb, ref, contract = ctx
    if not contract.get("id_column"):
        return ABSTAIN, "no id column declared", None
    base = grader(ref, answers)
    # Duplicate the first id row, with a perturbed prediction, so a grader that
    # de-duplicates or rejects is distinguished from one that lets the duplicate
    # change the score (the merge-inflation behaviour behind issue #156).
    dup_row = ref.iloc[[0]].copy()
    for col in contract["prediction_columns"]:
        try:
            dup_row.loc[dup_row.index[0], col] = float(dup_row.iloc[0][col]) + 1000.0
        except (TypeError, ValueError):
            pass  # non-numeric prediction (e.g. an id list or RLE string): duplicate the row as-is;
                  # the duplicated id itself is the attack, regardless of the value.
    sub = pd.concat([ref, dup_row], ignore_index=True)
    score = grader(sub, answers)
    medal = _medal(grader, score, lb)
    if score is None:
        return PASS, "submission with a duplicate id rejected", None
    changed = base is None or not np.isclose(float(score), float(base), rtol=1e-9, atol=1e-12)
    verdict = BLOCK if (medal in ("gold", "silver", "bronze") or changed) else PASS
    cex = {"attack": "one duplicated id row with a perturbed prediction", "submission": _to_jsonable(sub),
           "reference_score": _to_jsonable(base), "observed_score": _to_jsonable(score), "observed_medal": medal}
    return verdict, f"duplicate id accepted (score={score}, medal={medal}, changed={changed})", (cex if verdict == BLOCK else None)


def check_range(ctx):
    grader, answers, lb, ref, contract = ctx
    rng = contract.get("prediction_range")
    if not rng:
        return ABSTAIN, "no prediction range declared for this metric", None
    pcols = contract["prediction_columns"]
    lo, hi = rng
    out = ref.copy()
    bad = (hi + 1000.0) if hi is not None else 1e9
    out.loc[out.index[0], pcols[0]] = bad
    score = grader(out, answers)
    medal = _medal(grader, score, lb)
    if score is None:
        return PASS, f"out-of-range value {bad} rejected", None
    verdict = BLOCK if medal in ("gold", "silver", "bronze") else PASS
    cex = {"attack": f"out-of-range value {bad} in {pcols[0]}[0]", "submission": _to_jsonable(out),
           "observed_score": _to_jsonable(score), "observed_medal": medal}
    return verdict, f"out-of-range value accepted (score={score}, medal={medal})", (cex if verdict == BLOCK else None)


def check_no_free_gold_subset_perfect(ctx):
    """A submission perfect on ONE aggregation group only, garbage elsewhere.
    BLOCK if it wins a medal (the champs log-MAE case)."""
    grader, answers, lb, ref, contract = ctx
    grp = contract.get("group_column")
    if not grp or grp not in answers.columns:
        return ABSTAIN, "no aggregation group column declared", None
    pcols = contract["prediction_columns"]
    groups = list(dict.fromkeys(answers[grp].tolist()))
    if len(groups) < 2:
        return ABSTAIN, "need at least two aggregation groups", None
    perfect_group = groups[0]
    # exact predictions on the first group, garbage on the rest
    sub = answers.copy()
    mask = sub[grp] != perfect_group
    for col in pcols:
        sub.loc[mask, col] = 10.0 ** 6
    sub = _submission_columns(contract, sub)
    score = grader(sub, answers)
    medal = _medal(grader, score, lb)
    if score is not None and medal in ("gold", "silver", "bronze"):
        cex = {"attack": f"exact on group {perfect_group!r}, garbage on the rest",
               "submission": _to_jsonable(sub), "observed_score": _to_jsonable(score), "observed_medal": medal}
        return BLOCK, f"a submission perfect on one group only won a {medal} (score={score})", cex
    return PASS, f"partial-perfect submission won no medal (score={score}, medal={medal})", None


CHECKS = {
    "reject_nonfinite": check_reject_nonfinite,
    "order_invariance": check_order_invariance,
    "reject_wrong_length": check_reject_wrong_length,
    "reject_duplicate_ids": check_reject_duplicate_ids,
    "range": check_range,
    "no_free_gold_subset_perfect": check_no_free_gold_subset_perfect,
}


# --------------------------------------------------------------------------- #
# Runner                                                                       #
# --------------------------------------------------------------------------- #
def run_contract(contract_path: str, mleb_root: str = DEFAULT_MLEB_ROOT) -> dict:
    contract_path = Path(contract_path)
    contract = yaml.safe_load(contract_path.read_text())

    harness = contract.get("harness", {"kind": "mlebench"})
    kind = harness.get("kind", "mlebench")
    if kind == "mlebench":
        # The OpenAI demonstration: run the real mle-bench Grader + rank_score pipeline.
        Grader, _InvalidSubmissionError, gh_path = _install_mlebench(mleb_root)
        grade_fn, grade_path = _load_grade_fn(mleb_root, contract["source"]["grade_path"])
        grader = Grader(name=contract["competition_id"], grade_fn="builtins:len")
        grader.grade_fn = grade_fn  # the real published grade function
        source_hashes = {"grade_file_sha256": _sha256(grade_path), "grade_helpers_sha256": _sha256(gh_path)}
    elif kind == "callable":
        # Bring your own grader: any grade(submission_df, answers_df) -> float.
        grade_fn, grade_path = _import_callable(harness["grade"])
        lower_better = contract.get("metric", {}).get("direction", "lower_better") == "lower_better"
        grader = CallableGrader(grade_fn, lower_better=lower_better, round_ndigits=harness.get("round"))
        source_hashes = {"grade_file_sha256": _sha256(grade_path) if grade_path else None}
    else:
        raise ValueError(f"unknown harness kind: {kind!r} (use 'mlebench' or 'callable')")

    answers = build_answers(contract)
    leaderboard = build_leaderboard(contract)
    reference = build_reference(contract, answers)

    ref_score = grader(reference, answers)
    ctx = (grader, answers, leaderboard, reference, contract)

    results = []
    verdict_rank = {PASS: 0, ABSTAIN: 0, BLOCK: 1}
    worst = PASS
    if ref_score is None:
        # The grader rejected the declared-valid reference submission, so the
        # checks cannot be exercised. The contract is unrunnable as written.
        overall = "ABSTAIN"
        results.append({"check": "reference", "verdict": ABSTAIN,
                        "detail": "reference_rejected: the grader returned None on the declared-valid "
                                  "reference submission; the contract cannot be exercised as written",
                        "counterexample": None})
    else:
        for name in contract["checks"]:
            fn = CHECKS.get(name)
            if fn is None:
                results.append({"check": name, "verdict": ABSTAIN, "detail": "unknown check", "counterexample": None})
                continue
            v, detail, cex = fn(copy.copy(ctx))
            results.append({"check": name, "verdict": v, "detail": detail, "counterexample": cex})
            if verdict_rank[v] > verdict_rank[worst]:
                worst = v
        any_abstain = any(r["verdict"] == ABSTAIN for r in results)
        overall = "BREAKS" if worst == BLOCK else ("PARTIAL" if any_abstain else "HOLDS")

    receipt = {
        "kind": "mleb-grader-check/v1",
        "engine": "consilience-checker-audit mleb_check; reuses the consilience PASS/BLOCK/ABSTAIN verdict set and receipt discipline",
        "competition_id": contract["competition_id"],
        "source": contract["source"],
        "contract_author": contract.get("contract_author", "model"),
        "id_column": contract.get("id_column"),
        "prediction_columns": contract.get("prediction_columns"),
        "group_column": contract.get("group_column"),
        "prediction_range": contract.get("prediction_range"),
        "contract_sha256": _sha256(contract_path),
        "harness_kind": kind,
        **source_hashes,
        "seed": 0,
        "synthetic_answers": _to_jsonable(answers),
        "synthetic_leaderboard": list(contract["leaderboard"]),
        "reference_score": _to_jsonable(ref_score),
        "checks": results,
        "verdict": overall,
        "labels": contract.get("labels", []),
        "limits": "Synthetic answers test the grader's validation and arithmetic, not real Kaggle data. "
                  "A HOLDS is evidence on the checks run, not a proof of correctness.",
        "created": datetime.now(timezone.utc).isoformat(),
    }
    return receipt


def main():
    ap = argparse.ArgumentParser(description="Run an MLE-bench grader contract.")
    ap.add_argument("contract")
    ap.add_argument("--out", help="directory to write receipt.json")
    ap.add_argument("--mleb-root", default=DEFAULT_MLEB_ROOT)
    ap.add_argument("--json", action="store_true", help="print the receipt as JSON")
    args = ap.parse_args()

    receipt = run_contract(args.contract, mleb_root=args.mleb_root)

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    if args.json or not args.out:
        print(json.dumps(receipt, indent=2, default=str))

    verdict = receipt["verdict"]
    print(f"\n{receipt['competition_id']}: {verdict}", file=sys.stderr)
    for r in receipt["checks"]:
        print(f"  {r['check']:34s} {r['verdict']:8s} {r['detail']}", file=sys.stderr)
    sys.exit(1 if verdict == "BREAKS" else 0)


if __name__ == "__main__":
    main()
