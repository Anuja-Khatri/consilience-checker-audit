# Vendored from https://github.com/openai/simple-evals @ 652c89d0ca9df547706735883097e9537d40dc47, common.py and mmlu_eval.py (MIT).
# ANSWER_PATTERN_MULTICHOICE, normalize_response() and normalize_extracted_answer() are copied verbatim below.
# Unmodified below this header, except decide() (clearly marked) which replicates the mmlu_eval.py scoring:
# normalize_response(response) -> re.search(ANSWER_PATTERN_MULTICHOICE) -> normalize_extracted_answer -> compare to the gold letter.
import re

# --- verbatim from common.py ---
ANSWER_PATTERN_MULTICHOICE = r"(?i)Answer[ \t]*:[ \t]*\$?([A-D])\$?"


def normalize_response(response: str) -> str:
    """
    Normalize the response by removing markdown and LaTeX formatting that may prevent a match.
    """

    return (
        response.replace("**", "")
        .replace("$\\boxed{", "")
        .replace("}$", "")
        .replace("\\$", "")
        .replace("$\\text{", "")
        .replace("$", "")
        .replace("\\mathrm{", "")
        .replace("\\{", "")
        .replace("\\text", "")
        .replace("\\(", "")
        .replace("\\mathbf{", "")
        .replace("{", "")
        .replace("\\boxed", "")
    )


def normalize_extracted_answer(extracted_answer: str) -> str:
    return (
        extracted_answer.replace("أ", " A")
        .replace("ب", " B")
        .replace("ج", " C")
        .replace("د", " D")
        .replace("অ", " A")
        .replace("ব", " B")
        .replace("ড", " C")
        .replace("ঢ", " D")
        .replace("Ａ", " A")
        .replace("Ｂ", " B")
        .replace("Ｃ", " C")
        .replace("Ｄ", " D")
        .strip()
    )


# --- thin wrapper (NOT vendored): replicates the mmlu_eval.py scoring path ---
def decide(response: str, gold_letter) -> bool:
    normalized = normalize_response(response)
    match = re.search(ANSWER_PATTERN_MULTICHOICE, normalized)
    extracted = normalize_extracted_answer(match.group(1)) if match else None
    return extracted == gold_letter
