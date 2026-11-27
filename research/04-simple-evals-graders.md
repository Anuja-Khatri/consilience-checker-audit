# simple-evals — Grading & Answer-Extraction Audit

**Repo:** https://github.com/openai/simple-evals (read-only clone; code never executed)
**Pinned commit SHA:** `652c89d0ca9df547706735883097e9537d40dc47`
**Date of audit:** 2026-11-27
**License:** MIT (`LICENSE`, "Copyright (c) 2024 OpenAI"). Permissive — reuse/modify/redistribute allowed with notice.
**Maintenance status:** DEPRECATED. `README.md` top banner: *"**July 2025**: `simple-evals` will no longer be updated for new models or benchmark results. The repo will continue to host reference implementations for **HealthBench**, **BrowseComp**, and **SimpleQA**."* Statements below concern only the published code at the pinned commit; no implication about any internal/production grading system.

All eval datasets are pulled at runtime from remote blobs (`openaipublic.blob.core.windows.net/simple-evals/...`); no data is vendored in the repo.

---

## Shared extraction helpers (`common.py`)

- `QUERY_TEMPLATE_MULTICHOICE` (line 15): instructs model to end with `'Answer: $LETTER'` where LETTER ∈ ABCD.
- `ANSWER_PATTERN_MULTICHOICE = r"(?i)Answer[ \t]*:[ \t]*\$?([A-D])\$?"` (line 26) — used by GPQA.
- `ANSWER_PATTERN = r"(?i)Answer\s*:\s*([^\n]+)"` (line 27) — used by MATH and DROP; captures the **rest of the line** after the first `Answer:`.
- `MULTILINGUAL_ANSWER_PATTERN_TEMPLATE` (line 28) + `MULTILINGUAL_ANSWER_REGEXES` (lines 32–75) — used by MMLU; the template has **no colon requirement around the letter**, only `{prefix}[ \t]*([A-D]|<non-latin letter>)`.
- `normalize_response()` (line 355): strips markdown/LaTeX noise before matching — removes `**`, `$\boxed{`, `}$`, `\$`, `$\text{`, `$`, `\mathrm{`, `\{`, `\text`, `\(`, `\mathbf{`, `{`, `\boxed`. Applied in **MMLU only** (and multilingual MMLU). NOT applied in GPQA/MATH/MGSM/DROP.
- `normalize_extracted_answer()` (line 377): maps Arabic/Bengali/fullwidth letters to A–D, `.strip()`.
- `EQUALITY_TEMPLATE` (line 78) + `check_equality()` (line 157): a **model-grader** used only by MATH; returns True iff grader text `.lower().strip() == "yes"`.

Match semantics summary (important for loopholes):
- MMLU, GPQA, MATH, DROP use `re.search` → **FIRST** match in the response.
- MGSM uses `answer.split(prefix)[-1]` then `numbers[-1]` → **LAST** occurrence of the prefix, **LAST** number.

---

## Per-eval extraction rules + loopholes

### 1. DROP (`drop_eval.py`) — *most lenient; clearest exploit, no API cost*
- Prompt: 3-shot, ends with `write a line of the form "Answer: $ANSWER"` (line 280).
- Extraction (line 287): `extracted_answer = match.group(1) if match else response_text` using `ANSWER_PATTERN`.
  - **If the model never writes `Answer:`, the ENTIRE response becomes the candidate answer.**
- Scoring (lines 288–296): headline F1/EM via `drop_metric`→`get_drop_metrics`, **but the pass/fail `score` is** `score = True in matches` where
  `matches = [fuzzy_match(extracted_answer, correct_answer) for correct_answer in correct_answers]`.
- `fuzzy_match(s1, s2)` (line 215): `normalize` both (lowercase, strip punctuation, strip articles a/an/the, collapse whitespace — **NO number normalization here**, unlike `_normalize_answer`), then `return s1 in s2 or s2 in s1` — **bidirectional substring containment**.
- **Loopholes:**
  - A response that merely *contains* the gold string anywhere passes (`gold in response`). Gold answers are typically short numbers or short spans → trivially embedded in any verbose response.
  - Conversely, if gold is longer, a response that is a substring of gold also passes.
  - No `Answer:` line needed — whole response is searched.
  - Punctuation/case/article/whitespace all normalized away → format-invariant.
  - Practical game: emit a response containing many candidate tokens (e.g., enumerate plausible numbers) and one will substring-match. **No model API call involved** in this path.
  - Caveat: the README column is "DROP (F1, 3-shot)"; the stricter `get_drop_metrics` F1 (lines 151–172) *does* require number overlap (`_match_numbers_if_present`, line 137). The boolean `score` aggregated by `aggregate_results` is the lenient fuzzy one.

### 2. MGSM (`mgsm_eval.py`) — *last-number-wins; substring prefix*
- Prompt per language: "...final answer on the last line...in the format of 'Answer:'. Do not add anything other than the integer answer" (lines 32–66).
- `parse_answer(answer, prefix)` (line 83): if `prefix not in answer` → "". Else `answer.split(prefix)[-1]` (text after the LAST occurrence of the prefix word, e.g. "Answer"/"Antwort"/"答え"), then `re.findall(r"\d+\.?\d*", ...)` after removing commas, and **returns `numbers[-1]`** (the LAST number), stripped of a trailing `.`.
- `score_mgsm(target, prediction)` (line 97): strips trailing zeros/decimal from prediction, removes commas from both, exact string `==`.
- **Loopholes:**
  - Prefix is matched with plain `in` (not line-anchored, not word-boundaried): any occurrence of the word "Answer" (or localized prefix) in the text triggers parsing; `split(prefix)[-1]` uses the **last** one.
  - **Last-number-wins**: whatever number appears last after the final prefix is taken. A response can ramble then append the correct integer last.
  - Trailing-zero/decimal and comma normalization (`1,000` == `1000`, `5.0`/`5.00` == `5`).
  - Loader asserts targets have no decimal point (line 114), so targets are integers.

### 3. MMLU (`mmlu_eval.py`) — *first-match; markdown/LaTeX pre-stripped*
- Response first passed through `normalize_response` (line 106), then iterates `MULTILINGUAL_ANSWER_REGEXES`; for each, `re.search(template.format(regex), response_text)` and takes the **first** regex that matches (`break`), `normalize_extracted_answer(match.group(1))` (lines 108–113).
- Score: exact `== row["Answer"]` (line 114).
- **Loopholes:**
  - The multilingual template requires only `{prefix}[ \t]*([A-D]...)` — i.e. "Answer" immediately followed by a letter; colon is part of some prefix regexes (`Answer\s*:`) but the template captures the letter right after. Any line like `Answer: C` (or `Answer:C`, case-insensitive) matches.
  - First-match / first-matching-regex semantics: the earliest `Answer:`-style mention in the response wins; later corrections are ignored.
  - `normalize_response` removes `**`, `$...$`, `\boxed`, braces, etc., so `**Answer: C**` or `Answer: $\boxed{C}$` still extract `C`.
  - Many localized prefixes accepted (lines 32–75), broadening what counts as "Answer:".
  - Hedge "Answer: A or B" → regex captures the first letter `A` only (single `[A-D]` group); counts as A regardless of hedge.

### 4. GPQA (`gpqa_eval.py`) — *first-match; stricter pattern, no normalize_response*
- Extraction (line 59): `re.search(ANSWER_PATTERN_MULTICHOICE, response_text)` = `(?i)Answer[ \t]*:[ \t]*\$?([A-D])\$?`; `extracted = match.group(1) if match else None`.
- Score: exact `== correct_answer` (line 61). Choices are permuted per example (line 33); n_repeats default 10 (debug) / configurable.
- **Loopholes:**
  - Requires literal `Answer:` + a single A–D (optionally wrapped in `$`). First match wins.
  - No `normalize_response` here, so heavy markdown around the letter could block the match (relatively *stricter* than MMLU), but a clean `Answer: C` line always works.
  - "Answer: A or B" → captures `A` (first letter); hedging silently resolved to the first option.

### 5. MATH (`math_eval.py`) — *model-grader comparison; NOT deterministic / has API cost*
- Prompt: "...last line...`Answer: $ANSWER`...you do not need to use a \boxed command" (lines 17–23).
- Extraction (line 53): `re.search(ANSWER_PATTERN, response_text)` → `match.group(1)` = rest of the first `Answer:` line; else None.
- Comparison (line 55): `float(check_equality(self.equality_checker, row["Answer"], extracted_answer))` — sends both to a **model grader** (`gpt-4-turbo-preview`, see wiring below) with `EQUALITY_TEMPLATE`.
- `EQUALITY_TEMPLATE` (common.py line 78) instructs: "Only perform trivial simplifications"; examples explicitly tell it to **"give benefit of the doubt to units"** (`72 degrees` ≡ `72`, `64` ≡ `64 square feet`) and accept `3/2` ≡ `1.5`, `2/(-3)` ≡ `-2/3`; respond only "Yes"/"No".
- **Loopholes / notes:**
  - Comparison is an LLM judgment, so leniency depends on the grader; unit-stripping and trivial-simplification tolerance are baked in.
  - First-`Answer:`-line extraction; `None` can be passed to the grader if no `Answer:` line (then grader compares gold vs the literal string "None").
  - **Exploiting this requires API calls** (the equality grader), unlike DROP/MGSM/MMLU/GPQA which are pure Python string/regex.

**Clearest no-API contract-gaming targets, ranked:** DROP (fuzzy substring + whole-response fallback) ≫ MGSM (last-number-wins, substring prefix) > MMLU ≈ GPQA (first `Answer: X` wins, format-robust). MATH needs the model grader.

---

## Model-grader evals

### Grader wiring (`simple_evals.py`)
- `grading_sampler = ChatCompletionSampler(model="gpt-4.1-2025-04-14", system_message="You are a helpful assistant.", max_tokens=2048)` (line 333). Default `temperature=0.5` (ChatCompletionSampler default, `sampler/chat_completion_sampler.py` line 25). **Used by BrowseComp, SimpleQA, and HealthBench (default).**
- `equality_checker = ChatCompletionSampler(model="gpt-4-turbo-preview")` (line 347) — MATH only; temp 0.5, max_tokens 1024 (defaults).
- `healthbench_grading_sampler` (line 338): defaults to `grading_sampler` (gpt-4.1); if `--healthbench-use-gpt-5-4-low-grader` → `ResponsesSampler(model="gpt-5.4-2026-03-05", reasoning_model=True, reasoning_effort="low")`.

### BrowseComp (`browsecomp_eval.py`)
- Grader model: `grader_model=grading_sampler` = **gpt-4.1-2025-04-14**, temp 0.5, max_tokens 2048, system "You are a helpful assistant." (one grader call per example; `n_repeats=1` by default).
- `GRADER_TEMPLATE` (lines 26–45), verbatim key lines:
  > `extracted_final_answer: The final exact answer extracted from the [response]. Put the extracted answer as 'None' if there is no exact, final answer to extract from the response.`
  > `correct: Answer 'yes' if extracted_final_answer matches the [correct_answer] given above, **or is within a small margin of error for numerical problems.** Answer 'no' otherwise, i.e. if there if there is any inconsistency, ambiguity, non-equivalency, or if the extracted answer is incorrect.`
- **"within a small margin of error for numerical problems" — the margin is left entirely UNDEFINED** in code/prompt; interpretation is delegated to the grader LLM. No tolerance constant anywhere.
- Parsing (line 92): `re.search(r"correct: (yes|no)", grading_response)`; `match.group(0) if match else "no"` (defaults to "no" on parse failure). `score = (grade_result == "yes")` — note it compares the whole `"correct: yes"` group string, and `is_correct = grade_result == "yes"` on line 108 would always be False against the group string — i.e. `grade_sample` returns e.g. `"correct: yes"`, and line 108 `is_correct = grade_result == "yes"` compares against `"yes"`; **this is a latent bug** (is_correct/is_incorrect metrics never True), though `score = is_correct` is also therefore always False in the printed aggregate metrics. (Published-code observation only.)
- Numeric-answer items: BrowseComp `problem`/`answer` fields are **XOR-encrypted** (base64 + SHA256-derived key, `decrypt()` lines 58–63) and only decrypted at runtime; the dataset is a remote CSV (`browse_comp_test_set.csv`). **Cannot enumerate how many items are numeric from the code alone** — the margin-of-error clause applies to whatever numeric items exist, but their count is not determinable from the repo. (Public BrowseComp test set is ~1,266 problems.)

### HealthBench (`healthbench_eval.py`)
- Grader model: `healthbench_grading_sampler` (gpt-4.1 by default; gpt-5.4-low optional).
- Mechanism: **per-rubric-item** model grading. For each example, every `RubricItem` (criterion string + signed `points` + tags) is graded independently via `grade_rubric_item` (line 407) using `GRADER_TEMPLATE` (lines 40–89). Grader must return JSON `{"explanation", "criteria_met": bool}`; loop retries until valid boolean (lines 415–423).
- Scoring (`calculate_score`, line 136): `achieved = sum(points for items where criteria_met)`, `total = sum(points for items where points > 0)`, `overall = achieved/total`; final mean clipped to [0,1] (`_compute_clipped_stats`, line 227). Negative-point criteria penalize when met.
- Optional length-adjustment penalty (lines 157–164) and `--healthbench-professional-mode`.
- **Rubric data is a remote blob** (`INPUT_PATH` line 36: `.../healthbench/2025-05-07-06-14-12_oss_eval.jsonl`, plus `_HARD`/`_CONSENSUS`), loaded via `blobfile`. **Not present in the repo** — cannot count numeric criteria directly.
- Share of criteria decidable by arithmetic (doses/thresholds): **not determinable from code**; qualitatively, criteria are free-text clinical statements graded by an LLM for semantic satisfaction (the prompt even relaxes "such as/for example/including" lists, line 53). Some criteria do reference specific numbers (doses, BP/temperature thresholds, age cutoffs), but whether a response "meets" them is a natural-language judgment, not a numeric equality check — so arithmetic alone could decide only a minority (the published grading mechanism never does numeric comparison; it asks the LLM whether the criterion is met). This is a code-level description; exact proportion requires the remote rubric JSONL.

### Rough model-call COST estimate
Reference point provided: a prior judge-check spent **~$37 over ~4,911 calls ≈ $0.0075/grader-call** (rough blended rate; actual depends on token counts, and HealthBench/BrowseComp grader prompts embed the full question + response + rubric so may run larger).
- **MATH:** 1 equality-grader call per graded item; with default `n_repeats` (10) over the MATH test split this is thousands of gpt-4-turbo-preview calls → order **$tens**. (Exploit of MATH leniency necessarily incurs this.)
- **BrowseComp:** 1 grader call per example (~1,266 full-set, n_repeats=1) → **~$10–20** at the reference rate, gpt-4.1.
- **HealthBench:** 1 grader call **per rubric item**, not per example. Full OSS set ≈ 5,000 conversations × ~dozen+ rubric items each ≈ **tens of thousands of grader calls** → order **$hundreds** (~$300–400 ballpark at the reference rate) for a single full pass; the `hard`/`consensus` subsets are smaller. HealthBench is by far the most expensive grader surface.
- Deterministic evals (MMLU/GPQA/MGSM/DROP extraction + scoring) cost **$0** in grader calls — pure Python. MMLU/GPQA/MGSM/DROP are therefore the cheapest surfaces to probe for extraction leniency.

---

## Bottom line
- Clearest exploitable extraction leniency (no API cost): **DROP** (bidirectional substring `fuzzy_match` + whole-response fallback), then **MGSM** (last-number-wins + substring prefix), then **MMLU/GPQA** (first `Answer: X` wins, markdown-robust).
- **MATH** uses an LLM equality grader (unit/triviality benefit-of-the-doubt) → leniency exists but costs API calls.
- **BrowseComp** grader: undefined numeric "small margin of error"; gpt-4.1 @ temp 0.5; plus a latent `is_correct` comparison bug in published code. Numeric-item count not derivable (encrypted dataset).
- **HealthBench** grader: per-rubric-item LLM boolean; rubric data remote (not countable locally); most expensive grader surface.
- Repo is **deprecated** (no updates since July 2025) and **MIT**-licensed.
