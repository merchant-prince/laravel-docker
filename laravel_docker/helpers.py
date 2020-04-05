import os
import re
import readline
from collections.abc import Mapping
from scripting_utilities import Print


class Question:
    """
    This class is used to ask questions to the user.

    Attributes:
        question (string):
            The question to ask.
            e.g.: "What is your name?"

        validators ([callable]):
            The validation functions. This is an array of callable objects which
            raise a ValueError when the validation fails.

        default_answer (str):
            The default answer to the question. This is used if the user enters
            an EOL as the first character to the question.

        max_tries (int):
            The maximum number of times to try a question if its validation
            fails.

        answer (str):
            The answer to the question as entered by the user.
    """


    def __init__(self, question, validators = [lambda a: None], default_answer = None, max_tries = 3):
        self._question = question
        self._max_tries = max_tries
        self._default_answer = default_answer
        self._answer = None

        for validator in validators:
            if not callable(validator):
                raise ValueError("One of the validators provided is not a callable.")

        self.validators = validators

        self._ask()


    def _ask(self):
        """
        Ask the question to the user.
        """

        for try_count in range(0, self._max_tries):
            answer = self._ask_question(f"{self._question}: ", self._default_answer)

            if answer == '' and self._default_answer is not None:
                answer = self._default_answer

            try:
                for validator in self.validators:
                    validator(answer)

                self._answer = answer
            except ValueError as exception:
                Print.eol()
                Print.warning(exception)
                Print.eol(2)

                continue
            else:
                break
        else:
            raise ValueError("You have entered the wrong input too many times.")


    def _ask_question(self, question, default_answer):
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
    Each of the validators implemented SHOULD raise a ValueError when the
    condition of the validator is not met, and they should not return any value.
    """


    @staticmethod
    def directory_existence(name):
        if name in os.listdir() and os.path.isdir(name):
            raise ValueError("Another directory with the same name already exists in the current directory.")


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

        if re.match(url_regex, f"https://{value}") is None:
            raise ValueError("The provided value is not a valid domain.")




class Parser:
    """
    This is the parser responsible for processing the project configuration
    templates provided.

    Attributes:
        TEMPLATES_DIRECTORY_PATH (str):
            The absolute path to the templates directory.

    Properties:
        _raw_template_string (str)
        _parsed_template_string (str)
    """


    TEMPLATES_DIRECTORY_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/templates"


    def __init__(self):
        self._raw_template_string = None
        self._parsed_template_string = None


    @property
    def parsed_template_string(self):
        return self._parsed_template_string


    @staticmethod
    def template_path(path = ""):
        if path.startswith("/"):
            raise ValueError("You can only specify a relative path in this method.")

        return f"{Parser.TEMPLATES_DIRECTORY_PATH}/{path.rstrip('/')}"


    def read_template(self, template_path):
        """
        Set the raw template string from the template specified.
        """

        with open(template_path) as template:
            self._raw_template_string = template.read()

        return self


    def add_template_string(self, template_string):
        """
        Set the raw template string to the provided one.
        """

        self._raw_template_string = template_string

        return self


    def parse(self,variables = {}, delimiters_creator = lambda variable_name: f"[[{variable_name}]]"):
        """
        Parse the stored template with the provided variables through the
        delimiters_creator.

        Args:
            variables (dict):
                The variables replace in the template. They are passed through
                the delimiters_creator callable to create a token which is
                searched and replaced throughout the template.

            delimiters_creator (callable):
                The function through which the variable keys are passed to
                return a token - which is replaced throughout the template.
        """

        if not isinstance(variables, Mapping):
            raise ValueError("The variables argument should be a Mapping (dict).")

        if not callable(delimiters_creator):
            raise ValueError("The delimiters_creator argument should be a callable.")

        parsed_template = self._raw_template_string

        for name, value in variables.items():
            parsed_template = parsed_template.replace(delimiters_creator(name), str(value))

        if re.match(r'.*\[\[[A-Z][A-Z0-9_]+\]\].*', parsed_template) is not None:
            raise ValueError("There are still unparsed variables in the template.")

        self._parsed_template_string = parsed_template

        return self


    def output(self, file_path):
        if os.path.isfile(file_path):
            raise ValueError("Another file with the same name already exists.")

        with open(file_path, "w") as file:
            file.write(self._parsed_template_string)




class PrettyLog:
    """
    This class contains decorators to output messages to stdout during the
    installation process.
    """


    @staticmethod
    def message(message, position = "before", type = "info", eols_before = 1, eols_after = 2):
        """
        Outputs a message.

        Args:
            message (str):
                The message to print.
            type (str):
                The type of print function to use. It should be one of the
                following:
                    ["success", "info", "warning", "error"]
            position (str):
                Where to print the message; i.e. before or after calling the
                decorated function. The accepted values are:
                    ["before", "after"]
            eols_before (int):
                The number of EOLs to insert before the message.
            eols_after (int):
                The number of EOLs to insert after the message.
        """

        if position not in ["before", "after"]:
            raise ValueError("Invalid position provided.")

        if type not in ["success", "info", "warning", "error"]:
            raise ValueError("Invalid type provided.")


        def print_message():
            print_function = None

            if type == "success":
                print_function = Print.success
            elif type == "info":
                print_function = Print.info
            elif type == "warning":
                print_function = Print.warning
            elif type == "error":
                print_function = Print.error

            Print.eol(eols_before)
            print_function(message)
            Print.eol(eols_after)


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
