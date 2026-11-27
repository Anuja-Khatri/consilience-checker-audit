#!/usr/bin/env python3
"""checker-audit: a command-line tool for checker-integrity audits.

Clone the repo, then:
    python cli.py run-all          # run every contract, write receipts
    python cli.py verify           # independent second-way verification
    python cli.py report           # numbers lock, certificates, coverage
    python cli.py run <contract>   # run a single contract

Check your OWN grader: write a contract with `harness: {kind: callable, grade: "path.py:fn"}`
(see examples/byo_grader/) and run it with `python cli.py run <contract>`.
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import mleb_check  # noqa: E402
import extract_check  # noqa: E402
import build_report  # noqa: E402
import yaml  # noqa: E402


def _kind(path):
    return yaml.safe_load(Path(path).read_text()).get("kind")


def _run_one(contract, out_dir=None, mleb_root=mleb_check.DEFAULT_MLEB_ROOT):
    if _kind(contract) == "se-extractor-contract":
        receipt = extract_check.run_contract(contract)
    else:
        receipt = mleb_check.run_contract(contract, mleb_root=mleb_root)
    if out_dir:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    return receipt


def cmd_run(args):
    r = _run_one(args.contract, args.out, args.mleb_root)
    print(json.dumps(r, indent=2, default=str))
    print(f"\n{r.get('competition_id') or r.get('eval')}: {r['verdict']}", file=sys.stderr)
    sys.exit(1 if r["verdict"] == "BREAKS" else 0)


def cmd_run_all(args):
    rows = []
    for c in sorted(glob.glob(str(ROOT / "contracts/MLEB/*/contract.yaml"))):
        cid = Path(c).parent.name
        try:
            r = _run_one(c, ROOT / "results/receipts/MLEB" / cid, args.mleb_root)
            rows.append((cid, r["verdict"]))
        except Exception as e:
            rows.append((cid, f"ERROR: {type(e).__name__}"))
    for c in sorted(glob.glob(str(ROOT / "contracts/SE/*/contract.yaml"))):
        eid = Path(c).parent.name
        r = _run_one(c, ROOT / "results/receipts/SE" / eid)
        rows.append((f"SE/{eid}", r["verdict"]))
    holds = sum(v == "HOLDS" for _, v in rows)
    breaks = sum(v == "BREAKS" for _, v in rows)
    other = len(rows) - holds - breaks
    for cid, v in rows:
        print(f"  {v:10s} {cid}")
    print(f"\n{len(rows)} contracts: {holds} HOLDS, {breaks} BREAKS, {other} other")


def cmd_verify(args):
    cmd = [sys.executable, "-I", str(ROOT / "check_independent.py"), "--mleb-root", args.mleb_root]
    sys.exit(subprocess.call(cmd))


def cmd_report(args):
    build_report.main()


def main():
    ap = argparse.ArgumentParser(prog="checker-audit", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("run", help="run a single contract")
    pr.add_argument("contract")
    pr.add_argument("--out")
    pr.add_argument("--mleb-root", default=mleb_check.DEFAULT_MLEB_ROOT)
    pr.set_defaults(func=cmd_run)
    pa = sub.add_parser("run-all", help="run every contract and write receipts")
    pa.add_argument("--mleb-root", default=mleb_check.DEFAULT_MLEB_ROOT)
    pa.set_defaults(func=cmd_run_all)
    pv = sub.add_parser("verify", help="independent second-way verification")
    pv.add_argument("--mleb-root", default=mleb_check.DEFAULT_MLEB_ROOT)
    pv.set_defaults(func=cmd_verify)
    sub.add_parser("report", help="numbers lock + certificates").set_defaults(func=cmd_report)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
