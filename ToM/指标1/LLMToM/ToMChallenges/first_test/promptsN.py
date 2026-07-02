SystemEvaluatePrompt = \
"""
The story is about Person A found a container. The label on the container says item X, but there’s no item X in the
container. Person A opened the container and found item Y. Later, Person B entered the room and saw the container.

[Story]
Neila found a bag in the attic. The label on the bag says plate. Neila couldn’t see what was inside the bag. Neila opened the bag and found a vest. There is no plate in the bag. Neila closed the bag and put it back. Where was supposed to be in the bag?

[Candidate Answers]
A. vest
B. plate

Before answer the question in the story, several questions will be given.

[Question]
2+2=?

[Output]
4

Finally, answer the question in the story when receiving the specific instruction.

[Instruction]
Now answer the question in the story.

[Output]
Person A is Neila. Person B is Juanita. The container is a bag. Item X is plate. Item Y is vest.
So, the answer is [B]

Read and understand the examples above. 
Story and questions are given and outputs are required.
Strictly follow the Note to provide outputs.

Note:
(1) Before actually answer the question in the story, several other questions will be given. Make sures these tasks be solved first. 
    Do not answer the question in the story until asked to.
    
(2) Only answer the given question each time. Do not generate additional content.

(3) Answer the question in the story when asked by "Now answer the question in the story.". The output should strictly follow the example's format:
    Person A is ... Person B is ... The container is ... Item X is ... Item Y is ...

(4) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""

UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""