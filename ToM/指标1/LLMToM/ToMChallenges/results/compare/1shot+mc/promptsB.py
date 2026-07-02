SystemEvaluatePrompt = \
"""
The story is about Person A found a container. The label on the container says item X, but there’s no item X in the container. Person A opened the container and found item Y. Later, Person B entered the room and saw the container.

[Story]
Neila found a bag in the attic. The label on the bag says plate. Neila couldn’t see what was inside the bag. Neila opened the bag and found a vest. There is no plate in the bag. Neila closed the bag and put it back. Juanita entered the attic and saw the bag. What would Juanita think Neila would expect to find in the bag?

[Candidate Answers]
A. vest
B. plate

[Output]
[B]

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
"""