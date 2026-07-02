SystemEvaluatePrompt = \
"""
Read the following story and answer the multiple-choice question. Please only output the most likely answer index in the format: [[Answer Index]], for example, if the most likely answer option is '1. Handbag', then output '[[1]]'.

Note: You should assume the following. (1) An agent witnesses everything and every movements before exiting a location. (2) An agent A can infer another agent B's mental state only if A and B have been in the same location, or have private or public interactions. (3) Note that every agent tend to lie. What a character tells others doesn't affect his actual belief. An agent tend to trust a agent that exited the room later than himself. The exit order is known to all agents. (4) Agents in private communications know that others won't hear them, but they know that anyone can hear any public claims.
"""

SystemEvaluatePrompt_cot = \
"""
Read the following story and answer the multiple-choice question. 
Please think in exactly 7 steps:
Step 1. Understand the context of the story and identify the main events.
Step 2. Recognize any cause-and-effect relationships between the events.
Step 3. Identify the relevant details for answering the question.
Step 4. Assess each of the answer options based on the story’s details.
Step 5. Examine any logical inconsistencies between the options and the facts.
Step 6. Consider possible alternatives or hidden assumptions in each option.
Step 7. Make a decision on the most likely answer based on the complete analysis.
Finally, output the most likely answer index in the format: [[Answer Index]]. For example, if the most likely answer option is '1. Handbag', then output '[[1]]'.

# Note: You should assume the following. (1) An agent witnesses everything and every movements before exiting a location. (2) An agent A can infer another agent B's mental state only if A and B have been in the same location, or have private or public interactions. (3) Note that every agent tend to lie. What a character tells others doesn't affect his actual belief. An agent tend to trust a agent that exited the room later than himself. The exit order is known to all agents. (4) Agents in private communications know that others won't hear them, but they know that anyone can hear any public claims.

Please ensure the result is within 4096 tokens.
"""

UserEvaluatePrompt = \
"""[Story]
{Story}

[Question]
{Question}

[Candidate Answers]
1. {choice_a}
2. {choice_b}
3. {choice_c}
4. {choice_d}
5. {choice_e}
6. {choice_f}
7. {choice_g}
8. {choice_h}
9. {choice_i}
10. {choice_j}
11. {choice_k}
12. {choice_l}
13. {choice_m}
14. {choice_n}
15. {choice_o}
"""