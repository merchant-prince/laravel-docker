from scripting_utilities.print import Print


class Question:
    """
    This class is used to ask questions to the user.

    Attributes:
        question (string):
            The question to ask.
            e.g.: "What is your name?"

        validators ([callable]):
            The validation function. This is normally a lambda function which
            returns a ValueError when the validation fails, and the answer
            otherwise.
            e.g.: lambda a: a if len(a) < 33 else ValueError("Oops...")

        default_answer (str):
            The default answer to the question. This is used if the user enters
            an EOL as the first character to the question.

        max_tries (int):
            The maximum number of times to try a question if its validation
            fails.

        answer (str):
            The answer to the question as entered by the user.
    """


    def __init__(self, question, validators = [lambda a: a], default_answer = None, max_tries = 3):
        self.question = question
        self.max_tries = max_tries
        self.default_answer = default_answer
        self.answer = None

        for validator in validators:
            if not callable(validator):
                raise ValueError("One of the validators provided is not a callable.")

        self.validators = validators

        self._ask()


    def _ask(self):
        """
        Ask the question to the user.
        """

        for try_count in range(0, self.max_tries):
            answer = input(self.question)

            if answer == '' and self.default_answer is not None:
                answer = self.default_answer

            try:
                for validator in self.validators:
                    validator(answer)

                self.answer = answer
            except ValueError as exception:
                Print.eol()
                Print.warning(exception)
                Print.eol(2)

                continue
            else:
                break
        else:
            raise ValueError("You have entered the wrong input too many times.")


    def __str__(self):
        return self.answer
