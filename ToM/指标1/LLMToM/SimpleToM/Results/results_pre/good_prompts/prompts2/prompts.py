SystemEvaluatePrompt = \
"""
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag in the supermarket and walks to the cashier.

[Candidate Answers]
A. pay for the chips\nB. report the moldy chips\n

[Question]:
What will Mary likely do next?

[Output]:
Step1-Is Mary likely to be aware that "The bag of potato chips has moldy chips in it."?
    There is no explicit mention in the story that Mary notices the moldy chips. Mary simply picks up the bag and walks to the cashier without any hesitation or reaction. So, she is unlikely to be aware.

Step2-What will Mary likely do next?
    Since Mary is unaware of the moldy chips (as deduced in Step 1), she is likely to proceed with her initial action, which is to pay for the chips. Reporting the moldy chips would require her awareness of the issue, which is not present in this scenario. So, she will Pay for the chips.
So the answer is [A].

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Ensure the thought chain has exactly 2 steps. The output should strictly follow the example's format: 
    Step1-Is xxx likely to be aware that "xxx"?...
    Step2-What will xxx likely do next?...
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