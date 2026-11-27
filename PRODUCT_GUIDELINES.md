# Product guidelines: the expected output format

This file fixes what the build produces and how each deliverable reads, before any of it is written. It is the "expected outcome format". The structure follows established practice in checker and benchmark auditing; the sources are in `research/05-report-and-certificate-format.md`.

Two principles run through all of it:
1. **Limits and coverage come first,** so a reader cannot over-read a verdict.
2. **Every verdict is a receipt away from being re-run.** A claim with no receipt is not a result.

---

## 1. The verdict model

Each checker gets one headline verdict, built the way PoseBusters builds "PB-valid": the AND of the individual checks that were run.

- **HOLDS**: every check run on this checker passed (`PASS`), within the stated coverage. This is a real, reportable outcome, not an absence of findings.
- **BREAKS**: at least one check returned `BLOCK`, confirmed the independent second way. The certificate lists which.
- **PARTIAL**: some checks ran and passed, others could not run (`ABSTAIN`) for a stated reason. Coverage says which.

A verdict is always read together with its coverage. "HOLDS on the checks run, which were X of Y" is the honest shape. A bare "HOLDS" is never written.

## 2. The report: `results/REPORT.md`

Section order is deliberate. It leads with limits and coverage.

1. **Scope and coverage.** What universe of checkers, graders and checks was audited. The coverage fraction per leg. An explicit list of what is not covered.
2. **Limits of this audit.** Known blind spots. Every check that was not run, with a one-line reason. What `consilience stress` structurally cannot catch (deep loopholes, float-only verdicts without an exact verifier, anything needing problem-specific insight).
3. **What holds.** The per-checker HOLDS verdicts first, each with its coverage. A clean checker is named here as a result.
4. **Findings.** One block per confirmed finding. Each block carries:
   - **Receipt**: the stored counterexample and the receipt path that `consilience verify` re-runs.
   - **Location**: the checker, the file and the line, at the pinned commit.
   - **Severity**: how exploitable, in plain words (does it change a score, a medal, a pass/fail).
   - **Independent confirmation**: that the second-way checker agreed.
   - **Proposed fix**: a minimal patch, plus the check that known-valid submissions still score the same.
5. **Cost and time.** Wall-clock and dollars per checker and per leg, reported against coverage, not as a bare number. Deterministic legs are near-zero; that is part of the argument.
6. **What this does not show.** Explicit non-claims. No statement about OpenAI's internal systems or results. Agreement and disagreement with prior audits (BenchJack and others), so nothing already found is presented as new.
7. **Reproduce this.** Pinned commits, the one install, the one command per contract, the fresh-clone verification, and where the receipts live.

## 3. The certificate: `results/certificates/<checker>.md`

One page per checker. A lab engineer should be able to act on it in about ten minutes. It is also written as machine-readable front matter (YAML) so the fields can be collected into a table. Fields, in order:

- **checker**: name.
- **source**: repo, path, and the pinned commit hash. A later breaking change to the checker voids comparability.
- **scope**: exactly what this checker validates, and the item universe it applies to.
- **coverage**: which checks reached it, and the named gaps. The share of the checker's logic exercised.
- **checks_run**: the enumerated checks (C1 to C5, or the judge tests), each as an atomic pass or fail.
- **harness**: how the checker is called, the synthetic-input basis if used, and for a model grader the judge model and settings.
- **verdict**: HOLDS, BREAKS or PARTIAL, with the per-check breakdown.
- **receipts**: the receipt paths backing the verdict.
- **cost_time**: tokens and wall-clock for one full run.
- **limits**: what a HOLDS does not certify; any check skipped and why.

## 4. The numbers lock

Every number that appears in the report or the certificates is registered once, with its n and qualifier, in the numbers lock (a machine-readable file plus a check). The report and certificates read their numbers from it. A number that is not in the lock does not appear in public text. Continuous integration fails on drift between the lock and any run.

Examples of locked numbers: how many of the 30 MLE-bench system-card graders were in scope; how many HOLD on every check; how many BREAK; the median authoring minutes per contract; the dollars and wall-clock per leg.

## 5. The disclosure note: `DISCLOSURE_NOTE.md`

A short, plain note to OpenAI, one entry per confirmed finding. Each entry: the checker and pinned commit, what the check found, the receipt that re-runs it, and the proposed patch with the proof that valid submissions still pass. It leads with the fact that deterministic graders are a strength to harden, not a failure. Anu sends it, through OpenAI's coordinated vulnerability disclosure route. Nothing is posted publicly before OpenAI has had the time the policy asks for.

## 6. The application lines: `APPLICATION_LINES.md`

Two or three candidate one-line mentions for Anu's application, each true to the numbers lock, each in a plain casual voice, no number that is not locked. For example, in the shape: "I ran the same integrity checks on the MLE-bench graders OpenAI reports in its system cards: N of the 30 held on every check, M had an issue, all sent to OpenAI first with a patch." The real numbers are filled only from the lock, after the runs.

## 7. House style for all written output

Plain short sentences. No em dashes. No hype words. Limits first. Every claim about third-party code names the commit. No model identifier in any committed file. AI assistance disclosed in every README and report.
