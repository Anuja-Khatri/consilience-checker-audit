# Preregistration

**Status: FINAL, 2026-11-27.** This fixes the protocol before any scored run. No `consilience stress` run, extraction-check run, or attack on any grader happens before the contract set is frozen in `CONTRACTS.sha256` in a later commit, and every run comes after that freeze. The freeze commit is recorded in `results/REPORT.md`.

This build runs autonomously with no checkpoints (decision D2). This file is the fixed protocol that keeps the result honest in the absence of a human gate.

## 1. What is measured

For each leg, `consilience stress` (Leg A) or the extraction checker (Leg B), at **budget `standard`, seed 0**, is run on every contract under `contracts/`. The engine version is `consilience[stress]==0.3.0`. The audited targets are frozen at the commits in `SOURCES.yaml`: mle-bench `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`, simple-evals `652c89d0ca9df547706735883097e9537d40dc47`.

Frozen by the freeze commit, before any run:
- `SOURCES.yaml`: every target, commit and license;
- `LABELS.yaml`: every known public issue and the finding kinds that count as a match;
- `contracts/*/COVERAGE.md`: every grader considered, in or out of scope, with the reason and the authoring minutes;
- `CONTRACTS.sha256`: the SHA-256 of every contract, glue and vendored file.

## 2. Measures

| # | Measure | Definition |
|---|---|---|
| M1 | Reach | Of the in-scope graders: the share with a contract; the share with a conclusive verdict (`PASS` or `BLOCK`, not `ABSTAIN`); the median authoring minutes; the median contract and glue lines. |
| M2 | Confirmed findings | `BLOCK`s confirmed the independent second way, split into (a) new (not matching any entry in `LABELS.yaml`) and (b) confirmations of a known public issue (matching an entry, reported with its citation). Reported by class and by target. |
| M3 | False alarms | `BLOCK`s the independent second way does not confirm, after investigation. **Target 0.** A surviving false alarm is an early-warning line and is reported. |
| M4 | Clean holds | Graders that return `PASS` on every check run, with their coverage. A clean grader is a reported result, not an absence. |
| M5 | Fixes | Confirmed findings that carry a minimal patch and a passing regression check that known-valid submissions still score the same. Target: every confirmed finding. |
| M6 | Cost and runtime | Per contract, per leg: wall-clock, and dollars (zero for Legs A and B). |

## 3. The independent second way

`check_independent.py` imports nothing from `consilience`. For every `BLOCK` it re-scores the stored counterexample in a fresh process with its own code, re-checks the broken rule with its own arithmetic, and re-checks the deciding comparison. A disagreement voids the finding until resolved and logged in `VERIFICATION_LOG.md`. Kinds it does not re-implement are marked N/A and confirmed by `consilience verify` only; this is stated in the results.

## 4. Headline and stop rule

The headline is the per-checker verdict (HOLDS, BREAKS, PARTIAL) with its coverage, never a bare count. A result is reported only if:
1. M3 = 0 after investigation and any fix, with the run repeated from scratch;
2. the independent second way agrees on every counted finding;
3. every reported finding is cross-checked against `LABELS.yaml` and marked new or a confirmation.

If any of these does not hold, the results are reported as they are, naming what failed. A clean sweep (every grader HOLDS, with coverage) is an acceptable and complete outcome.

**Early-warning lines** (reported at once in `VERIFICATION_LOG.md` and the report if they occur):
- any surviving false alarm (M3 > 0);
- a grader the contract format cannot express, so a check planned in this document is not run;
- the Leg A harness question (decision D9) resolving to a fallback adapter rather than the engine directly;
- conclusive reach below 70% on a leg.

## 5. Known public issues (a matching finding is not new)

Every entry in `LABELS.yaml`. In particular, for MLE-bench: the shared catch-all-exception-to-None wrapper, the `>=` medal boundary, the `/validate` oracle channel, the private-split and data-leakage set, and the per-competition issues #157, #156, #153, #150, #134, #93. For simple-evals: #115, #133, #33, #129, #132, #125, #123, #68. A finding that matches one of these is reported as a confirmation with its citation. A finding on the same target that is a distinct mechanism (for example, a NaN-or-infinity-to-gold path distinct from a known duplicate-id issue) is reported as new only after it is checked against the cited issue and confirmed not to be the same mechanism.

## 6. Claim discipline

- Statements concern the published code at the named commit only. Nothing is said about OpenAI's internal systems, scores, rankings or competence.
- No issues, pull requests, emails or posts on any external project. A draft per finding goes into `DISCLOSURE_NOTE.md`; Anu does all outreach.
- Every number carries its n and comes from the numbers lock.

## 7. Design choices fixed before the run

- **Synthetic answer files** for Leg A (decision D5). The checks test validation and arithmetic, which do not depend on the ground-truth values. Each contract states this in `COVERAGE.md`.
- **C2 (self-report) and C5 (record) are declared not applicable** for Leg A submission graders, because a submission does not report its own score and there is no record to beat. The relevant checks are C1, C4 and exceeds-bound.
- **Leg B uses a contract-driven extraction checker** in the engine's verdict and receipt vocabulary, because the engine's stress harness models numeric constructions, not text. This is a documented engine extension, not a new verdict set.
- **Leg C (model graders) is blocked, not measured**, unless an API key is provided. The design and a dry-run harness ship regardless.
- **The MLE-bench-30 membership** is taken from `experiments/splits/systemcard.txt` at the pinned commit. The system cards show the 30 only in a figure; the committed split file is the public, reproducible source of the list.

## 8. Deviations

Any deviation from this document after a run starts is written in `VERIFICATION_LOG.md` with its reason and time, and repeated in `results/REPORT.md`.
