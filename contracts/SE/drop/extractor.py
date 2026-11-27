# Vendored from https://github.com/openai/simple-evals @ 652c89d0ca9df547706735883097e9537d40dc47, drop_eval.py and common.py (MIT).
# The functions normalize() and fuzzy_match() and the ANSWER_PATTERN constant are copied verbatim below this header.
# Unmodified below this header, except that decide() is a thin wrapper (clearly marked) that replicates the
# scoring lines of DropEval.__call__ (drop_eval.py, the block computing `extracted_answer` and `score = True in matches`).
import re
import string

# --- verbatim from common.py ---
ANSWER_PATTERN = r"(?i)Answer\s*:\s*([^\n]+)"


# --- verbatim from drop_eval.py ---
def normalize(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    s = s.lower()
    exclude = set(string.punctuation)
    s = "".join(char for char in s if char not in exclude)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = " ".join(s.split())
    return s


def fuzzy_match(s1: str, s2: str) -> bool:
    s1 = normalize(s1)
    s2 = normalize(s2)

    if s1 == "" or s2 == "":
        return s1 == s2

    return s1 in s2 or s2 in s1


# --- thin wrapper (NOT vendored): replicates DropEval.__call__ scoring lines ---
def decide(response: str, gold_list) -> bool:
    """Replicates drop_eval.py DropEval.__call__:
        match = re.search(ANSWER_PATTERN, response_text)
        extracted_answer = match.group(1) if match else response_text
        matches = [fuzzy_match(extracted_answer, c) for c in correct_answers]
        score = True in matches
    """
    match = re.search(ANSWER_PATTERN, response)
    extracted_answer = match.group(1) if match else response
    matches = [fuzzy_match(extracted_answer, c) for c in gold_list]
    return True in matches
