import os
import random
import re
import readline
import string
from collections.abc import Mapping

from harivansh_scripting_utilities.print import success, info, warning, error


class Question:
    """
    This class is used to ask questions to the user.

    Attributes:
        _question (str):
            The question to ask.
            e.g.: "What is your name?"

        _validators ((callable,)):
            An array of validation functions which raise ValueErrors on failure.

        _default_answer (str):
            The default answer to the question.
            This is used if the user enters an EOL as the first character as an answer to the question.

        _max_tries (int):
            The maximum number of times to try a question.

        _answer (str):
            The user's answer to the question.
    """

    def __init__(self, question, validators=(lambda a: None,), default_answer=None, max_tries=3):
        self._question = question
        self._max_tries = max_tries
        self._default_answer = default_answer
        self._answer = None

        for validator in validators:
            if not callable(validator):
                raise ValueError("One of the validators provided is not a callable.")

        self._validators = validators

        self._ask()

    def _ask(self):
        """
        Ask the question to the user.
        """

        for try_count in range(0, self._max_tries):
            answer = self.format(f"{self._question}: ", self._default_answer)

            if answer == '' and self._default_answer is not None:
                answer = self._default_answer

            try:
                for validate in self._validators:
                    validate(answer)

                self._answer = answer
            except ValueError as exception:
                print(f"\n{warning(exception)}\n\n", end="")
                continue
            else:
                break
        else:
            raise ValueError("You have entered the wrong input too many times.")

    @staticmethod
    def format(question, default_answer):
        """
        Ask a question with a default answer.

        Args:
            question (str)
            default_answer (str)
        """

        readline.set_startup_hook(lambda: readline.insert_text(default_answer))

        try:
            return input(question)
        finally:
            readline.set_startup_hook()

    def __str__(self):
        return self._answer


class Validation:
    """
    This class is used to validate answers collected from the users.
    Each of the validators implemented SHOULD raise a ValueError when the condition of the validator is not met,
    and they should not return any value.
    """

    @staticmethod
    def directory_exists(name):
        if os.path.isdir(name):
            raise ValueError("Another directory with the same name already exists in the current directory.")

    @staticmethod
    def is_pascalcase(value):
        if re.match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', value) is None:
            raise ValueError("The provided value is not a PascalCased alphabetic string.")

    @staticmethod
    def is_url(value):
        url_regex = re.compile(
            r"^"
            r"(?:http|ftp)s?://"  # scheme
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))"  # domain
            r"(?::\d+)?"  # port (optional)
            r"(?:/?|[/?]\S+)"  # path
            r"$",
            re.IGNORECASE
        )

        if re.match(url_regex, f"https://{value}") is None:
            raise ValueError("The provided value is not a valid domain.")


class Parser:
    """
    This is the parser responsible for processing the project configuration templates provided.

    Attributes:
        Parser.TEMPLATES_DIRECTORY_PATH (str):
            The absolute path to the templates directory.

    Properties:
        _raw_template_string (str)
        parsed_template_string (str)
    """

    TEMPLATES_DIRECTORY_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/templates"

    def __init__(self):
        self._raw_template_string = None
        self.parsed_template_string = None

    @staticmethod
    def template_path(path):
        filepath = f"{Parser.TEMPLATES_DIRECTORY_PATH}/{path.rstrip('/')}"

        if not os.path.isfile(filepath):
            raise ValueError("There is no file at the provided path within the templates directory.")

        return filepath

    def read_template(self, template_path):
        """
        Set the raw template string from the template file specified.

        Args:
            template_path (str):
                The path to the template file.
        """

        with open(template_path) as template:
            self._raw_template_string = template.read()

        return self

    def add_template_string(self, template_string):
        """
        Set the raw template string to the provided one.

        Args:
            template_string (str):
                The template string to store for later processing.
        """

        self._raw_template_string = template_string

        return self

    def parse(self, variables={}, delimiters_creator=lambda variable_name: f"[[{variable_name}]]"):
        """
        Parse the stored template with the provided variables through the delimiters_creator.

        Args:
            variables (dict):
                The variables to replace in the template. They are passed through the delimiters_creator callable to
                create a token which is then searched and replaced throughout the template.

            delimiters_creator (callable):
                The function through which the variable keys are passed to return a token (see above for description).
        """

        if not isinstance(variables, Mapping):
            raise ValueError("The variables argument should be a Mapping (dict).")

        if not callable(delimiters_creator):
            raise ValueError("The delimiters_creator argument should be a callable.")

        parsed_template = self._raw_template_string

        for name, value in variables.items():
            parsed_template = parsed_template.replace(delimiters_creator(name), str(value))

        unique_token = "".join(random.choices(f"{string.ascii_uppercase}_", k=64))
        # The following regex is created according to the delimiters_creator passed to this method.
        token_regex = re.compile(
            r".*" + re.escape(delimiters_creator(unique_token)).replace(unique_token, r"\w[\w_]*") + r".*"
        )

        if token_regex.match(parsed_template) is not None:
            raise ValueError("There are still unparsed variables in the template.")

        self.parsed_template_string = parsed_template

        return self

    def output(self, filepath):
        """
        Write the contents of the parsed template string to the specified file.

        Args:
            filepath (str):
                The path to the file to which the parsed template should be written.
        """

        if os.path.isfile(filepath):
            raise ValueError("Another file with the same name already exists.")

        with open(filepath, "w") as file:
            file.write(self.parsed_template_string)


def log(message, type="info", position="before"):
    """
    Outputs a log message before or after running the decorated function

    Args:
        message (str):
            The message to print.

        type (str):
            The type of print function to use. It should be one of the following:
                ["success", "info", "warning", "error"]

        position (str):
            Where to print the message; i.e. before or after calling the decorated function.
            The accepted values are: ["before", "after"]
    """

    if type not in ["success", "info", "warning", "error", "plain"]:
        raise ValueError("Invalid type provided.")

    if position not in ["before", "after"]:
        raise ValueError("Invalid position provided.")

    def print_message():
        """
        Pretty print the message according to the type provided.
        """

        if type == "success":
            prettified_message = success(message)
        elif type == "info":
            prettified_message = info(message)
        elif type == "warning":
            prettified_message = warning(message)
        elif type == "error":
            prettified_message = error(message)
        else:
            prettified_message = message

        print(f"\n{prettified_message}\n\n", end="")

    def decorator(function):
        def wrapper(*args, **kwargs):
            if position == "before":
                print_message()

            result = function(*args, **kwargs)

            if position == "after":
                print_message()

            return result

        return wrapper

    return decorator
