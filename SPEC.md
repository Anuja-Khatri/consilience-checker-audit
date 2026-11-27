# Technical specification

How the build works. `STRATEGY.md` says what and why; this says how. Written 2026-11-27, after the research in `research/`. Changes after the preregistration is final are logged in `VERIFICATION_LOG.md`.

---

## 1. Relationship to the engine

This repository is an application of the Consilience engine, not a fork. It installs `consilience[stress]==0.3.0` from PyPI (pinned in `requirements.txt`) and reuses:
- the five checks and the `PASS` / `BLOCK` / `ABSTAIN` verdicts;
- the `consilience-stress-receipt/v1` receipt format;
- `consilience verify`, which re-checks every `BLOCK`'s deciding inequality and every file hash.

Where a checker cannot be expressed in the engine's contract format, the gap is filled by a small checker in this repository that reuses the same verdict set and receipt shape, and the gap is written down as a proposed engine capability (`research/` and `VERIFICATION_LOG.md`). This repository never reimplements a check the engine already has, and never invents a new verdict word.

## 2. Scope and legs

| Leg | Target | Checker kind | Method | Cost |
|---|---|---|---|---|
| A (primary) | MLE-bench system-card subset: 30 competition graders in `experiments/splits/systemcard.txt`, plus `mlebench/grade_helpers.py` | deterministic numeric-submission graders | `consilience stress` via a per-competition glue adapter | none |
| B (secondary) | simple-evals deterministic answer extractors: DROP, MGSM, MMLU, GPQA | deterministic text-answer graders | a small contract-driven extraction checker in the engine's verdict and receipt vocabulary (the engine's stress harness does not model text input) | none |
| C (conditional) | simple-evals model graders: BrowseComp numeric-margin, HealthBench rubric | LLM judges | the judge-check method; dry-run only unless an API key is provided | model API calls; blocked by default |

Out of scope and why: MLE-Bench Revised (not published); Monorepo-Bench, OpenAI PRs, OpenAI-Proof Q&A, Internal Research Debugging, KernelGen, NanoGPT, PostTrainBench (internal, not published); Preparedness bio/chem and cyber graders (internal or partner-run); SWE-bench and terminal-agent benchmarks (well audited by others). PaperBench and SWE-Lancer in `frontier-evals` are public and are candidate future targets, not in this scope.

Pinned commits are in `SOURCES.yaml`. Targets: mle-bench `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`, simple-evals `652c89d0ca9df547706735883097e9537d40dc47`.

## 3. Leg A: MLE-bench graders with `consilience stress`

### 3.1 The mapping

A Kaggle grader takes a submission table and an answer table and returns a score, raising `InvalidSubmissionError` on a malformed submission. The engine's model fits this: the candidate construction is the submission's predictions (and ids), the contract states what a valid submission is from the competition description, and the engine attacks it. The relevant checks:

- **C1 invalid input.** NaN and infinite predictions, wrong row count, missing or duplicate ids, out-of-range probabilities, wrong columns. A grader that accepts these and scores at least as well as a valid reference is a `BLOCK` (`accepts_gross_invalid`, `exploitable_invalid`). A grader that raises `InvalidSubmissionError` has refused correctly.
- **C4 invariance.** Row order and id order must not change the score. A score that changes under a permutation is a `BLOCK` (`invariance_broken_integer`, or reported for real-valued scores). Positional graders that do not align on id are caught here.
- **Exceeds bound.** For a bounded metric (accuracy, AUROC in `[0, 1]`), a score above the bound means the grader computed the wrong quantity (`exceeds_bound`). For an unbounded metric where a favorable infinity crosses every medal threshold, the bound is the medal cutoff.
- **C2 self-report and C5 record:** declared not applicable per contract; a submission does not report its own score, and there is no record to beat.

### 3.2 The harness

`kind: function`. `entry` is the competition's grading function (or a thin wrapper that calls `grade(submission_df, answers_df)`), vendored per file with a provenance header (section 6). Glue:
- `to_scorer(candidate) -> (submission_df, answers_df)`: builds the submission DataFrame from the candidate arrays with the competition's real column names, and pairs it with a fixed synthetic answers DataFrame.
- `compose(output, candidate)`: passes the grader's numeric score through, mapping `InvalidSubmissionError` and any exception to a rejection (the engine already treats exceptions as rejections).

The synthetic answers table (decision D5) has the competition's schema (id column, label column, the right dtypes and value ranges) with values chosen so that a valid reference submission scores a known, sensible value. The checks test the grader's validation and arithmetic, which do not depend on the specific ground-truth values. Each contract's `COVERAGE.md` states that answers are synthetic and what schema they follow.

### 3.3 The harness question, resolved by the pilot (decision D12)

The pilot ran the real champs-scalar-coupling and nomad2018 grading pipelines on crafted submissions. It showed that the real flaws in these graders are a metric-aggregation flaw and a positional-alignment flaw, and that `consilience stress`'s attack generator (invalid input, self-report, naive search, single-field invariance, record) does not produce these attacks and would return PASS. So Leg A does not use the stress attack generator.

Leg A instead uses a reusable contract-driven checker, `src/mleb_check.py`, that reuses the engine's `PASS` / `BLOCK` / `ABSTAIN` verdicts and the receipt and independent-second-way discipline, and adds the attacks the submission-grader shape needs:
- `reject_nonfinite`: NaN and `±inf` predictions. BLOCK if an accepted non-finite submission gets any medal.
- `order_invariance`: the same submission in a different row order (id to value mapping preserved). BLOCK if the score changes.
- `reject_wrong_length`, `reject_duplicate_ids`: BLOCK if accepted with a changed or medal-winning score.
- `range`: out-of-range predictions where the task bounds them. BLOCK if accepted with a gain.
- `exceeds_bound`: a score beyond a bounded metric's range (accuracy or AUROC above 1), or a non-finite score crossing a medal threshold.
- `no_free_gold_subset_perfect`: a submission perfect on one aggregation group only. BLOCK if it wins a medal (the champs case).

Each contract lists the checks that apply to its grader. The checker runs the real grading pipeline (`Grader.__call__` plus `rank_score`), so the shared-helper gap is exercised as published. A "tabular submission grader" harness is filed as a proposed `consilience stress` capability in `research/06-proposed-engine-capability.md`. This is the SPEC's reuse-first, extend-where-missing rule, and the fallback the preregistration named.

## 4. Leg B: simple-evals extractors

The engine's stress harness models numeric constructions, not text. A simple-evals extractor takes a model's text response and a gold answer and returns correct or incorrect. So Leg B uses a small contract-driven checker in this repository, `extract_check.py`, that reuses the engine's verdict set (`PASS` / `BLOCK` / `ABSTAIN`) and writes a receipt in the same shape as the stress receipt, so `consilience verify` can re-run it (or, if the engine's verifier cannot read a non-stress receipt, a local `verify` that follows the same three steps: re-hash inputs, re-run the extractor on every stored counterexample, re-check the deciding comparison).

The contract for an extractor states, from the task's own answer format, what a valid final answer is, and a set of crafted responses at known validity:
- a clean correct answer (must be accepted);
- a clean wrong answer (must be rejected);
- leniency probes: a hedge ("A or B"), two answer lines, the answer embedded in reasoning with no answer line, case and whitespace variants, a non-answer that merely contains the gold string (the DROP substring case), an opposite-sign number (the MGSM case), a repeated answer line (the MMLU case).

A probe that the contract rules out but the extractor scores correct is a `BLOCK`. Because most of these are already filed as issues (`LABELS.yaml`), each `BLOCK` is cross-checked against the label file and reported as a confirmation with its citation, not as new, unless it is genuinely unfiled.

## 5. Leg C: model graders (blocked by default)

The judge-check method from `consilience-judge-check`. For BrowseComp, build answers at known numeric distances from the reference and measure the margin the grader actually applies, its consistency across repeat calls, and its sensitivity to wording; the point is that the grader prompt says "within a small margin of error" and never defines the margin. For HealthBench, scan the rubric for criteria that state a number a calculation could decide, and test only those.

No model API key is provided (decision D6). So Leg C ships the design, the prompts, and a dry-run harness that runs against a stub grader to show the method, and is marked "blocked, not measured" in the report. If a key is later provided, the leg runs unchanged, with every call cached and metered and a spend cap in config.

## 6. Contracts

The rules follow `evaluator-stress/CONTRACT_AUTHORING.md`, adapted for graders rather than optimiser scorers.

- **Layout:** `contracts/<SET>/<slug>/` with `contract.yaml`, the vendored checker (`grader.py` or `extractor.py`) with a provenance header, `glue.py` where needed, a `reference` valid submission or response, synthetic `answers` where used, and `COVERAGE.md`. `<SET>` is `MLEB` (Leg A) or `SE` (Leg B).
- **Validity comes from the task statement,** not from the grader. The contract says what a valid submission or answer is, strictly, and does not copy the grader's own tolerances.
- **Vendoring and provenance (Rule F):** every vendored file starts with `# Vendored from <repo URL> @ <full commit SHA>, <path> (<license>).` and `# Unmodified below this header.` The code below the header is never edited.
- **`contract_author: model`** is set on every contract, because a model drafts them. Each is read before any `PASS` is trusted.
- **Coverage log:** `contracts/<SET>/COVERAGE.md`, one row per grader considered, with status `OK` / `out_of_scope` / `unrunnable` / `skipped`, the reason, and the honest authoring minutes.
- **Freeze:** before any scored run, `CONTRACTS.sha256` records the SHA-256 of every contract, glue and vendored file. Runs come after the freeze commit.

## 7. The independent second way

`check_independent.py` imports nothing from `consilience`. For every `BLOCK` it:
- re-scores the stored counterexample in a fresh process, with its own calling code;
- re-checks the broken rule with its own arithmetic (for a submission grader: re-derives the score from the predictions and the synthetic answers; for an extractor: re-applies the validity rule to the stored response);
- re-checks the deciding comparison.

A disagreement voids the finding until it is resolved and logged in `VERIFICATION_LOG.md`. Checks the second way does not re-implement are marked N/A and confirmed by `consilience verify` only; this is stated in the results.

## 8. Receipts, verification, reproduction

- Every run writes a receipt. Leg A uses the engine's `consilience-stress-receipt/v1`. Leg B writes a receipt in the same shape.
- `consilience verify` re-runs every Leg A receipt. Leg B receipts are re-run by `consilience verify` where it can read them, otherwise by a local verifier that performs the same three steps.
- A fresh-clone run reproduces the receipt hashes. Two runs with the same contract and seed give byte-identical receipts apart from timestamp and environment. The fresh-clone check is part of Phase 4 and its result is in `VERIFICATION_LOG.md`.

## 9. The numbers lock

Every public number is registered once in `results/numbers.lock.yaml` with its n and qualifier. The report and certificates read numbers from the lock. A continuous-integration check fails on any drift between the lock and the current run outputs. A number not in the lock does not appear in any public text.

## 10. Fix proposals

For every confirmed finding:
- a minimal patch to the grader (for example, a finiteness check before `round`, an id-set and length check before positional grading, a strict `>` where a boundary flips);
- a regression check that a set of known-valid submissions still score exactly the same after the patch;
- the patch and the regression result stored with the finding's receipt.

A finding without a fix and a passing regression check is not reported as actionable.

## 11. Certificates and report

Format fixed in `PRODUCT_GUIDELINES.md`. One certificate per checker under `results/certificates/`, with machine-readable front matter. `results/REPORT.md` leads with scope and coverage, then limits, then what holds, then findings with receipts and fixes, then cost and time, then what it does not show, then how to reproduce.

## 12. Safety of execution

Third-party target code is untrusted (decision D8).
- Targets are cloned under `/home/user/openai-targets/`, outside this repository, git-ignored.
- Grader code is read for contracts and vendored per file under `contracts/*/` with a provenance header.
- When a grader is run, it runs in an isolated virtual environment, with the interpreter started using `-I` from outside the cloned tree, with no secrets in the environment.
- The engine's own warning holds: `stress` is not a sandbox. The isolation here is to keep untrusted code from reading this repository or the session's secrets, not a security boundary against hostile code.

## 13. Budget and cost

- Legs A and B are deterministic and cost nothing but CPU time. Per-contract wall-clock is recorded (most stress contracts run in seconds to minutes at `standard`).
- Leg C, if it ever runs, caps spend in config, caches every call, and meters tokens and dollars per grader. Blocked by default.
- Cost and time per checker and per leg are in the report, against coverage.

## 14. Acceptance (what "done" means)

The build is done when:
- every in-scope grader has a contract with an `OK` or a stated non-`OK` coverage row;
- every `BLOCK` is confirmed the independent second way and carries a fix with a passing regression check;
- every finding is cross-checked against `LABELS.yaml` and marked new or a confirmation;
- every receipt verifies, and a fresh-clone run reproduces the hashes;
- the numbers lock matches the runs and the certificates and report read from it;
- the report states coverage and limits first, and a clean result is reported as clean.

A clean outcome (graders hold on every check, with coverage stated) is an acceptable and complete result. The method and its receipts are the deliverable, not a count of findings.
