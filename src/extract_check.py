"""extract_check: a contract-driven checker for simple-evals answer extractors.

simple-evals extractors take a model's text response and a gold answer and
return correct or incorrect. The consilience stress engine models numeric
constructions, not text, so this leg uses a small checker in the engine's
verdict vocabulary (PASS / BLOCK / ABSTAIN) and receipt discipline.

The extractor code under test is vendored verbatim from simple-evals at the
pinned commit, with a provenance header, in each contract's extractor.py. A
thin decide() in that file replicates the eval's own scoring lines, so the
real, unmodified logic decides correctness.

A probe is a crafted (response, gold, expect_correct) case drawn from the
task's answer format. A BLOCK is raised when the extractor disagrees with the
contract: it marks correct an answer the task rules out (leniency), or marks
wrong an answer that is clearly correct (brittleness). Most findings here
confirm already-filed issues (see LABELS.yaml) and are reported as such.

Usage:
    python -I src/extract_check.py contracts/SE/<eval>/contract.yaml --out results/receipts/SE/<eval>
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

PASS, BLOCK, ABSTAIN = "PASS", "BLOCK", "ABSTAIN"


def _sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_extractor(contract_dir: Path):
    path = contract_dir / "extractor.py"
    spec = importlib.util.spec_from_file_location("se_extractor_" + contract_dir.name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


def run_contract(contract_path: str) -> dict:
    contract_path = Path(contract_path)
    contract = yaml.safe_load(contract_path.read_text())
    extractor, extractor_path = _load_extractor(contract_path.parent)

    results = []
    worst = PASS
    for probe in contract["probes"]:
        observed = bool(extractor.decide(probe["response"], probe["gold"]))
        expected = bool(probe["expect_correct"])
        if observed == expected:
            verdict, kind = PASS, "as expected"
        elif observed and not expected:
            verdict, kind = BLOCK, "leniency: a wrong/invalid answer marked correct"
            worst = BLOCK
        else:
            verdict, kind = BLOCK, "brittleness: a correct answer marked wrong"
            worst = BLOCK
        results.append({
            "label": probe["label"], "verdict": verdict, "kind": kind,
            "response": probe["response"], "gold": probe["gold"],
            "expected_correct": expected, "observed_correct": observed,
        })

    overall = "BREAKS" if worst == BLOCK else "HOLDS"
    receipt = {
        "kind": "se-extractor-check/v1",
        "engine": "consilience-checker-audit extract_check; reuses the consilience PASS/BLOCK/ABSTAIN verdict set and receipt discipline",
        "eval": contract["eval"],
        "source": contract["source"],
        "contract_author": contract.get("contract_author", "model"),
        "contract_sha256": _sha256(contract_path),
        "extractor_sha256": _sha256(extractor_path),
        "probes": results,
        "verdict": overall,
        "labels": contract.get("labels", []),
        "limits": "Probes are crafted from the task's answer format; they test the extractor's "
                  "decision logic, not a full run on the eval's dataset. Most findings confirm "
                  "already-filed issues cited in labels.",
        "created": datetime.now(timezone.utc).isoformat(),
    }
    return receipt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("contract")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    receipt = run_contract(args.contract)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    if args.json or not args.out:
        print(json.dumps(receipt, indent=2, default=str))
    print(f"\n{receipt['eval']}: {receipt['verdict']}", file=sys.stderr)
    for r in receipt["probes"]:
        print(f"  {r['verdict']:6s} {r['label']}: expected={r['expected_correct']} observed={r['observed_correct']} ({r['kind']})", file=sys.stderr)
    sys.exit(1 if receipt["verdict"] == "BREAKS" else 0)


if __name__ == "__main__":
    main()
