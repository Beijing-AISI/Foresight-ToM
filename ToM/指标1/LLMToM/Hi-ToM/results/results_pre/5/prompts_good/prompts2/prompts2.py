SystemEvaluatePrompt = """
Read the following story and answer the multiple-choice question. Please only output the most likely answer index in the format: [[Answer Index]], for example, if the most likely answer option is '1. Handbag', then output '[[1]]'.

Note: You should assume the following. (1) An agent witnesses everything and every movements before exiting a location. (2) An agent A can infer another agent B's mental state only if A and B have been in the same location, or have private or public interactions. (3) Note that every agent tend to lie. What a character tells others doesn't affect his actual belief. An agent tend to trust a agent that exited the room later than himself. The exit order is known to all agents. (4) Agents in private communications know that others won't hear them, but they know that anyone can hear any public claims.
"""

SystemEvaluatePrompt_cot = """
[Story]
Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.\nAbigail saw a mouse.\nThe carrot is in the red_envelope.\nNathan made no movements and stayed in the front_yard for 1 minute.\nNathan exited the front_yard.\nAvery saw a dog.\nEmma made no movements and stayed in the front_yard for 1 minute.\nEmma exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the red_container.\nIsabella exited the front_yard.\nAbigail moved the carrot to the red_envelope.\nAbigail exited the front_yard.\nNathan, Emma, Avery, Isabella and Abigail entered the waiting_room.\nIsabella publicly claimed that carrot is in the red_envelope.\nAbigail privately told Nathan that the carrot is in the red_envelope.\nEmma, Avery and Abigail entered the lounge.\nNathan saw a cat.\nThe eggplant is in the blue_drawer.\nEmma made no movements and stayed in the lounge for 1 minute.\nEmma exited the lounge.\nAvery moved the eggplant to the blue_pantry.\nAvery exited the lounge.\nAbigail moved the eggplant to the green_basket.\nAbigail exited the lounge.\nEmma, Avery and Abigail entered the waiting_room.\nEmma, Abigail, Avery and Isabella entered the front_yard.\nThe carrot is in the red_envelope.\nEmma moved the carrot to the red_drawer.\nEmma exited the front_yard.\nAbigail made no movements and stayed in the front_yard for 1 minute.\nAbigail exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the green_crate.\nIsabella exited the front_yard.\nEmma, Abigail, Avery and Isabella entered the waiting_room.\nEmma publicly claimed that carrot is in the red_container.\nIsabella privately told Nathan that the carrot is in the green_crate.

[Candidate Answers]\n1. red_basket\n2. blue_crate\n3. red_envelope\n4. green_basket\n5. blue_suitcase\n6. blue_cupboard\n7. red_drawer\n8. blue_treasure_chest\n9. red_container\n10. blue_drawer\n11. blue_pantry\n12. red_pantry\n13. red_bottle\n14. green_envelope\n15. green_crate\n

[Question]:
    Where does Abigail really think the carrot is?
[Answer]:
Reason Based on Agent A's Actions
    bigail's Actions: Throughout the story, Abigail interacts with the carrot several times. Initially, she sees the carrot in the red envelope. She witnesses Isabella moving the carrot to the red container but then moves it back to the red envelope herself. Towards the end of the story, after multiple movements by other characters, she is present when Emma moves the carrot to the red drawer, and finally, Isabella moves it to the green crate.
Conclude Where Agent A Believes the Object Is
    Abigail's Belief: The last action that Abigail directly observes is Emma moving the carrot to the red drawer. There is no indication that Abigail is aware of the subsequent movement of the carrot to the green crate by Isabella, as the narrative does not explicitly state that Abigail saw this action. Therefore, based on the sequence of events Abigail is aware of, she most likely believes the carrot is still in the red drawer where Emma last placed it.Following the sequence of Abigail's observations and the actions she is privy to, it can be concluded that Abigail believes the carrot is in the red drawer. Thus, the answer is [[7]].

Output controls in 4096 token and Output the answer in the format:[[Answer index]]. Let's think step by step. 
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
