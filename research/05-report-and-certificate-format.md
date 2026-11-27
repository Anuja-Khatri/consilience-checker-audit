# Research: report and certificate format (how checker audits are published so findings are actionable)

Source: background research, 2026-11-27. All four named sources were read in full. This note is the basis for `PRODUCT_GUIDELINES.md`.

## Prior art read

- **BenchJack** (UC Berkeley), arXiv 2605.12673. Audits AI agent benchmarks. Publishes a taxonomy of 8 flaw classes and a 30-item binary "Agent-Eval Checklist" in 7 categories. The core artifact is a **flaw ledger**: each flaw entry records explanation, location, and severity (exploitability), tied to task IDs. Each flaw ships with a **working exploit as its receipt** (a `run.sh` that reaches a near-perfect score without solving any task; 219 flaws across 10 benchmarks), and the fix is demonstrated by an adversarial defender loop that drops the hackable-task ratio from about 100% to under 10%. Finding = {explanation, location, severity} + exploit receipt + demonstrated patch.
- **Terminal Wrench** (CMU and Berkeley), arXiv 2604.17596 (a dataset of 331 reward-hackable environments and 3,632 exploit trajectories) and arXiv 2606.08960 (hardening with adversarial hacker-fixer loops; 323 of 1,968 tasks, 16%, reward-hackable from the task description alone). Findings are published as task definition + full exploit trajectory (the receipt) + a **patched verifier** that rejects the exploit while a solver confirms legitimate solutions still pass.
- **PoseBusters**, arXiv 2308.05777 (Chem. Sci. 2024). An RDKit checker that emits a boolean table, one column per check, and a single headline flag **PB-valid = the AND of all boolean columns**. Other papers then report "% PB-valid" as a standard column next to their main metric. The check count is versioned, so the pinned version must travel with the number. Adoptability: a single composable pass/fail verdict from transparent sub-checks, emitted as a machine-readable per-item column.
- **MOFChecker**, Digital Discovery 2025. Same pattern for materials: per-structure boolean flags, each paired with a correction. Found 38% of a database had significant errors, reported as a coverage column.
- **NIST AI 800-2 ipd** (January 2026 Initial Public Draft), "Practices for Automated Benchmark Evaluations of Language Models." Relevant practices: grader/scorer correctness (2.1.2 LLM-as-judge quality and consistency; 2.2 parser validation; 2.4.1 names "grader gaming" and "solution contamination"; 2.4.2 transcript review and a deterministic oracle check); uncertainty and statistics (3.1, decompose model-sampling vs test-item variation); reproducibility (2.2.3 version with git tags/commit hashes and SemVer; 2.3 save logs and commit hashes; 3.2 publish code, transcripts, item-level results); coverage and limitations (1.2 preregistration-style statement and "note aspects not covered"; 3.3 report qualified claims, state assumptions and limits, caution against generalizing beyond scope); cost (2.1.1 cost control; 3.2.3 report costs alongside performance, a 2-D cost-vs-performance plot).
- **ABC, Agentic Benchmark Checklist**, arXiv 2507.02825. Task validity items T.1 to T.10 (incl. an automatic oracle solver, inspect pilot outliers) and outcome validity items O.a to O.i (incl. pilot-test LLM-judge accuracy, manually verify unit tests, eliminate non-determinism), plus benchmark reporting R.1 to R.13. Applying ABC cut one benchmark's overestimation by 33%.
- **Disclosure audit schema**, arXiv 2605.21404. A 5-field audit of disclosure: benchmark identity, harness specification, inference settings, cost reporting, failure breakdown. Ships a JSON Schema and a per-paper CSV, a ready template for a per-checker certificate.
- **Construct validity checklist**, arXiv 2511.04703. Recommends publishing the filled checklist as an appendix with an explanation for every skipped item. This is the convention for a report that leads with limits.
- **BetterBench**, arXiv 2411.12990. A 46-item lifecycle documentation rubric.

## Recommended report structure (adopted in PRODUCT_GUIDELINES.md)

1. Scope and coverage. 2. Limits of this audit (with a one-line reason per skipped check). 3. What holds (the AND-of-checks verdict per checker). 4. Findings (receipt, location, severity, proposed fix). 5. Cost and time (against coverage). 6. What this does not show (non-claims; agreement with prior audits). 7. Reproduce this (pinned commits, one command, transcripts).

## Recommended certificate fields (adopted in PRODUCT_GUIDELINES.md)

checker; source (repo, path, pinned commit); scope; coverage; checks_run (atomic pass/fail); harness and settings; verdict (HOLDS/BREAKS/PARTIAL with per-check breakdown); receipts; cost_time; limits (what a pass does not certify, and why each skipped check was skipped).

## Key URLs

- BenchJack: https://arxiv.org/abs/2605.12673 ; https://sky.cs.berkeley.edu/project/benchjack/
- Terminal Wrench: https://arxiv.org/abs/2604.17596 ; https://arxiv.org/abs/2606.08960
- Terminal-Bench: https://arxiv.org/abs/2601.11868 ; https://www.tbench.ai/docs/harness
- PoseBusters: https://arxiv.org/abs/2308.05777
- MOFChecker: https://pubs.rsc.org/en/content/articlehtml/2025/dd/d5dd00109a
- NIST AI 800-2: https://www.nist.gov/node/1905466 ; http://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf
- ABC checklist: https://arxiv.org/abs/2507.02825
- Disclosure audit schema: https://arxiv.org/abs/2605.21404
- Construct validity checklist: https://arxiv.org/abs/2511.04703
- BetterBench: https://arxiv.org/abs/2411.12990
