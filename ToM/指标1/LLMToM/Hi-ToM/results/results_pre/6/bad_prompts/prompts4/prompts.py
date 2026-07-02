SystemEvaluatePrompt = \
"""
Below is a multiple-choice question with a story and several answer options. Based on the content of the story and the given question, please infer the most likely answer and output the answer index.
Note:
(1) Ensure the thought chain has exactly 4 steps, the output format is: Step1: xxx; Step2: xxx; Step3: xxx; Step4: xxx;
(2) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Question]
{Question}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
{c}. {choice_c}
{d}. {choice_d}
{e}. {choice_e}
{f}. {choice_f}
{g}. {choice_g}
{h}. {choice_h}
{i}. {choice_i}
{j}. {choice_j}
{k}. {choice_k}
{l}. {choice_l}
{m}. {choice_m}
{n}. {choice_n}
{o}. {choice_o}
"""
