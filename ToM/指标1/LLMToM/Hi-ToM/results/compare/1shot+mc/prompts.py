SystemEvaluatePrompt = \
"""
[Story]
Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.\nAbigail saw a mouse.\nThe carrot is in the red_envelope.\nNathan made no movements and stayed in the front_yard for 1 minute.\nNathan exited the front_yard.\nAvery saw a dog.\nEmma made no movements and stayed in the front_yard for 1 minute.\nEmma exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the red_container.\nIsabella exited the front_yard.\nAbigail moved the carrot to the red_envelope.\nAbigail exited the front_yard.\nNathan, Emma, Avery, Isabella and Abigail entered the waiting_room.\nIsabella publicly claimed that carrot is in the red_envelope.\nAbigail privately told Nathan that the carrot is in the red_envelope.\nEmma, Avery and Abigail entered the lounge.\nNathan saw a cat.\nThe eggplant is in the blue_drawer.\nEmma made no movements and stayed in the lounge for 1 minute.\nEmma exited the lounge.\nAvery moved the eggplant to the blue_pantry.\nAvery exited the lounge.\nAbigail moved the eggplant to the green_basket.\nAbigail exited the lounge.\nEmma, Avery and Abigail entered the waiting_room.\nEmma, Abigail, Avery and Isabella entered the front_yard.\nThe carrot is in the red_envelope.\nEmma moved the carrot to the red_drawer.\nEmma exited the front_yard.\nAbigail made no movements and stayed in the front_yard for 1 minute.\nAbigail exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the green_crate.\nIsabella exited the front_yard.\nEmma, Abigail, Avery and Isabella entered the waiting_room.\nEmma publicly claimed that carrot is in the red_container.\nIsabella privately told Nathan that the carrot is in the green_crate.

[Candidate Answers]
A. red_basket\nB. blue_crate\nC. red_envelope\nD. green_basket\nE. blue_suitcase\nF. blue_cupboard\nG. red_drawer\nH. blue_treasure_chest\nI. red_container\nJ. blue_drawer\nK. blue_pantry\nL. red_pantry\nM. red_bottle\nN. green_envelope\nO. green_crate\n

[Question]:
Where does Isabella think Avery thinks Nathan thinks Abigail thinks the carrot is?

[Output]:
[C]

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Directly output the answer index without any explanation. 
(2) Enclose the answer index in square brackets, the output format is: [answer index]
"""



UserEvaluatePrompt = """
[Story]
{Story}

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

[Question]
{Question}
"""

