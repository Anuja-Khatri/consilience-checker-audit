# consilience-checker-audit

**An independent, preregistered, receipted integrity check of the grading code behind evaluations that OpenAI publishes as open source.**

Status: in progress. Nothing here is final until `PREREGISTRATION.md` is marked FINAL and `results/REPORT.md` exists.

---

## What this is

Evaluations rest on checkers: the graders, reward functions, test suites and model judges that turn a model's output into a score. If a checker accepts an invalid answer, trusts a number the answer reports about itself, or flips its verdict on a rounding error, then a search run against it, or a decision made on it, can be wrong in a way no one sees.

This repository does one thing. It takes checkers that OpenAI has published as open code, states what each one should accept from the public task description alone, attacks each one before anyone optimises against it, and reports what holds, what breaks, and the fix. Every result is re-runnable from a receipt.

It covers two kinds of checker:
- **Deterministic graders** (code): checked with `consilience stress`.
- **Model graders** (LLM judges): checked with the judge-check method, if budget allows.

## What this is not

- It is not a bug count. A clean result on a checker that matters, reported with its coverage, is a real outcome.
- It says nothing about OpenAI's internal systems, scores, rankings or competence. Every statement is about published code at a named commit only.
- It is not a security boundary and it does not run anyone's model for them.

## How it reuses existing work

This repository is an application of the Consilience engine, not a fork of it. It depends on the published engine and reuses its method, verdict set, receipt format and verifier:

- `consilience[stress]` (the engine, from PyPI; pinned in `requirements.txt`) provides the five checks, the `PASS` / `BLOCK` / `ABSTAIN` verdicts, the receipt format, and `consilience verify`.
- The structure follows the `evaluator-stress` benchmark in [consilience-benchmarks](https://github.com/Anuja-Khatri/consilience-benchmarks).
- The model-grader leg follows the method in [consilience-judge-check](https://github.com/Anuja-Khatri/consilience-judge-check).

The pinned commits of the engine and of every audited target are in `SOURCES.yaml`.

## Layout

| Path | What it is |
|---|---|
| `STRATEGY.md` | The goal, the tests every part must pass, the scope and the rules. Read first. |
| `SPEC.md` | The technical specification: method, contracts, checks, reuse, safety, budget. |
| `PREREGISTRATION.md` | The protocol, committed before any scored run. |
| `PRODUCT_GUIDELINES.md` | The expected output format: the report and the per-checker certificate. |
| `DECISIONS.md` | Every non-trivial decision, with its reason. |
| `SOURCES.yaml` | Pinned commits of the engine and of each audited target. |
| `LABELS.yaml` | Public issues already known, so a finding that matches one is not called new. |
| `CONTRACTS.sha256` | The frozen hash of every contract and glue file, written before any run. |
| `contracts/<SET>/<slug>/` | One folder per checker: `contract.yaml`, glue, reference, vendored checker, `COVERAGE.md`. |
| `run_benchmark.py`, `check_independent.py` | The runner, and the independent second-way checker that imports nothing from the engine. |
| `research/` | The research notes behind the scope, one file per question, with sources. |
| `results/REPORT.md` | The integrity report: limits first, what holds, findings with receipts and fixes. |
| `results/certificates/` | One page per checker: scope, coverage, checks run, result, limits. |
| `results/receipts/` | Every receipt. `consilience verify` re-runs each one. |
| `VERIFICATION_LOG.md` | Every deviation, fix and re-check. |
| `CORRECTIONS.md` | Corrections after the fact. |
| `DISCLOSURE_NOTE.md` | A short note to OpenAI, one finding per entry, with receipt and patch. Anu sends it. |
| `APPLICATION_LINES.md` | Candidate one-line mentions, each true to the numbers lock. |

## AI assistance

The code and text in this repository were written with an AI coding assistant under Anuja Khatri's direction. No claim is made that any file was hand-written, hand-labelled or hand-checked by a person except where a person is named as having reviewed it.

## Disclosure

Findings concern published code at a named commit. Any finding goes to OpenAI first, through its coordinated vulnerability disclosure route, before anything is made public. All outreach is done by Anuja Khatri. This repository opens no issues, pull requests or posts on any external project.

## License

Code in this repository: MIT (see `LICENSE`), matching the Consilience engine. Any third-party checker code vendored under `contracts/*/` keeps its own license and carries a provenance header; see that file and `SOURCES.yaml`. The audited targets at their pinned commits: simple-evals is MIT; mle-bench carries its own `LICENSE`, confirmed during contract authoring.
