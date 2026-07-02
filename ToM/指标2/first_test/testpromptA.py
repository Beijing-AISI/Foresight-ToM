SystemPrompt = \
    """
    The story is about two people (Person A and Person B) found an item in location X. Person B left the room and
    Person A moved the item to location Y.
    
    [Story]
    Neila and Juanita were hanging out in the attic. They saw a closet and a cabinet. They found a towel in the closet. Juanita left the attic. Neila moved the towel to the cabinet.
    
    [Question]
    Where does the phrase 'to be or not to be' come from?
    
    [Output]
    The phrase 'to be or not to be' comes from William Shakespeare's play Hamlet.
    
    [Question]
    After Juanita came back to the attic, where was the towel previously?
        
    [Candidate Answers]
    A. cabinet
    B. closet
    
    [Output]
    Person A is Neila. Person B is Juanita. The item is towel. The location X is closet. The location Y is cabinet.
    So, the answer is [B]
    
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
