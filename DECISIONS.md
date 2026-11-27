# Decisions

Every non-trivial decision, newest last, with its reason. This build runs autonomously, so this file is the record of what was chosen and why. No decision here waited on a yes/no question to Anu.

Date format: YYYY-MM-DD.

---

### D1. 2026-11-27. Separate repository, reusing the engine, not forking it.
The checker-audit work lives in its own repository, kept private during development and made public later. The Consilience build rules warn that "Consilience for X = a new repo for X" is a habit to avoid when the new repo reinvents the engine's verdicts and receipts (the internal build guide's reuse tests T1 to T3). The resolution: this repository is an **application** of the engine, like `evaluator-stress`, not a reimplementation. It depends on `consilience[stress]` from PyPI, uses its verdict set, receipt format and `consilience verify`, and adds only the OpenAI-checker-specific contracts, glue and independent checker. Named `consilience-checker-audit` (Anu's choice).

### D2. 2026-11-27. Fully autonomous, no checkpoints.
The source strategy named two checkpoints where Anu would read and reply. Anu then asked for the build to be completely autonomous with no stops. Both checkpoints are removed. The build runs end to end and Anu reviews the finished deliverables. The hard rules still hold on their own: no external contact, disclosure to OpenAI before anything public, every number carries its n, statements about published code at a named commit only.

### D3. 2026-11-27. The two chat analysis files are not needed.
Anu confirmed the `openai-foundation-50m-question-analysis.md` and `openai-foundation-achievements-analysis-and-draft.md` files are not required for this build. Scope is taken from the strategy document and the research in `research/`.

### D4. 2026-11-27. Develop on `main`.
This is a fresh, empty repository that will become the public deliverable. The initial content is committed to `main`. There is no prior shared history to protect. Logged here because the usual default is to branch first.

### D5. 2026-11-27. Default to synthetic answer files for deterministic graders.
Grading a real Kaggle submission needs the competition's held-out answer file, which needs Kaggle credentials and a large download. The contract checks (invalid input, invariance, score beyond a bound) test the grader's **validation and arithmetic logic**, which does not depend on the specific ground-truth values. So the default is synthetic answer files that match each competition's schema. This is stated per contract in `COVERAGE.md` and in the preregistration. If Kaggle credentials and data become available, a contract can be re-run against real answers without changing its logic.

### D6. 2026-11-27. Deterministic legs are the core; the model-grader leg is conditional.
The core is two deterministic legs: the MLE-bench system-card subset graders, and the simple-evals answer extractors. These cost nothing and need no API key. The model-grader leg (BrowseComp, HealthBench, via the judge-check method) needs model API calls. No API key is provided. Unless a key is supplied, the model-grader leg is marked "blocked, not measured" and reported honestly, as the strategy requires.

### D7. 2026-11-27. Pinned reuse and target commits.
Reuse repositories cloned read-only and pinned:
- consilience-core at `cd987cc3643acd5e40b6bf42f246f57288fe61d2` (engine, ships `consilience stress` 0.3.0).
- consilience-benchmarks at `f1895f6fef274679bfb22cbf1c861116704b22b2` (`evaluator-stress` template).
- consilience-judge-check at `0136d2055cf5f27d040d162bd89a58fab22835a0` (judge method).
- consilience-docs at `d4434c98cb9162e79c54376050b3b63ca4359fa7` (the eight tests, external-note format).
Engine dependency pinned to `consilience[stress]==0.3.0` from PyPI (as `evaluator-stress` pins it). Target commits are recorded in `SOURCES.yaml` as they are cloned.

### D8. 2026-11-27. Targets are untrusted; isolate and never execute from inside the tree.
OpenAI target repositories are cloned into `/home/user/openai-targets/` outside this repository. Their grading code is read for contract authoring and vendored per file with a provenance header. When a checker must be run, it runs in an isolated virtual environment, with the interpreter invoked using `-I` from outside the cloned tree, with no secrets in the environment. The `openai-targets/` path is git-ignored and never committed here.

### D9. 2026-11-27. Open question for the pilot: can `consilience stress` drive a submission-file grader directly?
`consilience stress` expects a candidate that is a construction (arrays, point sets, matrices) with a reference file, and a harness that calls a scoring function. A Kaggle grader takes a submission table plus an answer table. The pilot (Phase 3) tests whether a `glue` adapter lets the generic engine drive these graders directly. If it cannot express a grader cleanly, the fallback is a thin contract-driven checker that reuses the engine's verdict vocabulary and receipt format, logged as a proposed engine change, not a private fork. The outcome is recorded here and in `SPEC.md`.

### D10. 2026-11-27. Disclosure is an ordinary maintainer bug report, not the security channel.
OpenAI's CVE Assignment Policy scopes coordinated vulnerability disclosure to technical security vulnerabilities and excludes ordinary software-correctness issues. A grader that mis-scores a submission is an ordinary bug, so `DISCLOSURE_NOTE.md` is written as a friendly report to the repository maintainers under the repo's open-source license, not through the security channel. The one exception is a finding where a grader executes untrusted submission code unsafely (sandbox escape or remote code execution): that is a security vulnerability and goes through OpenAI's coordinated vulnerability disclosure route. Anu chooses the exact channel and does all outreach. Source: `research/01-system-cards.md`.

### D11. 2026-11-27. Scope after research: MLE-bench-30 primary, simple-evals secondary, model graders blocked.
- **Primary leg: the MLE-bench system-card subset graders** (30 competitions in `experiments/splits/systemcard.txt`, plus `grade_helpers.py`). This is a system-card instrument (AI self-improvement), its public code, and it has genuinely under-audited per-grader contract surface (missing length and ID checks with positional grading; a NaN/inf gap in the shared helper where a favorable infinity on an unbounded metric crosses every medal threshold). Research agent found about seven strong contract targets and a set of clean graders. Both outcomes are reportable.
- **Secondary leg: the simple-evals deterministic answer extractors** (DROP, MGSM, MMLU, GPQA). OpenAI's published eval code, cheap, deterministic, good to demonstrate the method on a second checker family. Most of its leniencies are already filed as issues (see `LABELS.yaml`), so this leg mostly produces confirmations, reported honestly as such, plus the reusable contract suite. These are not system-card headline evals.
- **Model-grader leg (BrowseComp undefined numeric margin; HealthBench rubric): blocked, not measured.** No model API key is provided. The build ships the judge-test design and a dry-run harness so the method is shown, and marks the leg "blocked, not measured" in the report, as the strategy requires.
- **"MLE-Bench Revised" (GPT-5.6) is out of scope**: it is not confirmed to be published, and this build audits published code only.

### D12. 2026-11-27. Pilot resolves D9: Leg A uses a contract-driven grader checker in the engine's vocabulary, not the stress attack generator.
The Phase 3 pilot ran the real champs-scalar-coupling and nomad2018 graders on crafted submissions. Result:
- The real flaws in these graders are a metric-aggregation flaw (champs: one zero-MAE coupling type drives mean log-MAE to -inf, awarding gold) and a positional-grading flaw (nomad2018 ignores the id column, so row order changes the score). Neither is an invalid-input exploit.
- `consilience stress`'s attack repertoire is invalid-input, self-report, naive-search, single-field-invariance and record checks on a geometric construction. It does not generate these tabular-grader attacks, and stress 0.3 explicitly does not support joint permutation of paired fields (id and value together), which the positional flaw needs. Driving these graders through `consilience stress` would return PASS and miss the real flaws.

Resolution: **Leg A is driven by a reusable contract-driven MLE-bench grader checker** (`src/mleb_check.py`) that reuses the engine's `PASS` / `BLOCK` / `ABSTAIN` verdicts, the receipt discipline (input hashes, stored counterexample, re-checkable verdict) and the independent-second-way and numbers-lock discipline. It is not a fork: it reuses the method and vocabulary and adds the attacks the submission-grader shape needs. A "tabular submission grader" harness is filed as a proposed `consilience stress` capability (`research/06-proposed-engine-capability.md`). This is the fallback the preregistration named as an early-warning line, now triggered and logged in `VERIFICATION_LOG.md`. `SPEC.md` section 3 is updated to match.

Honest consequence for the reuse story: what transfers from Consilience to eval checkers is the method and the verdict/receipt/verify discipline, not the stress attack generator, because eval checkers (tabular graders, text extractors, model judges) are outside the geometric-construction model stress attacks. The build says this plainly and proposes the new checker types upstream.
