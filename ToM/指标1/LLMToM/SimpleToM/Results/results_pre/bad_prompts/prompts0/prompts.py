SystemEvaluatePrompt= """
Below is a multiple-choice question with a story and several answer options. Based on the content of the story and the given question, please infer the most likely answer and output the answer index.
Note:
(1) Directly output the answer index without any explanation. 
(2) Enclose the answer index in square brackets, the output format is: [answer index].
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
