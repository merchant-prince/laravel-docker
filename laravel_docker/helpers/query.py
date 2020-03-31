class Question:
    """
    This class is used to ask questions to the user.

    Attributes:
        question (string):
            The question to ask.
            e.g.: "What is your name?"

        validator (callable):
            The validation function. This is normally a lambda function which
            returns a ValueError when the validation fails, and the answer
            otherwise.
            e.g.: lambda a: a if len(a) < 33 else ValueError("Oops...")

        max_tries (int):
            The maximum number of times to try a question if its validation
            fails.

        answer (str):
            The answer to the question as entered by the user.
    """


    def __init__(self, question, validator = lambda a: a, max_tries = 3):
        self.question = question
        self.max_tries = max_tries
        self.answer = None

        if not callable(validator):
            raise ValueError("The validator provided is not a callable.")

        self.validator = validator


    def ask(self):
        """
        Ask the question to the user.

        Returns:
            str: The answer entered by the user.
        """

        for try_count in range(0, self.max_tries):
            answer = input(f"{self.question} ({try_count}/{self.max_tries}): ")

            try:
                validated_answer = self.validator(answer)

                if isinstance(validated_answer, ValueError):
                    raise validated_answer
            except ValueError as exception:
                print(exception)
                continue
            else:
                break
        else:
            raise ValueError("You entered the wrong input too many times.")

        return str(self)
