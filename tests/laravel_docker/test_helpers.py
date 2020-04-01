import os
from io import StringIO
from unittest import TestCase
import tests.helpers as helpers
from scripting_utilities.cd import ChangeDirectory
from laravel_docker.helpers import Question, Validation


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
        except ValueError:
            self.assertTrue(True)
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


    def test_an_alphabetic_value_is_accepted(self):
        value = "thisisAlphabetic"
        Validation.is_alphabetic(value)


    def test_a_non_alphabetic_value_is_not_accepted(self):
        value = "non44alpha00Betic55"
        self.assertRaises(ValueError, Validation.is_alphabetic, value)


    def test_an_alphanumeric_value_is_accepted(self):
        value = "thisisalphaNumeric001"
        Validation.is_alphanumeric(value)


    def test_a_non_alphanumeric_value_is_not_accepted(self):
        value = "this is not alphanumeric 4554"
        self.assertRaises(ValueError, Validation.is_alphanumeric, value)


    def test_a_string_consisting_of_digits_only_is_accepted(self):
        value = "1234566"
        Validation.is_digit(value)


    def test_a_string_not_consisting_of_digits_only_is_not_accepted(self):
        value = "3550a"
        self.assertRaises(ValueError, Validation.is_digit, value)


    def test_a_string_consisting_of_lowercase_characters_only_is_accepted(self):
        value = "thisislowercase"
        Validation.is_lowercase(value)


    def test_a_string_consisting_of_mixed_case_characters_is_not_accepted(self):
        value = "ThisIsMixedCase"
        self.assertRaises(ValueError, Validation.is_lowercase, value)


    def test_a_string_longer_than_the_minimum_length_specified_is_accepted(self):
        length = 10
        value = "z" * (length + 1)
        validator = Validation.min_length(length)
        validator(value)


    def test_a_string_shorter_than_the_minimum_length_specified_is_not_accepted(self):
        length = 10
        value = "a" * (length - 1)
        self.assertRaises(ValueError, Validation.min_length(length), value)


    def test_a_string_shorter_than_the_maximum_length_specified_is_accepted(self):
        length = 10
        value = "z" * (length - 1)
        validator = Validation.max_length(length)
        validator(value)


    def test_a_string_longer_than_the_maximum_length_specified_is_not_accepted(self):
        length = 10
        value = "a" * (length + 1)
        self.assertRaises(ValueError, Validation.max_length(length), value)


    def test_a_value_is_not_accepted_if_the_cwd_contains_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectTest"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)
                self.assertRaises(ValueError, Validation.directory_existence, project_name)
            finally:
                os.rmdir(project_name)


    def test_a_value_is_accepted_if_the_cwd_does_not_contain_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectThatDoesNotExistTest"

        with ChangeDirectory("/tmp"):
            Validation.directory_existence(project_name)


    def test_a_correctly_formatted_url_is_accepted(self):
        url = "application.local"

        Validation.is_url(url)


    def test_an_incorrect_url_is_not_accepted(self):
        bad_url = "bad url.test"

        self.assertRaises(ValueError, Validation.is_url, bad_url)
