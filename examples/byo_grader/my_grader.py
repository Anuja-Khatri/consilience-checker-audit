"""A toy grader, to show the checker-audit tool on a grader that is NOT from OpenAI.

It scores a classification submission by accuracy. It has a deliberate, common
flaw: it aligns predictions to answers by ROW POSITION and ignores the id column.
The checker-audit tool finds this with its order_invariance check.

Replace this with your own grade(submission, answers) function and point a
contract's `harness.grade` at it to check your own grader.
"""
import pandas as pd


def grade(submission: pd.DataFrame, answers: pd.DataFrame) -> float:
    # BUG: positional alignment. A correct grader would merge on the id column.
    pred = submission["pred"].reset_index(drop=True).to_numpy()
    truth = answers["label"].reset_index(drop=True).to_numpy()
    if len(pred) != len(truth):
        raise ValueError("submission and answers differ in length")
    return float((pred == truth).mean())  # accuracy, higher is better
