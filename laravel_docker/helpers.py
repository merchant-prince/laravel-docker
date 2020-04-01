import os
import re
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




class Validation:
    """
    This class is used to validate answers collected from the users.
    """


    @staticmethod
    def directory_existence(name):
        if name in os.listdir() and os.path.isdir(name):
            raise ValueError("Another directory with the same name already exists in the current directory.")


    @staticmethod
    def is_alphabetic(value):
        if not value.isalpha():
            raise ValueError(f"The provided value is not alphabetic.")


    @staticmethod
    def is_alphanumeric(value):
        if not value.isalnum():
            raise ValueError("The provided value is not alphanumeric.")


    @staticmethod
    def is_digit(value):
        if not value.isdigit():
            raise ValueError("The provided value does not contain digits only.")


    @staticmethod
    def is_lowercase(value):
        if value.lower() != value:
            raise ValueError(f"The provided value is not lowercase.")


    @staticmethod
    def is_pascalcased(value):
        if re.match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', value) is None:
            raise ValueError("The provided value is not PascalCased")


    @staticmethod
    def is_url(value):
        url_regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )

        if re.match(url_regex, f"http://{value}") is None:
            raise ValueError("The provided value is not a valid domain.")


    @staticmethod
    def min_length(length):
        def minimum_length_validator(value):
            if len(value) < length:
                raise ValueError(f"The provided value should be longer than {length} characters.")

        return minimum_length_validator


    @staticmethod
    def max_length(length):
        def maximum_length_validator(value):
            if len(value) > length:
                raise ValueError(f"The provided value should not be longer than {length} characters.")

        return maximum_length_validator
