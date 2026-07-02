SystemEvaluatePrompt= """
Below is a multiple-choice question with a story and several answer options. Based on the content of the story and the given question, please infer the most likely answer and output the answer index.
Note:
(1) Ensure the thought chain has exactly 5 steps, the output format is: Step1: xxx; Step2: xxx; Step3: xxx; Step4: xxx; Step5: xxx;
(2) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""

UserEvaluatePrompt = """
[Story]
{Story}

[Question]
{Question}

[Choices]
{a}. {choice_a}
{b}. {choice_b}
"""
