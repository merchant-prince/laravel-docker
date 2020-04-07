import os
import shutil
from io import StringIO
from pathlib import Path
from tests import helpers
from unittest import TestCase
from scripting_utilities import ChangeDirectory
from laravel_docker.helpers import Parser, PrettyLog, Question, Validation


class TestQuestion(TestCase):


    def test_a_question_is_displayed_correctly(self):
        question_string = "What is your name?"
        answer = "Harivansh"

        with helpers.suppressed_stdout() as stdout, helpers.send_input(answer):
            Question(question_string)

        self.assertTrue(question_string in stdout.getvalue())


    def test_an_exception_is_raised_if_any_of_the_validators_provided_is_not_a_callable(self):
        question_string = "What is your name?"
        validator = [
            lambda a: a,
            "wrong validator type"
        ]

        self.assertRaises(ValueError, Question, question_string, validator)


    def test_the_correct_error_message_is_displayed_on_validation_error(self):
        question_string = "What is your name?"
        error_messages = {
            "min": "This is the MINIMUM error message.",
            "max": "This is the MAXIMUM error message."
        }
        validators = [
            lambda a: None if len(a) > 3 else helpers.raise_exception(ValueError(error_messages["min"])),
            lambda a: None if len(a) < 10 else helpers.raise_exception(ValueError(error_messages["max"]))
        ]
        answers = {
            "correct": "Harivansh",
            "wrong_min": "Hi",
            "wrong_max": "PointusLaziusMaximus"
        }

        with helpers.suppressed_stdout() as stdout, helpers.send_input(f"{answers['wrong_min']}\n{answers['wrong_max']}\n{answers['correct']}"):
            Question(question_string, validators)

        output = stdout.getvalue()

        self.assertTrue(error_messages["min"] in output)
        self.assertTrue(error_messages["max"] in output)


    def test_an_exception_is_raised_if_a_question_is_unsuccessfully_answered_n_times(self):
        question_string = "What is your name?"
        validators = [lambda a: a if len(a) < 3 else helpers.raise_exception(ValueError("Oops..."))]
        wrong_answer = "Wrong Answer"
        max_tries = 5

        try:
            with helpers.suppressed_stdout(), helpers.send_input(f"{wrong_answer}\n" * max_tries):
                Question(question_string, validators, None, max_tries)
        except:
            pass
        else:
            self.assertTrue(False, "The expected ValueError was not raised.")


    def test_the_answer_defaults_to_the_default_answer_if_no_input_is_provided_by_the_user(self):
        question_string = "What is your name?"
        validators = [lambda a: a if len(a) < 20 else helpers.raise_exception(ValueError("error message..."))]
        answer = "\n"
        default_answer = "Hari Vansh"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            recorded_answer = str(Question(question_string, validators, default_answer))

        self.assertEqual(recorded_answer, default_answer)




class TestValidators(TestCase):


    def test_a_value_is_not_accepted_if_it_is_not_pascalcased(self):
        project_name = "le-projectname"

        self.assertRaises(ValueError, Validation.is_pascalcased, project_name)


    def test_a_value_is_accepted_if_it_is_pascalcased(self):
        project_name = "LeProjectname"

        Validation.is_pascalcased(project_name)


    def test_a_value_is_not_accepted_if_the_cwd_contains_a_directory_with_the_same_name(self):
        with helpers.temporary_directory():
            project_name = "TheAwesomeProjectTest"

            os.mkdir(project_name)

            self.assertRaises(ValueError, Validation.directory_existence, project_name)


    def test_a_value_is_accepted_if_the_cwd_does_not_contain_a_directory_with_the_same_name(self):
        with helpers.temporary_directory():
            Validation.directory_existence("TheAwesomeProjectThatDoesNotExistTest")


    def test_a_correctly_formatted_url_is_accepted(self):
        url = "application.local"

        Validation.is_url(url)


    def test_an_incorrect_url_is_not_accepted(self):
        bad_url = "bad url.test"

        self.assertRaises(ValueError, Validation.is_url, bad_url)




class TestParser(TestCase):


    def test_the_correct_template_path_is_returned(self):
        path = "One"
        templates_directory_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        expected_path = f"{templates_directory_path}/laravel_docker/templates/One"

        self.assertEqual(Parser.template_path(path), expected_path)


    def test_a_template_is_read(self):
        with helpers.temporary_directory():
            template_name = "template.txt"
            template_string = "This is the template string."

            with open(template_name, "w") as template:
                template.write(template_string)

            parser = Parser()
            parser.read_template(template_name)

            self.assertEqual(parser._raw_template_string, template_string)


    def test_a_template_string_is_added(self):
        template_string = "This is the template string."
        parser = Parser()
        parser.add_template_string(template_string)

        self.assertEqual(parser._raw_template_string, template_string)


    def test_the_parser_variable_not_of_the_mapping_type_will_raise_an_error(self):
        template_string = "This is the template string."
        variables = "WRONG VARIABLE TYPE"
        parser = Parser()

        parser.add_template_string(template_string)

        self.assertRaises(ValueError, parser.parse, variables)


    def test_the_parser_delimiters_creator_not_of_the_callable_type_will_raise_an_error(self):
        template_string = "This is the template string."
        variables = {}
        delimiters_creator = "WRONG DELIMITERS CREATOR TYPE"
        parser = Parser()

        parser.add_template_string(template_string)

        self.assertRaises(ValueError, parser.parse, variables, delimiters_creator)


    def test_parser_will_throw_an_error_if_there_are_remaining_variables_in_the_parsed_template(self):
        templates_and_delimiters_creator = {
            "This is the template string with [[LE_VAR]] and [[MORE_VARS]].": lambda d: f"[[{d}]]",
            "This is the template string with {{LE_VAR}} and {{MORE_VARS}}.": lambda d: f"{{{{{d}}}}}",
            "This is the template string with ||LE_VAR|| and ||MORE_VARS||.": lambda d: f"||{d}||"
        }
        parser = Parser()

        for template, delimiters_creator in templates_and_delimiters_creator.items():
            parser.add_template_string(template)

            self.assertRaises(ValueError, parser.parse, {}, delimiters_creator)


    def test_a_template_is_successfully_parsed_with_the_default_delimiters_creator_if_the_correct_variables_mapping_is_provided(self):
        template_string = "The user's name is [[NAME]] and his email is [[EMAIL]]."
        variables = {
            "NAME": "Harivansh",
            "EMAIL": "hello@harivan.sh"
        }
        expected_parsed_template_string = "The user's name is Harivansh and his email is hello@harivan.sh."
        parser = Parser()

        parser.add_template_string(template_string).parse(variables)

        self.assertEqual(parser.parsed_template_string, expected_parsed_template_string)


    def test_a_template_is_successfully_parsed_with_a_custom_delimiters_creator_if_the_correct_variables_mapping_is_provided(self):
        template_string = "The user's name is {{LE_NAME}} and his email is {{LE_EMAIL}}."
        variables = {
            "NAME": "Harivansh",
            "EMAIL": "hello@harivan.sh"
        }
        delimiters_creator = lambda n: f"{{{{LE_{n}}}}}"
        expected_parsed_template_string = "The user's name is Harivansh and his email is hello@harivan.sh."
        parser = Parser()

        parser.add_template_string(template_string).parse(variables, delimiters_creator)

        self.assertEqual(parser.parsed_template_string, expected_parsed_template_string)


    def test_the_output_file_cannot_be_written_to_the_specified_path_if_it_already_exists(self):
        template_string = "The user's name is [[NAME]] and his email is [[EMAIL]]."
        variables = {
            "NAME": "Harivansh",
            "EMAIL": "hello@harivan.sh"
        }
        output_filename = "output.txt"

        with helpers.temporary_directory():
            Path(output_filename).touch()

            parser = Parser()

            parser.add_template_string(template_string).parse(variables)

            self.assertRaises(ValueError, parser.output, output_filename)


    def test_the_output_file_is_written_to_the_specified_path(self):
        template_string = "The user's name is [[NAME]] and his email is [[EMAIL]]."
        variables = {
            "NAME": "Harivansh",
            "EMAIL": "hello@harivan.sh"
        }
        expected_parsed_template_string = "The user's name is Harivansh and his email is hello@harivan.sh."
        output_filename = "output.txt"

        with helpers.temporary_directory():
            (Parser()
                .add_template_string(template_string)
                .parse(variables)
                .output(output_filename))

            with open(output_filename) as output:
                output_file_contents = output.read()

            self.assertEqual(output_file_contents, expected_parsed_template_string)




class TestDecorators(TestCase):


    def test_start_decorator_outputs_message_before_calling_the_wrapped_function(self):
        delimiter = "="
        function_message = "function message"
        decorator_message = "Hello, world!"

        @PrettyLog.message(f"{decorator_message}{delimiter}")
        def test_function():
            print(f"{delimiter}{function_message}")

        with helpers.suppressed_stdout() as stdout:
            test_function()

        messages = [token.strip() for token in stdout.getvalue().split(delimiter)]

        self.assertTrue(decorator_message in messages[0])
        self.assertTrue(function_message in messages[-1])


    def test_end_decorator_outputs_message_after_calling_the_wrapped_function(self):
        delimiter = "="
        function_message = "function message"
        decorator_message = "Hello, world!"

        @PrettyLog.message(f"{delimiter}{decorator_message}", position = "after")
        def test_function():
            print(f"{function_message}{delimiter}")

        with helpers.suppressed_stdout() as stdout:
            test_function()

        messages = [token.strip() for token in stdout.getvalue().split(delimiter)]

        self.assertTrue(function_message in messages[0])
        self.assertTrue(decorator_message in messages[-1])


    def test_exception_is_raised_when_the_wrong_position_is_provided(self):
        function = lambda x: x

        self.assertRaises(ValueError, PrettyLog.message, function, position = "wrong_position")


    def test_exception_is_raised_when_the_wrong_type_is_provided(self):
        function = lambda x: x

        self.assertRaises(ValueError, PrettyLog.message, function, type = "wrong_type")
