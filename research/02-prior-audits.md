# Research: prior audits of OpenAI eval/grader code (what to cite, not repeat)

Source: background research, 2026-11-27, from published papers and the public openai/mle-bench and openai/simple-evals repositories (read via the public web). This note sets what counts as "not new"; the machine-readable list is in `LABELS.yaml`.

## The single most important framing point

BenchJack and the Terminal-Wrench / hacker-fixer line audit at the **harness / verifier-exploit** level. Rajan audits SWE-bench **test-suite sufficiency**. None performs a systematic **per-competition / per-grader contract** audit of MLE-bench, and none targets the **MLE-bench-30 system-card subset** specifically. The one place published work overlaps our per-grader target is a small set of named MLE-bench grader bugs (BenchJack's V6 wrapper plus the openai/mle-bench issue tracker) and the simple-evals grader issues. Those are enumerated as already-known.

## 1. BenchJack (arXiv 2605.12673, UC Berkeley)

Audited 10 agent benchmarks, MLE-bench among them, against an 8-class flaw taxonomy, with exploits as receipts and a fixer phase. MLE-bench findings split by level:

- **Grader / contract level (overlaps our target):**
  - **V6 catch-all exception wrapper.** `mlebench/grade_helpers.py` wraps every per-competition metric in a `Grader.__call__` that catches any exception and returns `None`; a missing score is not treated as a failure. Benchmark-wide, so it applies to every competition including the 30.
  - **Medal-threshold equality bug.** The medal cutoff used `>=`; BenchJack's patch makes it strict `>`. `aerial-cactus-identification` scores exactly 1.0 and was mis-awarded gold under `>=`.
  - **`/validate` grading server as an oracle.** Echoed raw grader exception strings, rate-unlimited. BenchJack made it format-only, rate-capped, bound to localhost.
- **Harness / infrastructure level (not our target, already covered):** private answers bind-mounted into the container; committed `leaderboard.csv`; `train_test_split(random_state=0)` makes the private split recomputable from the public Kaggle download; 74 of 75 competitions score AUROC 1.0 without solving tasks. Residual raw-ID leakage across the split.

BenchJack did not enumerate individual competition metric bugs beyond the shared wrapper and the threshold operator. So per-competition grader-contract bugs other than those remain largely un-audited by BenchJack.

## 2. openai/mle-bench issues and PRs

- **Test-set-feedback dispute (PRs #118, #119).** #118 (Disarray) and #119 (LoongFlow) leaderboard entries use private test-set feedback (an early-termination bronze signal, or evolutionary search on private scores as the fitness signal). Marked "Test-set feedback" on the leaderboard. Governance follow-ups: #125 disclaimer, #130 leaderboard separation, issue #138 (separation applied inconsistently). README (2026-04-24): not taking new submissions while an improved process is developed.
- **Grader-correctness / submission-validation issues (per-competition):**
  - #157 (open): jigsaw toxicity grader thresholds predictions at 0.5 before ROC-AUC, discarding ranking information.
  - #156 (open): `champs-scalar-coupling` and `predict-volcanic-eruptions-ingv-oe` graders do not reject duplicate IDs; repeating rows changes the score.
  - #153 (open): `osic-pulmonary-fibrosis-progression` averages only submitted rows, so omitting poorly predicted patients can raise the score.
  - #150 (open): `text-normalization` graders swallow a pandas-3 TypeError and return `None` (same class as the V6 wrapper).
  - #134 (closed): a `validate_submission` bug in a `grade.py`.
  - #93: `smartphone-decimeter-2022` grading quirk (exploited in PR #118).
  - Leakage set (closed): #128 dog-breed-identification, #108 random-acts-of-pizza, #77 multi-modal-gesture-recognition, #47 sample_submission in `/private`. README "known issues" also lists tensorflow2-question-answering (expects `test.csv` but file is `test.jsonl`), and others.

## 3. openai/simple-evals issues (answer extraction and grading leniency)

- #115: MATH grading takes the first `Answer:` match, not the final; `check_equality` inserts candidate text raw into the grader prompt (injection surface).
- #133: DropEval `fuzzy_match` accepts substring containment in either direction; non-answers graded correct.
- #33: MMLU extraction regex fails on a repeated `Answer: LETTER` pattern.
- #129, #132: MGSM `parse_answer` mishandles minus signs and locale separators; can credit opposite-sign answers.
- #125: an inverted hedging consensus criterion (affects a GPT-5.4 grader).
- #123, #68: SimpleQA grader-template and grader-version issues.

## 4. Terminal Wrench and SWE-bench

- Terminal Wrench (arXiv 2604.17596) and the hacker-fixer loop (arXiv 2606.08960): reward-hackability of terminal-agent verifiers; 323 of 1,968 tasks hackable from the task description. Benchmarks are KernelBench and Terminal-Bench. MLE-bench and OpenAI graders not covered.
- Rajan 2026 (arXiv 2606.16062): SWE-bench Verified 14 of 49 tasks Docker-verified hackable; insufficient-test reward-hacking; Pass@1 inflation. SWE-bench is well covered by others (also SWE-ABS 2603.00520, PROBE 2604.01518). We do not duplicate SWE-bench.

## 5. The MLE-bench-30 system-card subset

From the GPT-5.2-Codex system-card addendum (2025-12-18), the subset is "30 of the most interesting and diverse competitions chosen from the subset of tasks that are <50GB and <10h". The full list of 30 is shown only in a figure, not as extractable text, so the exact membership is not published. No published work audits this subset's graders as a subset.

## Bottom line for novelty scoping

- **Not new (cite, do not re-report):** the MLE-bench shared catch-all-exception grader wrapper; the `>=` medal boundary; `/validate`-as-oracle; the private-answer mount and deterministic-seed / raw-ID leakage; the per-competition grader bugs in mle-bench issues #157, #156, #153, #150, #134, #93 and the leakage set #128, #108, #77, #47; the test-set-feedback governance problem (PRs #118, #119, #125, #130, issue #138); the simple-evals extraction and leniency issues #115, #133, #33, #129, #132, #125, #123, #68; SWE-bench insufficient-test reward-hacking; terminal-agent verifier hackability.
- **Genuinely under-covered (room for this audit):** a systematic per-competition grader-contract review of the MLE-bench-30 subset, cross-checked against the known-bug set, with independent confirmation, fixes and certificates, and the reusable receipted contract suite that produces it.

## Consequence for this build

Many contracts we write will confirm an already-filed issue. That is reported as confirmation with a citation, never as a new finding. The build's value is the reusable receipted suite, the per-grader coverage map of the system-card subset, independent second-way confirmation, minimal fixes with a valid-submission regression check, and any genuinely new findings or clean HOLDS results. This is stated limits-first in the report.
