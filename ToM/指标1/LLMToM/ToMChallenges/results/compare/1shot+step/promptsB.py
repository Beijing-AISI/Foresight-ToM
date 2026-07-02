SystemEvaluatePrompt = \
"""
The story is about Person A found a container. The label on the container says item X, but there’s no item X in the
container. Person A opened the container and found item Y. Later, Person B entered the room and saw the container.

[Story]
Neila found a bag in the attic. The label on the bag says plate. Neila couldn’t see what was inside the bag. Neila opened the bag and found a vest. There is no plate in the bag. Neila closed the bag and put it back. Juanita entered the attic and saw the bag. What would Juanita think Neila would expect to find in the bag?

[Candidate Answers]
A. vest
B. plate

[Output]
Step 1: Neila found a bag labeled "plate" and initially couldn’t see inside. Based on the label, Neila would naturally expect to find a plate in the bag.
Step 2: When Neila opened the bag, she discovered a vest instead, realizing there was no plate. She then closed the bag and put it back.
Step 3: Juanita enters the attic and sees the bag. Since Juanita has not opened the bag, she has no knowledge of its contents beyond what the label indicates. Juanita would expect the bag to contain a plate based on the label.

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