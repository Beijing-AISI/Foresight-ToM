SystemPrompt = \
    """
    The story is about Person A found a container. The label on the container says item X, but there’s no item X in the
    container. Person A opened the container and found item Y. Later, Person B entered the room and saw the container.
    
    [Story]
    Neila found a bag in the attic. The label on the bag says plate. Neila couldn’t see what was inside the bag. Neila opened the bag and found a vest. There is no plate in the bag. Neila closed the bag and put it back.
    
    [Question]
    Where does the phrase 'to be or not to be' come from?
    
    [Output]
    The phrase 'to be or not to be' comes from William Shakespeare's play Hamlet.
    
    [Question]
    Where was supposed to be in the bag?
    
    [Candidate Answers]
    A. vest
    B. plate
    
    [Output]
    Person A is Neila. Person B is Juanita. The container is a bag. Item X is plate. Item Y is vest.
    So, the answer is [A]
    
    Read and understand the examples above. 
    Story and questions are given and outputs are required.
    Strictly follow the Note to provide outputs.
    
    Note:
    (1) When there are no [Candidate Answers] following the [Question], answer the question freely, but be careful not exceed 200 words.
    
    (2) When there are [Candidate Answers] following the [Question], The output should strictly follow the format:
        Person A is ... Person B is ... The item is ... The location X is ... The location Y is ...
        And finally, enclose the answer index in square brackets, the output format is: so the answer is [answer index].
    """

FirstPrompt = """
[Story]
{Story}

[Question]
{Question}
"""

LastPrompt = """
[Question]
{Question}

[Candidate Answers]
{a}. {choice_a}
{b}. {choice_b}
"""
