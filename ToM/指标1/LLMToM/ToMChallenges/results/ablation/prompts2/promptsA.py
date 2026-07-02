SystemEvaluatePrompt = \
"""
The story is about two people (Person A and Person B) found an item in location X. Person B left the room and
Person A moved the item to location Y.

[Story]
Neila and Juanita were hanging out in the attic. They saw a closet and a cabinet. They found a towel in the closet. Juanita left the attic. Neila moved the towel to the cabinet. After Juanita came back to the attic, where would Juanita look for the towel?

[Candidate Answers]
A. cabinet
B. closet

[Output]
Person A is Neila. Person B is Juanita. The item is towel. The location X is closet. The location Y is cabinet.

Step1-Where is the item currently? Where was the item previously?
    The item (towel) is currently in the cabinet (Location Y).
    The item was previously in the closet (Location X).

Step2-Where would Person A look for the item? Where would Person B look for the item?
    Neila (Person A), who moved the towel, knows it is now in the cabinet. Therefore, she would look for the towel in the cabinet.
    Juanita (Person B) left the attic before the towel was moved. She would not know that the towel has been moved to the cabinet. She still believes the towel is in the closet (Location X).

So, the answer is [B]

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Ensure the thought chain has exactly 2 steps. The output should strictly follow the example's format:
    Person A is ... Person B is ... The item is ... The location X is ... The location Y is ...
    Step1-Where is the item currently? Where was the item previously?
    Step2-Where would Person A look for the item? Where would Person B look for the item?

(2) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""