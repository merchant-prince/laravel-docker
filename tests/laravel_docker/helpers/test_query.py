from io import StringIO
from unittest import TestCase
from laravel_docker.helpers.query import Question
from tests.utils import suppressed_stdout, send_input, raise_exception


class TestQuestion(TestCase):


    def test_a_question_is_displayed_correctly(self):
        question_string = "What is your name?"
        answer = "Harivansh"

        with suppressed_stdout() as stdout, send_input(answer):
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
            lambda a: None if len(a) > 3 else raise_exception(ValueError(error_messages["min"])),
            lambda a: None if len(a) < 10 else raise_exception(ValueError(error_messages["max"]))
        ]
        answers = {
            "correct": "Harivansh",
            "wrong_min": "Hi",
            "wrong_max": "PointusLaziusMaximus"
        }

        with suppressed_stdout() as stdout, send_input(f"{answers['wrong_min']}\n{answers['wrong_max']}\n{answers['correct']}"):
            Question(question_string, validators)

        output = stdout.getvalue()

        self.assertTrue(error_messages["min"] in output)
        self.assertTrue(error_messages["max"] in output)


    def test_an_exception_is_raised_if_a_question_is_unsuccessfully_answered_n_times(self):
        question_string = "What is your name?"
        validators = [lambda a: a if len(a) < 3 else raise_exception(ValueError("Oops..."))]
        wrong_answer = "Wrong Answer"
        max_tries = 5

        try:
            with suppressed_stdout(), send_input(f"{wrong_answer}\n" * max_tries):
                Question(question_string, validators, None, max_tries)
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False, "The expected ValueError was not raised.")
