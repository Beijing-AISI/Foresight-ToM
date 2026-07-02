SystemEvaluatePrompt = \
"""
[Story]
Nathan, Emma, Avery, Isabella and Abigail entered the front_yard.\nAbigail saw a mouse.\nThe carrot is in the red_envelope.\nNathan made no movements and stayed in the front_yard for 1 minute.\nNathan exited the front_yard.\nAvery saw a dog.\nEmma made no movements and stayed in the front_yard for 1 minute.\nEmma exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the red_container.\nIsabella exited the front_yard.\nAbigail moved the carrot to the red_envelope.\nAbigail exited the front_yard.\nNathan, Emma, Avery, Isabella and Abigail entered the waiting_room.\nIsabella publicly claimed that carrot is in the red_envelope.\nAbigail privately told Nathan that the carrot is in the red_envelope.\nEmma, Avery and Abigail entered the lounge.\nNathan saw a cat.\nThe eggplant is in the blue_drawer.\nEmma made no movements and stayed in the lounge for 1 minute.\nEmma exited the lounge.\nAvery moved the eggplant to the blue_pantry.\nAvery exited the lounge.\nAbigail moved the eggplant to the green_basket.\nAbigail exited the lounge.\nEmma, Avery and Abigail entered the waiting_room.\nEmma, Abigail, Avery and Isabella entered the front_yard.\nThe carrot is in the red_envelope.\nEmma moved the carrot to the red_drawer.\nEmma exited the front_yard.\nAbigail made no movements and stayed in the front_yard for 1 minute.\nAbigail exited the front_yard.\nAvery made no movements and stayed in the front_yard for 1 minute.\nAvery exited the front_yard.\nIsabella moved the carrot to the green_crate.\nIsabella exited the front_yard.\nEmma, Abigail, Avery and Isabella entered the waiting_room.\nEmma publicly claimed that carrot is in the red_container.\nIsabella privately told Nathan that the carrot is in the green_crate.

[Candidate Answers]
A. red_basket\nB. blue_crate\nC. red_envelope\nD. green_basket\nE. blue_suitcase\nF. blue_cupboard\nG. red_drawer\nH. blue_treasure_chest\nI. red_container\nJ. blue_drawer\nK. blue_pantry\nL. red_pantry\nM. red_bottle\nN. green_envelope\nO. green_crate\n

[Question]:
Where does Abigail thinks the carrot is?

[Output]:
Step1-Infer the carrot's last location:
   Initially, the carrot was in the red_envelope.Abigail moved it to the red_envelope again after Isabella had moved it to the red_container.Emma later moved the carrot to the red_drawer in the front_yard.Isabella moved it to the green_crate, but Abigail was not present to observe this.At the end of the story, the carrot’s final physical location is the green_crate, but Abigail did not witness this action.
Step2-Infer Abigail's belief:
    Abigail would believe the carrot is in the red_drawer because that was the last observed location of the carrot before she left.
So the answer is [G].

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Ensure the thought chain has exactly 2 steps. The output should strictly follow the example's format: 
    Step1-Infer the object's last location:...
    Step2-Infer person1's belief:...
(2) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
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

