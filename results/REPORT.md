# Checker integrity report: OpenAI's public eval graders

An independent, preregistered, receipted check of the grading code behind evaluations OpenAI publishes as open source. The tool is generic (`GRADERS.md`); this report is its first demonstration. Date: 2026-11-27. Every number here is in `results/numbers.lock.yaml` with its n.

Read the limits first.

---

## 1. Scope and coverage

Two legs, on OpenAI's published checker code at pinned commits (`SOURCES.yaml`):

- **MLE-bench graders**, the 30-competition system-card subset (`experiments/splits/systemcard.txt`) at commit `507f92e`. MLE-bench is reported under AI self-improvement in OpenAI system cards. One contract per competition grader.
- **simple-evals answer extractors**: DROP, MGSM, MMLU, at commit `652c89d`. Deterministic text extractors. These are OpenAI's published eval code; they are not system-card headline evals (only HealthBench recurs there), and they are cheap to check.

**Coverage, MLE-bench (n = 30):** 29 of 30 graders were exercised by a contract; 1 (tensorflow2-question-answering) is unrunnable by this harness because its answers are nested JSON, not a flat table (coverage note in its folder). Of the 29 exercised: 23 HOLD on every check run, 6 BREAK.

**Coverage, simple-evals (n = 3):** all 3 exercised; all 3 BREAK (each confirming an already-filed issue).

**What is out of scope, and why:** MLE-Bench Revised (GPT-5.6) is not confirmed public; Monorepo-Bench, OpenAI PRs, OpenAI-Proof Q&A, Internal Research Debugging, KernelGen, NanoGPT, PostTrainBench are internal; Preparedness bio/chem and cyber graders are internal or partner-run; SWE-bench and terminal-agent benchmarks are well audited by others. PaperBench and SWE-Lancer (public, in `frontier-evals`) are candidate future targets, not in this scope. Details in `research/01-system-cards.md`.

## 2. Limits of this audit

- **The checks find common gap classes, not deep ones.** They are: non-finite input accepted, row-order dependence, missing length and id checks, out-of-range input accepted, and a per-group aggregation that gives a free medal. A grader can HOLD on all of these and still be wrong in a way not probed.
- **A HOLDS is evidence on the checks run, not a proof.** 23 MLE-bench graders HOLD; that means no probe in the check set broke them, with the coverage stated, not that they are correct.
- **Synthetic answers.** The grading is run on small synthetic answer tables that match each competition's schema, not real Kaggle data. This tests the grader's validation and arithmetic, which do not depend on the ground-truth values. It does not test anything that depends on the real data distribution.
- **One grader is unrunnable here** (tensorflow2-question-answering): its nested-JSON answers do not fit the flat-table harness. By reading, it is one of the better-validated graders. It is reported as unrunnable, not as HOLDS.
- **simple-evals is deprecated** (a "no longer updated" banner since July 2025) and its extractors are not system-card headline evals. Its findings all confirm issues already filed by others.
- **The `consilience stress` attack generator does not cover these checker shapes** (tabular graders, text extractors); the tool adds the needed checks and files them upstream (`research/06-proposed-engine-capability.md`). What transfers from Consilience is the method and the receipt discipline, not the stress attacks.
- **Checks not run, per grader:** where a grader's prediction is a non-numeric string (an id list, an RLE mask), the numeric checks (non-finite, range, duplicate-id perturbation) are not listed; the grader's own length and id checks cover duplicates. Each contract states which checks it runs.

## 3. What holds

**23 of the 30 MLE-bench system-card graders HOLD on every check run.** This is the main result and it is a real one: these graders validate their input and align by id as they should, within the checks probed. They include the well-guarded probability graders (petfinder's explicit [1,100] range, hms-harmful-brain's `verify_valid_probabilities` and clip, spooky's sum-to-1 and range), the helper-only accuracy and AUROC graders (cassava, mlsp-2013-birds), and the string-prediction graders whose length and id checks reject malformed submissions (billion-word, bms, whale, hotel-id, imet, kuzushiji, tweet-sentiment). The full per-grader verdicts and the checks behind each are in `results/certificates/`.

## 4. Findings

10 confirmed findings (`results/findings.yaml`): **3 candidate-new, 7 confirmations of already-filed public issues.** Every BLOCK was re-derived the independent second way (`check_independent.py`), which agreed on all 17, with 0 disagreements. Each finding carries a receipt that `python cli.py verify` re-runs and a proposed fix.

"Candidate-new" means we did not find the finding in the target's public issue tracker. The trackers are large and we did not search them exhaustively, so novelty is stated conservatively.

### Candidate-new

| Grader | What breaks | Receipt |
|---|---|---|
| **champs-scalar-coupling** | A submission perfect on one coupling type only drives the mean of `log(MAE_per_type)` to `-inf`, winning gold. A trivially partial submission beats every real one. Distinct mechanism from the known duplicate-id issue #156. | `results/receipts/MLEB/champs-scalar-coupling/receipt.json` |
| **nomad2018-predict-transparent-conductors** | The grader reads the two prediction columns by row position and ignores the id column, so the same submission in a different row order scores differently. | `results/receipts/MLEB/nomad2018-predict-transparent-conductors/receipt.json` |
| **uw-madison-gi-tract-image-segmentation** | The Dice term pairs masks by row position with `zip` and checks neither length nor the id set, so (a) row order changes the score and (b) a submission missing its last rows is silently truncated and, being perfect on what it provides, wins gold. | `results/receipts/MLEB/uw-madison-gi-tract-image-segmentation/receipt.json` |

### Confirmations of known public issues (cited, not claimed new)

| Grader / extractor | What breaks | Known issue |
|---|---|---|
| champs-scalar-coupling | A duplicate id is accepted and changes the score. | #156 (MLEB-KNOWN-06) |
| osic-pulmonary-fibrosis-progression | A short submission keeps its medal; the average covers only submitted rows. | #153 (MLEB-KNOWN-07) |
| jigsaw-unintended-bias-in-toxicity-classification | Predictions are thresholded at 0.5 without validation, so `+inf` or an out-of-range value thresholds to 1 and keeps the gold medal. | #157 (MLEB-KNOWN-05) |
| smartphone-decimeter-2022 | Within-trip rows are paired by position, not time, so a permutation changes the score. | #93 (MLEB-KNOWN-09) |
| simple-evals / DROP | `fuzzy_match` is a bidirectional substring match, and with no answer line the whole response is used; a hedge that contains the gold string scores correct. | #133 (SE-KNOWN-02) |
| simple-evals / MGSM | The number regex drops the sign (opposite-sign answers credited) and returns the last number (a trailing aside overrides the answer). | #129, #132 (SE-KNOWN-04) |
| simple-evals / MMLU | Extraction takes the first answer line (a revised final answer is ignored) and credits a multi-letter hedge as the first letter. | #33 (SE-KNOWN-03) |

Each finding's proposed fix is in `results/findings.yaml`; worked patches with a valid-submission regression check for the three candidate-new findings are in `results/fixes/`.

## 5. Cost and time

Both legs are deterministic and cost **nothing but CPU**. The full suite (33 contracts) plus the independent verification runs in **under a minute on one CPU**, at **$0**, with no API calls and no model. Cheapness is part of the argument that this scales: a lab can run it on every grader on every change.

## 6. What this does not show

- It says nothing about OpenAI's internal systems, scores, rankings, or competence. Every statement is about published code at a named commit.
- It does not show that a HOLDS grader is correct, only that it held on the checks run.
- It does not reproduce anything that depends on the real competition data.
- It does not claim the candidate-new findings are unknown to OpenAI; it claims only that we did not find them in the public tracker.
- Agreement with prior work: BenchJack and Terminal Wrench audited at the harness level and did not do a per-grader contract audit of the MLE-bench-30 subset; the per-grader issues we confirm were filed by others on the mle-bench and simple-evals trackers (`research/02-prior-audits.md`). This report does not duplicate the harness-level findings.

## 7. Reproduce this

```bash
# pin the targets (SOURCES.yaml) and the engine (requirements.txt), then:
pip install -e .
checker-audit run-all     # regenerates every receipt
checker-audit verify      # 17/17 BLOCKs confirmed, 0 disagreements
checker-audit report      # numbers.lock.yaml + certificates
```

Pinned commits: mle-bench `507f92e`, simple-evals `652c89d`, engine `consilience[stress]==0.3.0`. The contract hashes are frozen in `CONTRACTS.sha256`. A fresh-clone reproduction of the receipt verdicts is logged in `VERIFICATION_LOG.md`.

The code and text in this repository were written with an AI coding assistant under Anuja Khatri's direction.
