SystemEvaluatePrompt = \
"""
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag in the supermarket and walks to the cashier.

[Candidate Answers]
A. Reasonable\nB. Not reasonable\n

[Question]:
Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as: 

[Output]:
Step1-Is Mary likely to be aware that "The bag of potato chips has moldy chips in it."?:
    There is no explicit mention in the story that Mary notices the moldy chips. Mary simply picks up the bag and walks to the cashier without any hesitation or reaction. So, she is unlikely to be aware.

Step2-What will Mary likely do?:
    Since Mary is unaware of the moldy chips (as deduced in Step 1), she is likely to proceed with her initial action, which is to pay for the chips. Reporting the moldy chips would require her awareness of the issue, which is not present in this scenario. So, she will Pay for the chips.

Step3-Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as:
    Given that Mary is unaware of the mold, her action of paying for the chips is consistent with her knowledge of the situation. Her behavior is reasonable because she has no reason to suspect an issue with the chips. So, her behaviour is Reasonable.
So the answer is [A].

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Identify the fewest number of steps N (where 1 ≤ N ≤ 3) necessary to logically solve the problem, avoid unnecessary steps. 
    if question like "Is xxx likely to be aware that "xxx"?"
        N == 1, the output format is 
        Step1-Is xxx likely to be aware that "xxx"?:...
    if quetion like "What will xxx likely do?"
        N == 2, the output format is 
        Step1-Is xxx likely to be aware that "xxx"?:...
        Step2-What will xxx likely do?:...;
    if quetion like "xxx "xxx" and not "xxx". The behavior of xxx can be best described as:"
        N == 3, the output format is 
        Step1-Is xxx likely to be aware that "xxx"?:...
        Step2-What will xxx likely do?:...;
        Step3-xxx "xxx" and not "xxx". The behavior of xxx can be best described as:...;
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