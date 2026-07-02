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
Person A is Neila. Person B is Juanita. The container is a bag. Item X is plate. Item Y is vest.

Step1-What was in the container? What was supposed to be in the container?
    What was in the container: A vest was in the bag.
    What was supposed to be in the container (based on the label): A plate was supposed to be in the bag.

Step2-What would Person A expect to find in the container? What would Person B expect to find in the container?
    Neila (Person A), upon opening the bag, saw a vest inside. Neila would now expect to find a vest in the bag, as she knows what is actually inside.
    Juanita (Person B), upon seeing the bag with the "plate" label and not opening it herself, would expect to find a plate in the bag.

Step3-What would Person A think Person B would expect to find in the container? What would Person B think Person A would expect to find in the container? 
    Neila (Person A) would think that Juanita (Person B), upon seeing the "plate" label on the bag and not opening it, would expect to find a plate in the bag.
    Juanita (Person B), unaware that Neila opened the bag, would think Neila also expects the bag to contain a plate, based on the label.

So, the answer is [B]

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Identify the fewest number of steps N (where 1 ≤ N ≤ 3) necessary to logically solve the problem, avoid unnecessary steps.

(2) Ensure the thought chain has exactly N steps. The output should strictly follow the example's format:
    if question like "What was in the xxx" and "What was supposed to be in the xxx", N = 1, the output format is 
        Person A is ... Person B is ... The container is ... Item X is ... Item Y is ...
        Step1-What was in the container? What was supposed to be in the container?

    if question like "What would xxx expect to find in the xxx?", N = 2, the output format is
        Person A is ... Person B is ... The container is ... Item X is ... Item Y is ...
        Step1-What was in the container? What was supposed to be in the container?
        Step2-What would Person A expect to find in the container? What would Person B expect to find in the container?

    if question like "What would xxx think xxx would expect to find in the xxx?", N = 3, the output format is
        Person A is ... Person B is ... The container is ... Item X is ... Item Y is ...
        Step1-What was in the container? What was supposed to be in the container?
        Step2-What would Person A expect to find in the container? What would Person B expect to find in the container?
        Step3-What would Person A think Person B would expect to find in the container? What would Person B think Person A would expect to find in the container? 
        
(3) Finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
"""


UserEvaluatePrompt = """
[Story]
{Story}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""