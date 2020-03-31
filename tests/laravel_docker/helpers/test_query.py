from io import StringIO
from unittest import TestCase
import tests.helpers as helpers
from contextlib import redirect_stdout
from laravel_docker.helpers.query import Question


class TestQuestion(TestCase):


    def test_a_question_is_displayed_correctly(self):
        question_string = "What is your name?"
        answer = "Harivansh"

        with helpers.suppress_stdout() as stdout, helpers.send_input(answer):
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
        length_validation_message = "Oops..."
        type_validation_message = "Nope..."
        validators = [
            lambda a: a if not a.isdigit() else ValueError(type_validation_message),
            lambda a: a if len(a) < 10 else ValueError(length_validation_message)
        ]
        wrong_answer = {
            "bad_length": "Wrong Answer",
            "wrong_type": 123
        }
        answer = "Answer"

        with helpers.suppress_stdout() as stdout, helpers.send_input(f"{wrong_answer['bad_length']}\n{wrong_answer['wrong_type']}\n{answer}"):
            Question(question_string, validators)

        output = stdout.getvalue()

        self.assertTrue(length_validation_message in output)
        self.assertTrue(type_validation_message in output)


    def test_an_exception_is_raised_if_a_question_is_unsuccessfully_answered_n_times(self):
        question_string = "What is your name?"
        validators = [lambda a: a if len(a) < 3 else ValueError("Oops...")]
        wrong_answer = "Wrong Answer"
        max_tries = 5

        try:
            with helpers.suppress_stdout(), helpers.send_input(f"{wrong_answer}\n" * max_tries):
                Question(question_string, validators, max_tries)
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False, "The expected ValueError was not raised.")
