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
Person A is Neila. Person B is Juanita. The item is towel. The location X is closet. The location Y is cabinet.

Step1-Where is the item currently? Where was the item previously?
    The item (towel) is currently in the cabinet because Neila moved it there.  
    The item (towel) was previously in the closet, as Neila and Juanita found it there.

Step2-Where would Person A look for the item? Where would Person B look for the item?
    Neila knows she moved the towel to the cabinet, so she would look in the cabinet.
    Juanita was not present when Neila moved the towel. Juanita last saw the towel in the closet, so she would look there.

Step3-Where would Person A think Person B would look for the item? Where would Person B think Person A would look for the item?
    Neila knows that Juanita did not see her move the towel. Therefore, Neila would think Juanita would look for the towel in the closet.
    Juanita does not know that Neila moved the towel. Based on what Juanita knows, she would assume Neila would look for the towel where it was last seen—the closet.

So, the answer is [B]

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Identify the fewest number of steps N (where 1 ≤ N ≤ 3) necessary to logically solve the problem, avoid unnecessary steps.

(2) Ensure the thought chain has exactly N steps. The output should strictly follow the example's format:
    if question like "where is xxx", N = 1, the output format is 
        Person A is ... Person B is ... The item is ... The location X is ... The location Y is ...
        Step1-Where is the item currently? Where was the item previously?

    if question like "Where would xxx look for the xxx?", N = 2, the output format is
        Person A is ... Person B is ... The item is ... The location X is ... The location Y is ...
        Step1-Where is the item currently? Where was the item previously?
        Step2-Where would Person A look for the item? Where would Person B look for the item?

    if question like "Where would xxx think xxx would look for the xxx?", N = 3, the output format is
        Person A is ... Person B is ... The item is ... The location X is ... The location Y is ...
        Step1-Where is the item currently? Where was the item previously?
        Step2-Where would Person A look for the item? Where would Person B look for the item?
        Step3-Where would Person A think Person B would look for the item? Where would Person B think Person A would look for the item?

(3) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""