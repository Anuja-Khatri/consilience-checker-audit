# Strategy: the checker-audit build

Read this first. It holds the goal, the tests every part must pass, the scope, and the rules. It is the fixed reference so that no later session drifts from the goal. `SPEC.md` says how; this says what and why.

Written 2026-11-27. Autonomous build; decisions are logged in `DECISIONS.md`.

---

## 1. The goal, in one sentence

Take the graders behind the evaluations OpenAI publishes as open code, state what each one should accept, attack each one before anyone optimises against it, and report what holds, what breaks, and the fix, all re-runnable from receipts.

Said to the reader at the OpenAI Foundation: "I took the graders behind the evals in your own system cards, stated what each one should accept, attacked them before anyone optimises against them, and here is what holds, what breaks, and the fix, all re-runnable from receipts."

## 2. Why this build exists

Evaluations rest on checkers. The security of those checkers is the thing most often left unexamined, and the place where a reward hack or a fake record starts. A small, careful, receipted audit of OpenAI's own public eval checkers is a work sample that shows the method working at small scale on the reader's own instruments.

What success is: a clean method applied honestly, with coverage stated, on checkers that matter. A clean result is a real result. The integrity of the method is the work sample, not a count of bugs. Do not stretch to manufacture findings.

## 3. What is built, as a product

Three things, in one repository:
1. **A reusable suite.** One contract per checker, the five stress checks, judge tests for model graders, an independent second checker, receipts, and a report generator. It can be pointed at another evaluation next week.
2. **A benchmark of OpenAI's eval checkers.** A frozen set of contracts for named checkers at pinned commits, so the result can be re-run and compared when the checkers change.
3. **An evaluation report.** Limits first, what holds first, then findings, each confirmed a second way, each with a proposed fix and its receipt.

## 4. The tests every part must pass

Adapted from the eight tests in the Consilience build guide. Check each before writing code, and again before reporting.

| # | Test | Fails if |
|---|---|---|
| T1 | **It reuses the engine.** It depends on `consilience[stress]`, uses the engine's verdict set (`PASS` / `BLOCK` / `ABSTAIN`), its receipt format, and `consilience verify` re-runs its receipts. | It invents its own verdicts or receipts, or reimplements the checks. |
| T2 | **It is generic.** The suite works on any checker of its kind. An OpenAI checker is one demonstration; the contract format is not special-cased to one repository. | The runner only understands one grader's file layout. |
| T3 | **Anyone can re-run it.** One install, one command per contract, a receipt that `consilience verify` re-checks, and a fresh-clone run that reproduces the receipt hashes. | A result exists only as a claim in prose. |
| T4 | **It is on OpenAI's own instruments.** Priority to checkers behind evals named in OpenAI system cards, then OpenAI's other open eval repos. | It audits a checker OpenAI does not use or publish. |
| T5 | **It reads as help, not attack.** Limits and what holds are reported as prominently as what breaks. Every finding carries a minimal fix and a check that valid submissions still pass. Findings go to OpenAI first. | The headline is a list of mistakes, or a finding ships with no fix. |
| T6 | **It is honest in the house style.** Preregistration committed before runs, numbers locked with their n, independent second way, receipts that verify, limits first, corrections file, AI assistance disclosed. | Any number not verified a second way, or a run before the preregistration is final. |
| T7 | **It covers both kinds of checker.** Deterministic graders (code) and model graders (LLM judges), as far as budget allows, with the model-grader leg marked honestly if it is blocked. | It silently drops the model-grader kind without saying so. |
| T8 | **It is cheap and says so.** Wall-clock time and dollars per checker are reported. Cheapness is part of the argument that the method scales. | Cost and time are not measured. |

Stop rule: if, after honest work, no checker in scope can be audited to this standard, say so plainly in the report. A clean "nothing broke, here is the coverage" is an acceptable and honest outcome. A build that fails T1 to T8 is not.

## 5. Scope

The scope is locked in `PREREGISTRATION.md` after the research in `research/` is complete. The default core, subject to the research confirming public availability, licences, and that prior audits have not already covered the same per-grader layer:

- **Leg A, deterministic, MLE-bench system-card subset.** The graders for the competitions in `experiments/splits/systemcard.txt`, plus the shared helpers in `mlebench/grade_helpers.py`. MLE-bench is reported under AI self-improvement in OpenAI system cards.
- **Leg B, deterministic, simple-evals answer extraction.** The answer extractors for MMLU, GPQA, MATH, MGSM and DROP. Deterministic, no API calls, cheap.
- **Leg C, model graders, conditional.** The BrowseComp numeric-margin grader and, if enough numeric criteria exist, the HealthBench rubric grader, by the judge-check method. Runs only if an API key is provided; otherwise marked "blocked, not measured".

Prior audits are cited, not repeated. Where a finding matches a public issue listed in `LABELS.yaml`, it is reported as "not new".

## 6. Rules, non-negotiable

- **Honesty.** Statements concern published code at a named commit only. Nothing is implied about OpenAI's internal systems, scores, rankings or competence. A clean result is reported as clean, with coverage.
- **No contact.** This repository opens no issues, pull requests, emails or posts on any external project or channel. Anu does all outreach.
- **Disclosure first.** Findings go to OpenAI, through its coordinated vulnerability disclosure route, before anything is public.
- **AI assistance disclosed.** Every README and report states the code and text were written with an AI coding assistant under Anu's direction. No claim that Anu personally coded, labelled or hand-checked anything.
- **Numbers.** Every number carries its n and qualifier, and comes from the numbers lock.
- **Writing.** Plain short sentences. No em dashes. No hype. Limits first.
- **Isolation.** Third-party target code is cloned outside this repository, read for contracts, vendored per file with a provenance header, and run only in an isolated environment. No model identifier appears in any committed file.
- **Autonomy.** No yes/no questions to Anu. Every non-trivial decision is logged in `DECISIONS.md` with its reason.

## 7. Phases

| Phase | What | Exit |
|---|---|---|
| 0 | Isolated workspace; reuse repos and targets cloned at pinned commits; repo scaffold. | Workspace ready, commits pinned. |
| 1 | Research (system cards, prior audits, grader inspection, feasibility, product format). | `research/` complete; scope decided. |
| 2 | `SPEC.md`, `PRODUCT_GUIDELINES.md`, `PREREGISTRATION.md` final, `SOURCES.yaml`, `LABELS.yaml`. | Preregistration FINAL; contracts frozen next. |
| 3 | Contracts and glue for 3 pilot checkers; wire the runner to the engine; confirm the harness fits or decide the adapter. | Pilot verdicts stable. |
| 4 | All in-scope contracts; `CONTRACTS.sha256` frozen; full runs; independent checker; receipts; fresh-clone verification; numbers lock. | All receipts verify. |
| 5 | Fix proposals; certificates; `results/REPORT.md`; `DISCLOSURE_NOTE.md`; `APPLICATION_LINES.md`. | Deliverables complete. |
