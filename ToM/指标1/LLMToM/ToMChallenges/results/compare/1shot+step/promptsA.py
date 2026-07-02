SystemEvaluatePrompt = \
"""
The story is about two people (Person A and Person B) found an item in location X. Person B left the room and
Person A moved the item to location Y.

[Story]
Neila and Juanita were hanging out in the attic. They saw a closet and a cabinet. They found a towel in the closet. Juanita left the attic. Neila moved the towel to the cabinet. After Juanita came back to the attic, where would Juanita think Neila would look for the towel?

[Candidate Answers]
A. cabinet
B. closet

[Output]
Step 1: Juanita and Neila found the towel in the closet, so both of them initially know its location is the closet.
Step 2: Juanita left the attic, so she is unaware of what happened after she left.
Step 3: Neila moved the towel to the cabinet, but Juanita does not know this because she was not present.
Step 4: When Juanita returns to the attic, she would still believe the towel is in the closet since she has no knowledge of Neila's action.

So the answer is [B].

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Think step by step and output the thinking process.
(2) Enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""