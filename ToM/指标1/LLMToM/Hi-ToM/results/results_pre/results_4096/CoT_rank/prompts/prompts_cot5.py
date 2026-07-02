SystemEvaluatePrompt = \
"""
Read the following story and answer the multiple-choice question. Please only output the most likely answer index in the format: [[Answer Index]], for example, if the most likely answer option is '1. Handbag', then output '[[1]]'.

Note: You should assume the following. (1) An agent witnesses everything and every movements before exiting a location. (2) An agent A can infer another agent B's mental state only if A and B have been in the same location, or have private or public interactions. (3) Note that every agent tend to lie. What a character tells others doesn't affect his actual belief. An agent tend to trust a agent that exited the room later than himself. The exit order is known to all agents. (4) Agents in private communications know that others won't hear them, but they know that anyone can hear any public claims.
"""

SystemEvaluatePrompt_cot = \
"""
Read the following story and answer the multiple-choice question. 
Please think in exactly 5 steps:
Step 1. Read the story and extract the key details.
Step 2. Identify any possible connections or relationships between the facts.
Step 3. Break down the options and analyze how they relate to the details in the story.
Step 4. Evaluate each option in terms of how well it fits with the story's key points.
Step 5. Make a final decision and select the most likely answer based on the analysis.
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