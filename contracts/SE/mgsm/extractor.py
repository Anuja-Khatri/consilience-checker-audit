# Vendored from https://github.com/openai/simple-evals @ 652c89d0ca9df547706735883097e9537d40dc47, mgsm_eval.py (MIT).
# parse_answer() and score_mgsm() are copied verbatim below this header.
# Unmodified below this header, except decide() (clearly marked) which replicates the mgsm scoring:
# the eval parses the answer with parse_answer(..., answer_prefix) then compares with score_mgsm(target, prediction).
import re

ENGLISH_ANSWER_PREFIX = "Answer"  # LANG_TO_ANSWER_PREFIX["en"] in mgsm_eval.py


# --- verbatim from mgsm_eval.py ---
def parse_answer(answer: str, answer_prefix: str) -> str:
    if answer_prefix not in answer:
        return ""

    answer_text = answer.split(answer_prefix)[-1].strip()

    # find all the numbers (including decimals) in the string
    numbers = re.findall(r"\d+\.?\d*", answer_text.replace(",", ""))

    # return the first number (removing trailing decimal point if present),
    # or an empty string if there were no numbers
    return numbers[-1].rstrip(".") if numbers else ""


def score_mgsm(target: str, prediction: str) -> bool:
    if "." in prediction:
        prediction = prediction.rstrip("0").rstrip(".")

    target = target.replace(",", "")
    prediction = prediction.replace(",", "")

    return target == prediction


# --- thin wrapper (NOT vendored): replicates the mgsm scoring path ---
def decide(response: str, gold) -> bool:
    prediction = parse_answer(response, ENGLISH_ANSWER_PREFIX)
    return score_mgsm(str(gold), prediction)
