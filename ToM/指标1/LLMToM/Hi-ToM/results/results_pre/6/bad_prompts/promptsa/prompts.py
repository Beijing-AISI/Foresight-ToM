SystemEvaluatePrompt = \
"""
Below is a multiple-choice question with a story and several answer options. Based on the content of the story and the given question, please infer the most likely answer and output the answer index.
Note:
(1) Identify the fewest number of steps N (where 1 ≤ N ≤ 5) necessary to logically solve the problem, ensuring no unnecessary steps are included.
(2) Ensure the thought chain has exactly N steps, the output format is: Step1: xxx; ... StepN: xxx;
(3) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
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
