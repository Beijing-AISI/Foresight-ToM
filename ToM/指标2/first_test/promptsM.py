SystemEvaluatePrompt = \
"""
The story is about two people (Person A and Person B) found an item in location X. Person B left the room and
Person A moved the item to location Y.

[Story]
Neila and Juanita were hanging out in the attic. They saw a closet and a cabinet. They found a towel in the closet. Juanita left the attic. Neila moved the towel to the cabinet. After Juanita came back to the attic, where was the towel previously?

[Candidate Answers]
A. cabinet
B. closet

Before answer the question in the story, several questions will be given.

[Question]
2+2=?

[Output]
4

Finally, answer the question in the story when receiving the specific instruction.

[Instruction]
Now answer the question in the story.

[Output]
Person A is Neila. Person B is Juanita. The item is towel. The location X is closet. The location Y is cabinet.
So, the answer is [B]

Read and understand the examples above. 
Story and questions are given and outputs are required.
Strictly follow the Note to provide outputs.

Note:
(1) Before actually answer the question in the story, several other questions will be given. Make sures these tasks be solved first. 
    Do not answer the question in the story until asked to.
    
(2) Only answer the given question each time. Do not generate additional content.

(3) Answer the question in the story when asked by "Now answer the question in the story.". The output should strictly follow the format:
    Person A is ... Person B is ... The item is ... The location X is ... The location Y is ...

(4) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""