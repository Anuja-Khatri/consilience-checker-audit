# consilience-checker-audit

**Check the graders behind your evaluations before they mislead you.** State what a grader should accept, attack it, and get a receipt that proves what holds and what breaks.

Evaluations, leaderboards and RL reward signals all rest on *checkers*: the graders, reward functions and judges that turn a model's output into a score. When a checker accepts an invalid answer, grades by row position, trusts a number the answer reports about itself, or hands a medal to a trivially partial submission, every number built on it can be wrong and nobody sees it. This tool finds those gaps and proves each one with a counterexample anyone can re-run.

It is a reusable tool, not a one-off script: clone it, point a one-page contract at any grader, and it reports whether the grader is sound. You can run it on graders you cannot release. The graders OpenAI publishes as open code are the worked demonstration that ships with it.

It is part of **[Consilience](https://github.com/Anuja-Khatri/consilience-core)**, a deterministic verification engine (a typed input goes in, a checkable verdict comes out, with a receipt). This repository applies that discipline to eval checkers, reusing the engine's verdicts, receipts and `verify` step rather than reinventing them.

## Status and scope

Complete, verified, and reproduced from a fresh clone. It covers two kinds of checker:
- **deterministic graders** (code that scores a submission table), and
- **deterministic answer extractors** (code that reads a final answer out of a model's text response).

Checking **live model-judge graders** (LLM-as-judge, such as BrowseComp's grader) is designed and documented (`SPEC.md`, `GRADERS.md`) but **not yet run** here: it needs a judge-model API key, which was out of scope for this pass. Everything shipped is deterministic and costs nothing to run.

## Results at a glance (the OpenAI demonstration)

Full report, limits first: **[`results/REPORT.md`](results/REPORT.md)**.

- **MLE-bench system-card graders (30):** **23 hold on every check**, 6 break, 1 could not be run by this harness.
- **simple-evals answer extractors (3):** all 3 break, each confirming an already-filed issue.
- **10 findings total:** 3 look new (not found in the public trackers), 7 confirm issues others already filed (cited, not claimed new).
- **Every finding was confirmed a second independent way** (17 of 17, zero disagreements), and the whole run reproduces from a fresh clone at **$0**.

A clean result is a real result: "23 of 30 graders hold, with the coverage stated" is the headline, not a bug count.

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

Answer extractors (`src/extract_check.py`), the deterministic code that reads a final answer out of a model's text response: crafted probes at known validity test extraction leniency and brittleness (hedges, substring matches, sign and locale parsing, first-vs-final answer). Checking a *live* LLM judge is the designed-but-not-yet-run extension noted above.

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
