SystemPrompt = \
    """
    [Story]
    Neila and Juanita were hanging out in the attic. They saw a closet and a cabinet. They found a towel in the closet. Juanita left the attic. Neila moved the towel to the cabinet.

    [Requirement]
    What related questions can be raised based on this story?

    [Output]
    Generally speaking, what can be possible found in the closet?
    For an average household, what might be placed in the cabinet?
    What kind of experience could living in an attic be?
    What idea might Nella have had in mind to move the towels to the cabinet?
    What might two people do in the attic?

    Read and understand the examples above. Then a new story will be given, strictly follow the Note to provide outputs.

    Note:
    (1) The generated questions should related to the given story.

    (2) Generate no less than 8 and no more than 16 questions. 
        Make sure that each question ends in a question mark '?'. And the questions are separated by line breaks.
    """

UserPrompt = """
[Story]
{Story}

[Requirement]
What related questions can be raised based on this story?
"""