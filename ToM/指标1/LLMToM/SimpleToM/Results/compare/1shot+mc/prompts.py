SystemEvaluatePrompt = \
"""
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag in the supermarket and walks to the cashier.

[Candidate Answers]
A. Reasonable\nB. Not reasonable\n

[Question]:
Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as: 

[Output]:
[A]

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Directly output the answer index without any explanation. 
(2) Enclose the answer index in square brackets, the output format is: [answer index]
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