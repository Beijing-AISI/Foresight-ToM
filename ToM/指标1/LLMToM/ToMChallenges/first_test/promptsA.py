SystemEvaluatePrompt = \
"""
The story is about two people (Person A and Person B) found an item in location X. Person B left the room and
Person A moved the item to location Y.

[Story]
Neila and Juanita were hanging out in the attic. They saw a closet and a cabinet. They found a towel in the closet. Juanita left the attic. Neila moved the towel to the cabinet. After Juanita came back to the attic, where was the towel previously?

[Candidate Answers]
A. cabinet
B. closet

[Output]
Person A is Neila. Person B is Juanita. The item is towel. The location X is closet. The location Y is cabinet.
So, the answer is [B]

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Ensure the thought chain has exactly 1 steps. The output should strictly follow the example's format:
    Person A is ... Person B is ... The item is ... The location X is ... The location Y is ...

(2) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""