SystemEvaluatePrompt = """
Read the following story and answer the multiple-choice question. Please only output the most likely answer index in the format: [[Answer Index]], for example, if the most likely answer option is '1. Handbag', then output '[[1]]'.

Note: You should assume the following. (1) An agent witnesses everything and every movements before exiting a location. (2) An agent A can infer another agent B's mental state only if A and B have been in the same location, or have private or public interactions. (3) Note that every agent tend to lie. What a character tells others doesn't affect his actual belief. An agent tend to trust a agent that exited the room later than himself. The exit order is known to all agents. (4) Agents in private communications know that others won't hear them, but they know that anyone can hear any public claims.
"""

SystemEvaluatePrompt_cot = """
Note: Output controls in 8000 token and Output the answer in the format:[[Answer index]]. Let's think step by step. 

[Story]
Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.\nAbigail saw a mouse.\nThe carrot is in the red_envelope.\nNathan made no movements and stayed in the front_yard for 1 minute.\nNathan exited the front_yard.\nAvery saw a dog.\nEmma made no movements and stayed in the front_yard for 1 minute.\nEmma exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the red_container.\nIsabella exited the front_yard.\nAbigail moved the carrot to the red_envelope.\nAbigail exited the front_yard.\nNathan, Emma, Avery, Isabella and Abigail entered the waiting_room.\nIsabella publicly claimed that carrot is in the red_envelope.\nAbigail privately told Nathan that the carrot is in the red_envelope.\nEmma, Avery and Abigail entered the lounge.\nNathan saw a cat.\nThe eggplant is in the blue_drawer.\nEmma made no movements and stayed in the lounge for 1 minute.\nEmma exited the lounge.\nAvery moved the eggplant to the blue_pantry.\nAvery exited the lounge.\nAbigail moved the eggplant to the green_basket.\nAbigail exited the lounge.\nEmma, Avery and Abigail entered the waiting_room.\nEmma, Abigail, Avery and Isabella entered the front_yard.\nThe carrot is in the red_envelope.\nEmma moved the carrot to the red_drawer.\nEmma exited the front_yard.\nAbigail made no movements and stayed in the front_yard for 1 minute.\nAbigail exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the green_crate.\nIsabella exited the front_yard.\nEmma, Abigail, Avery and Isabella entered the waiting_room.\nEmma publicly claimed that carrot is in the red_container.\nIsabella privately told Nathan that the carrot is in the green_crate.

[Candidate Answers]\n1. red_basket\n2. blue_crate\n3. red_envelope\n4. green_basket\n5. blue_suitcase\n6. blue_cupboard\n7. red_drawer\n8. blue_treasure_chest\n9. red_container\n10. blue_drawer\n11. blue_pantry\n12. red_pantry\n13. red_bottle\n14. green_envelope\n15. green_crate\n

[Question]:
    Where does Isabella think Avery thinks Nathan thinks Abigail thinks the carrot is?
[Answer]:
Determine each agent's initial belief and object position changes: 
    Nathan, Emma, Avery, Isabella, and Abigail entered the front yard. The carrot was initially in the red envelope. Nathan, Emma, and Avery left the front yard one after another. Isabella moved the carrot to the red container and then left the front yard. Abigail moved the carrot back to the red envelope and then left the front yard.

Infer agent D's belief: 
    Isabella saw the carrot last moved to the red container, so Isabella believes the carrot is in the red container.

Infer agent C's belief: 
    Avery left earlier than Isabella, so Isabella believes Avery's belief is based on the situation before he left. Avery saw the carrot last moved to the red envelope, so Isabella believes Avery thinks the carrot is in the red envelope.

Infer agent B's belief: 
    Nathan left earlier than Avery, so Avery's belief is based on the situation before he left. Nathan saw the carrot last moved to the red envelope, so Isabella believes Avery thinks Nathan thinks the carrot is in the red envelope.

Infer agent A's belief about what agent B thinks agent C believes agent D believes: 
    Abigail left later than Nathan, so Nathan's belief is based on the situation before he left. Nathan saw the carrot last moved to the red envelope, so Isabella believes Avery thinks Nathan thinks Abigail thinks the carrot is in the red envelope. Therefore, the answer is [[3]].
"""

UserEvaluatePrompt = """
[Story]
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
