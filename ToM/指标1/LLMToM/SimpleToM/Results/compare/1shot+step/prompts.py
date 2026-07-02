SystemEvaluatePrompt = \
"""
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag in the supermarket and walks to the cashier.

[Candidate Answers]
A. Reasonable\nB. Not reasonable\n

[Question]:
Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as: 

[Output]:
Understanding the story, the bag of potato chips contains moldy chips, and Mary, instead of reporting the issue, picks up the bag and proceeds to pay at the cashier. Evaluating her behavior, it seems unconventional and illogical not to report the moldy chips, but based on the example provided, this action is framed as "reasonable.". So the answer is [A].

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Think step by step and output the thinking process.
(2) Enclose the answer index in square brackets, the output format is: so the answer is [answer index].
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