# consilience-checker-audit

**A reusable tool for checker-integrity audits: state what a grader should accept, attack it before anyone optimises against it, and get a receipt. Deterministic graders and model-judge extractors. The evaluations OpenAI publishes as open code are the first demonstration.**

This is a generic Consilience capability, not a one-off script. Anyone can clone it and run it on their own checkers, including ones they cannot release. OpenAI's public eval graders are the worked example that ships with it.

Status: the suite, the OpenAI demonstration, and the report are complete. See `results/REPORT.md`.

---

## What a checker is, and why audit it

Evaluations rest on checkers: the graders, reward functions, test suites and model judges that turn a model's output into a score. If a checker accepts an invalid answer, trusts a number the answer reports about itself, grades by row position, or flips its verdict on a rounding error, then a search run against it, or a safety decision made on it, can be wrong in a way no one sees. This tool finds those gaps and proves each one with a re-runnable receipt.

## Quick start (clone and run)

```bash
git clone https://github.com/Anuja-Khatri/consilience-checker-audit
cd consilience-checker-audit
python -m venv .venv && . .venv/bin/activate
pip install -e .            # or: pip install -r requirements.txt

checker-audit run-all       # run every contract, write receipts
checker-audit verify        # independent second-way verification
checker-audit report        # numbers lock, certificates, coverage
```

No install needed either: `python cli.py run-all` works from a clone.

To reproduce the OpenAI demonstration you also need the two target repos cloned at the pinned commits in `SOURCES.yaml`, and the engine pinned in `requirements.txt`. A fresh-clone reproduction is in `results/REPORT.md`.

## Check your own grader

Point a contract at any `grade(submission, answers)` function. Nothing about the tool is OpenAI-specific. See the worked example in `examples/byo_grader/` and the guide in `GRADERS.md`.

```yaml
# a contract for your own grader
harness:
  kind: callable
  grade: "path/to/your_grader.py:grade"
id_column: id
prediction_columns: [pred]
metric: { direction: higher_better }
answers: { id: [1,2,3,4,5], columns: { label: [0,1,0,1,1], pred: [0,1,0,1,1] } }
leaderboard: [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
reference: { kind: exact }
checks: [order_invariance, reject_wrong_length, reject_duplicate_ids]
```

```bash
checker-audit run examples/byo_grader/contract.yaml
# example-byo-accuracy: BREAKS   (order_invariance: positional grading ignores the id column)
```

## The checks

Deterministic graders (`src/mleb_check.py`, harness `mlebench` or `callable`):
- **reject_nonfinite** — NaN or infinite predictions accepted and winning a medal.
- **order_invariance** — the same submission in a different row order scores differently.
- **reject_wrong_length** — a short submission accepted and winning a medal.
- **reject_duplicate_ids** — a duplicate id accepted and changing the score.
- **range** — an out-of-range prediction accepted and winning a medal.
- **no_free_gold_subset_perfect** — a submission perfect on one aggregation group only winning a medal.

Model-judge answer extractors (`src/extract_check.py`): crafted probes at known validity test extraction leniency and brittleness (hedges, substring matches, sign and locale parsing, first-vs-final answer).

Every run writes a receipt (verdict, counterexample, input hashes). `check_independent.py` re-derives every finding a second way, importing nothing from the checker. `src/build_report.py` locks the numbers and writes one certificate per checker.

## How it reuses the Consilience engine

This repository is an application of the Consilience method, not a fork. It reuses the engine's `PASS` / `BLOCK` / `ABSTAIN` verdicts, the receipt and `verify` discipline, the independent second way, the numbers lock and the preregistration discipline. The pilot showed that the `consilience stress` attack generator does not cover tabular-grader or text-extractor flaws, so the tool adds those checks and files them upstream as a proposed engine capability (`research/06-proposed-engine-capability.md`). It depends on `consilience[stress]` and does not reimplement any check the engine already has.

## The OpenAI demonstration

The suite is run on the graders behind evaluations OpenAI publishes:
- **MLE-bench** system-card subset (30 competition graders in `experiments/splits/systemcard.txt`), reported under AI self-improvement in OpenAI system cards.
- **simple-evals** deterministic answer extractors (DROP, MGSM, MMLU).

Results, limits first, are in `results/REPORT.md`, with a certificate per checker in `results/certificates/` and a receipt per checker in `results/receipts/`. Findings that match an already-filed public issue are reported as confirmations with their citation (`LABELS.yaml`); candidate-new findings are marked as such.

## Layout

| Path | What it is |
|---|---|
| `STRATEGY.md`, `SPEC.md`, `PRODUCT_GUIDELINES.md` | The goal, the method, the output format. |
| `PREREGISTRATION.md` | The protocol, committed before any scored run. |
| `GRADERS.md` | How to write a contract for your own grader. |
| `cli.py`, `src/` | The tool. |
| `contracts/MLEB/`, `contracts/SE/` | One contract per checker (the OpenAI demonstration). |
| `examples/byo_grader/` | A non-OpenAI worked example. |
| `check_independent.py` | The independent second-way verifier. |
| `results/REPORT.md`, `results/certificates/`, `results/receipts/` | Report, certificates, receipts. |
| `results/numbers.lock.yaml` | Every public number with its n. |
| `DISCLOSURE_NOTE.md`, `APPLICATION_LINES.md` | The maintainer note (Anu sends it) and the application lines. |
| `VERIFICATION_LOG.md`, `CORRECTIONS.md`, `DECISIONS.md` | Deviations, corrections, decisions. |

## AI assistance

The code and text in this repository were written with an AI coding assistant under Anuja Khatri's direction. No claim is made that any file was hand-written, hand-labelled or hand-checked by a person except where a person is named as having reviewed it.

## Disclosure

Findings concern published code at a named commit. Any finding goes to the maintainers first, before anything is made public; a grader-correctness bug is an ordinary bug, not a security vulnerability (see `research/01-system-cards.md`). All outreach is done by Anuja Khatri. This repository opens no issues, pull requests or posts on any external project.

## License

MIT (see `LICENSE`), matching the Consilience engine. Third-party checker code vendored under `contracts/*/` keeps its own license and carries a provenance header; see `SOURCES.yaml`.
