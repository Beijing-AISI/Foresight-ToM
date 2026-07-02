SystemEvaluatePrompt = """
Read the following story and answer the multiple-choice question. Please only output the most likely answer index in the format: [[Answer Index]], for example, if the most likely answer option is '1. Handbag', then output '[[1]]'.

Note: You should assume the following. (1) An agent witnesses everything and every movements before exiting a location. (2) An agent A can infer another agent B's mental state only if A and B have been in the same location, or have private or public interactions. (3) Note that every agent tend to lie. What a character tells others doesn't affect his actual belief. An agent tend to trust a agent that exited the room later than himself. The exit order is known to all agents. (4) Agents in private communications know that others won't hear them, but they know that anyone can hear any public claims.
"""

SystemEvaluatePrompt_cot = """
[Story]
Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.\nAbigail saw a mouse.\nThe carrot is in the red_envelope.\nNathan made no movements and stayed in the front_yard for 1 minute.\nNathan exited the front_yard.\nAvery saw a dog.\nEmma made no movements and stayed in the front_yard for 1 minute.\nEmma exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the red_container.\nIsabella exited the front_yard.\nAbigail moved the carrot to the red_envelope.\nAbigail exited the front_yard.\nNathan, Emma, Avery, Isabella and Abigail entered the waiting_room.\nIsabella publicly claimed that carrot is in the red_envelope.\nAbigail privately told Nathan that the carrot is in the red_envelope.\nEmma, Avery and Abigail entered the lounge.\nNathan saw a cat.\nThe eggplant is in the blue_drawer.\nEmma made no movements and stayed in the lounge for 1 minute.\nEmma exited the lounge.\nAvery moved the eggplant to the blue_pantry.\nAvery exited the lounge.\nAbigail moved the eggplant to the green_basket.\nAbigail exited the lounge.\nEmma, Avery and Abigail entered the waiting_room.\nEmma, Abigail, Avery and Isabella entered the front_yard.\nThe carrot is in the red_envelope.\nEmma moved the carrot to the red_drawer.\nEmma exited the front_yard.\nAbigail made no movements and stayed in the front_yard for 1 minute.\nAbigail exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the green_crate.\nIsabella exited the front_yard.\nEmma, Abigail, Avery and Isabella entered the waiting_room.\nEmma publicly claimed that carrot is in the red_container.\nIsabella privately told Nathan that the carrot is in the green_crate.

[Candidate Answers]\n1. red_basket\n2. blue_crate\n3. red_envelope\n4. green_basket\n5. blue_suitcase\n6. blue_cupboard\n7. red_drawer\n8. blue_treasure_chest\n9. red_container\n10. blue_drawer\n11. blue_pantry\n12. red_pantry\n13. red_bottle\n14. green_envelope\n15. green_crate\n

Note: Output controls in 8000 token. Let's think step by step. Please first judge the question in order 0-4 and read the corresponding analysis example. Output the answer in the format:[[Answer index]].

[Order_0]:
    Where is the carrot really?
[Answer_0]:
    step 0: Read the text, select the object last relevant movement:
        Isabella moved the carrot to the green_crate.
    step 1: where is the carrot really:
        The last relevant is "Isabella moved the carrot to the green_crate.", so the carrot is in the green_crate.
    step 2: Conclusion all the above steps, the carrot is in the green_crate. So the answer is [[15]].

[Order_1]:
    Where does Abigail really think the carrot is?
[Answer_1]:
    step 0: Read the text, Select the paragraphs where both Abigail and the carrot appear in the same room, and remove "claim","tell", any unrelated details.
        Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.
        The carrot is in the red_envelope.
        Nathan exited the front_yard.
        Emma exited the front_yard.
        Avery exited the front_yard.
        Isabella moved the carrot to the red_container.
        Isabella exited the front_yard.
        Abigail moved the carrot to the red_envelope.
        Abigail exited the front_yard.
        Nathan, Emma, Avery, Isabella and Abigail entered the waiting_room.
        Emma, Abigail, Avery and Isabella entered the front_yard.
        The carrot is in the red_envelope.
        Emma moved the carrot to the red_drawer.
        Emma exited the front_yard.
        Abigail exited the front_yard.
        Avery exited the front_yard.
        Isabella moved the carrot to the green_crate.
        Isabella exited the front_yard.
        Emma, Abigail, Avery and Isabella entered the waiting_room.
    step 1: Where does Abigail really think the carrot is:
        Abigail see the last relevant is "Emma moved the carrot to the red_drawer.", so Abigail thinks the carrot is in the red_drawer.
    step 2: Conclusion all the above steps, Abigail really thinks the carrot is in the red_drawer. So the answer is [[7]].

[Order_2]:
    Where does Nathan think Abigail thinks the carrot is?
[Answer_2]:
    step 0: Read the text, Select the paragraphs where both Nathan, Abigail, carrot appear in the same room, and remove "claim","tell", any unrelated details.
        Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.
        The carrot is in the red_envelope.
        Nathan exited the front_yard.
        Emma exited the front_yard.
        Avery exited the front_yard.
        Isabella moved the carrot to the red_container.
        Isabella exited the front_yard.
        Abigail moved the carrot to the red_envelope.
        Abigail exited the front_yard.
        Nathan, Emma, Avery, Isabella and Abigail entered the waiting_room.
    step 1: Where does Nathan thinks the carrot is: 
        Nathan see the last relevant is "The carrot is in the red_envelope.". so Nathan thinks the carrot is in the red_envelope.
    step 2: where does Nathan thinks Abigail thinks the carrot is:
        Abigail exit later than Nathan, so (Nathan, Abigail) is based on Nathan's belief. Nathan see the last relevant is "The carrot is in the red_envelope.", so (Nathan, Abigail) thinks the carrot is in the red_envelope.
    step 3: Conclusion all the above steps, Nathan thinks Abigail thinks the carrot is in the red_envelope. So the answer is [[3]].

[Order_3]:
    Where does Avery think Nathan thinks Abigail thinks the carrot is?
[Answer_3]:
    step 0: Read the text, Select the paragraphs where both Avery, Nathan, Abigail, carrot appear in the same room, and remove "claim","tell", any unrelated details.
        Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.
        The carrot is in the red_envelope.
        Nathan exited the front_yard.
        Emma exited the front_yard.
        Avery exited the front_yard.
        Isabella moved the carrot to the red_container.
        Isabella exited the front_yard.
        Abigail moved the carrot to the red_envelope.
        Abigail exited the front_yard.
        Nathan, Emma, Avery, Isabella and Abigail entered the waiting_room.
    step 1: Where does Avery thinks the carrot is:
        Avery see the last relevant is "The carrot is in the red_envelope.", so Avery thinks the carrot is in the red_envelope.
    step 2: Where does Avery thinks Nathan thinks the carrot is:
        Nathan exits earlier than Avery, so (Avery, Nathan) is based on Nathan's belief. Nathan see the last relevant is "The carrot is in the red_envelope.", so (Avery, Nathan) thinks the carrot is in the red_envelope.
    step 3: where does Avery thinks Nathan thinks Abigail thinks the carrot is:
        Abigail exits later than Nathan, so (Avery, Nathan, Abigail) is based on Nathan's belief. Nathan see the last relevant is "The carrot is in the red_envelope.", so (Avery, Nathan, Abigail) thinks the carrot is in the red_envelope.
    step 4: Conclusion all the above steps, Avery thinks Nathan thinks Abigail thinks the carrot is in the red_envelope. So the answer is [[3]].

[Order_4]
    Where does Isabella think Avery thinks Nathan thinks Abigail thinks the carrot is?
[Answer_4]
    step 0: Read the text, Select the paragraphs where both Isabella, Avery, Nathan, Abigail, carrot appear in the same room, and remove "claim","tell", any unrelated details.
        Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.
        The carrot is in the red_envelope.
        Nathan exited the front_yard.
        Emma exited the front_yard.
        Avery exited the front_yard.
        Isabella moved the carrot to the red_container.
        Isabella exited the front_yard.
        Abigail moved the carrot to the red_envelope.
        Abigail exited the front_yard.
        Nathan, Emma, Avery, Isabella and Abigail entered the waiting_room.
    step 1: Where does Isabella thinks the carrot is:
        Isabella see the last relevant is "Isabella moved the carrot to the red_container.", so Isabella thinks the carrot is in the red_container.
    step 2: Where does Isabella thinks Avery thinks the carrot is:
        Avery exits earlier than Isabella, so (Isabella, Avery) is based on Avery's belief. Avery see the last relevant is "The carrot is in the red_envelope." so (Isabella, Avery) thinks the carrot is in the red_envelope.
    step 3: where does Isabella thinks Avery thinks Nathan thinks the carrot is:
        Nathan exits earlier than Avery, so (Isabella, Avery, Nathan) is based on Nathan's belief. Nathan see the last relevant is "The carrot is in the red_envelope." so (Isabella, Avery, Nathan) thinks the carrot is in the red_envelope.
    step 4: where does Isabella thinks Avery thinks Nathan thinks Abigail thinks the carrot is:
        Abigail exits later than Nathan, so (Isabella, Avery, Nathan, Abigail) is based on Nathan's belief. Nathan see the last relevant is "The carrot is in the red_envelope." so (Isabella, Avery, Nathan, Abigail) thinks the carrot is in the red_envelope.
    step 5: Conclusion all the above steps, Isabella thinks Avery thinks Nathan thinks Abigail thinks the carrot is in the red_envelope. So the answer is [[3]].
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
