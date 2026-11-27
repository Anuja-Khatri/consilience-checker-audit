# Application lines (candidates)

Two or three one-line mentions for the application, each true to the numbers lock
(`results/numbers.lock.yaml`). Plain, casual voice. No number that is not locked.
Pick one; do not combine numbers in a way the lock does not support.

Locked numbers used below: 30 MLE-bench system-card graders checked; 23 hold on
every check; 6 break; 3 of the findings are candidate-new; 3 simple-evals
extractors checked, all confirming already-filed issues; $0 to run; 17 of 17
findings confirmed a second way.

---

1. *(the main one)*
   "I built a small reusable tool that stress-checks the graders behind evals, and
   ran it on the 30 MLE-bench graders OpenAI reports in its system cards. 23 held on
   every check; 6 broke, 3 of them apparently new, each with a re-runnable receipt
   and a one-line fix, sent to the maintainers first. It costs nothing to run, and
   anyone can point it at their own graders."

2. *(method-and-honesty angle)*
   "On OpenAI's own published eval graders, I checked 30 and found 23 clean and 6
   with integrity gaps, every finding confirmed a second independent way before I
   reported it. The clean results are reported as prominently as the breaks."

3. *(the product angle)*
   "The deliverable is not an audit, it's a tool: clone it, write a one-page
   contract for your grader, and it tells you if the grader accepts invalid input,
   grades by row order, or hands out a free medal, with a receipt. The OpenAI evals
   are just the first demonstration."

Not to use: any count of "new findings" stated as certain (they are candidate-new),
any claim about OpenAI's internal systems, or any number not in the lock.
