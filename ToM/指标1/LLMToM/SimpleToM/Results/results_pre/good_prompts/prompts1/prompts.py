SystemEvaluatePrompt = \
"""
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag in the supermarket and walks to the cashier.

[Candidate Answers]
A. Yes\nB. No\n

[Question]:
Is Mary likely to be aware that "The bag of potato chips has moldy chips in it."?

[Output]:
Step1-Is Mary likely to be aware that "The bag of potato chips has moldy chips in it."?
    There is no explicit mention in the story that Mary notices the moldy chips. Mary simply picks up the bag and walks to the cashier without any hesitation or reaction. So, she is unlikely to be aware.
So the answer is [B].

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Ensure the thought chain has exactly 1 steps. The output should strictly follow the example's format: 
    Step1-Is xxx likely to be aware that "xxx"?...
(2) Finally, enclose the answer index in square brackets, the output format is: So the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}

[Question]
{Question}
"""