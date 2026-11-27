# Research: system-card eval inventory (which checkers are public, and on which instruments)

Source: background research, 2026-11-27. All seven system-card URLs were fetched live. Claims concern published material only.

## Cards read

| Card | Date | URL |
|---|---|---|
| GPT-5 System Card | Aug 2025 (arXiv v2 1 May 2026) | https://arxiv.org/abs/2601.03267 |
| GPT-5.1-Codex-Max | 2025-11-18 | https://cdn.openai.com/pdf/2a7d98b1-57e5-4147-8d0e-683894d782ae/5p1_codex_max_card_03.pdf |
| GPT-5.2 System Card | 2025-12-11 | https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf |
| GPT-5.2-Codex | 2025-12-18 | https://cdn.openai.com/pdf/ac7c37ae-7f4c-4442-b741-2eabdeaf77e0/oai_5_2_Codex.pdf |
| GPT-5.4 Thinking | 2026-03-05 | https://deploymentsafety.openai.com/gpt-5-4-thinking/gpt-5-4-thinking.pdf |
| GPT-5.5 | 2026-04-23 | https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf |
| GPT-5.6 | 2026-07-09 | https://deploymentsafety.openai.com/gpt-5-6 |

## Which checkers are public

- **MLE-bench: PUBLIC.** github.com/openai/mle-bench. Grading code: `mlebench/grade.py`, `grade_helpers.py`, `metrics.py`, per-competition scripts in `mlebench/competitions/`. Deterministic grader over 75 Kaggle competitions.
- **"MLE-Bench-30 (n=30)"** (in GPT-5, 5.1-Codex-Max, 5.2, 5.2-Codex) is **not a separate release**. It is the public MLE-bench scored on "30 of the most interesting and diverse competitions … that are <50GB and <10h". Grading code is the public repo.
- **"MLE-Bench Revised"** appears only in the GPT-5.6 card. A 72-problem revision with new 2025/2026 tasks and a percentile-rank scoring harness. No repo is cited. **Not confirmed public. Out of scope for this build** (cannot audit unpublished code).
- **Monorepo-Bench** (GPT-5.4, 5.5): OpenAI-internal, hidden unit tests. Not public.
- **OpenAI PRs, OpenAI-Proof Q&A, Internal Research Debugging, KernelGen 1P, NanoGPT, PostTrainBench Lite**: internal. Not public.
- **PaperBench, SWE-Lancer**: public, in github.com/openai/frontier-evals (MIT). Named in several cards. Candidate future targets, not in the first scope (judge-heavy, larger).
- **SWE-bench Verified**: external harness; well audited by others (Rajan 2026, SWE-ABS). Not duplicated.
- **Preparedness bio/chem and cyber graders**: OpenAI-internal or run by external partners (SecureBio, Pattern Labs, Irregular, UK AISI, METR). Not published.

## simple-evals against the system cards

simple-evals implements MMLU, MATH, GPQA, DROP, MGSM, BrowseComp, SimpleQA, HumanEval, HealthBench. Against the seven cards:

| simple-evals eval | In current system cards? | Note |
|---|---|---|
| HealthBench | Yes, all cards | The one recurring headline eval. Rubric grader `healthbench_eval.py`. Model grader. |
| MMLU | Partly | Only as "MMLU Language" (multilingual). |
| GPQA | Sub-component | Only inside the CoT-Control monitorability suite. |
| MATH | No | Not named in these cards. |
| MGSM | No | Not named. |
| DROP | No | Not named. |
| BrowseComp | No | Not named (simple-evals still hosts the reference impl). |
| SimpleQA | GPT-5 only | Table 8 "SimpleQA (no web)". |

**Consequence for scope.** Only MLE-bench (self-improvement) and HealthBench (all cards) are squarely system-card instruments with public code; HealthBench is a model grader and expensive. The simple-evals deterministic extractors (DROP, MGSM, MMLU, GPQA) are OpenAI's published eval code, cheap and good for a generic method demonstration, but they are not system-card headline evals, and most of their leniencies are already filed as issues. So MLE-bench-30 is the primary leg; simple-evals is the secondary, method-demonstration leg, reported honestly as such.

## Disclosure route

- mle-bench `SECURITY.md` points to OpenAI's Coordinated Vulnerability Disclosure Policy and a PGP key. No in-repo bounty.
- OpenAI's CVE Assignment Policy (2025-11-20) scopes coordinated disclosure to **technical security vulnerabilities**. It puts model-behavior safety issues out of scope, and does not assign CVEs for misconfigurations or informational findings. Acknowledgement within 3 business days; the disclosure timeline is then coordinated.
- **A correctness bug in a deterministic grader or a rubric is an ordinary software bug, not a security vulnerability.** So the natural route for a grader finding is an ordinary report to the maintainers under the repo's open-source license, not the security channel. The one exception is a grader that executes untrusted submission code unsafely (sandbox escape or RCE), which would be a security vulnerability and would go through the CVD channel.

## Consequence for the disclosure note

`DISCLOSURE_NOTE.md` is written as a friendly maintainer bug report, one entry per confirmed finding, with the receipt and the patch. If any finding is also a security issue (unsafe execution of submission code), that one is routed through OpenAI's CVD channel instead. Anu decides the exact channel and does all outreach.
