from io import StringIO
from unittest import TestCase
import tests.helpers as helpers
from contextlib import redirect_stdout
from laravel_docker.helpers.query import Question


class TestQuestion(TestCase):


    def test_a_question_is_displayed_correctly(self):
        question_string = "What is your name?"
        answer = "Harivansh"
        question = Question(question_string)

        with helpers.suppress_stdout() as stdout, helpers.send_input(answer):
            question.ask()

        self.assertTrue(question_string in stdout.getvalue())


    def test_an_exception_is_raised_if_a_callable_is_not_provided_to_the_question(self):
        question_string = "What is your name?"
        validator = "wrong validator type"

        self.assertRaises(ValueError, Question, question_string, validator)


    def test_the_correct_error_message_is_displayed_on_validation_error(self):
        question_string = "What is your name?"
        validation_error_message = "Oops..."
        validator = lambda a: a if len(a) < 10 else ValueError(validation_error_message)
        wrong_answer = "Wrong Answer"
        answer = "Answer"
        question = Question(question_string, validator)

        with helpers.suppress_stdout() as stdout, helpers.send_input(f"{wrong_answer}\n{answer}"):
            question.ask()

        self.assertTrue(validation_error_message in stdout.getvalue())


    def test_an_exception_is_raised_if_a_question_is_unsuccessfully_answered_n_times(self):
        question_string = "What is your name?"
        validator = lambda a: a if len(a) < 3 else ValueError("Oops...")
        wrong_answer = "Wrong Answer"
        max_tries = 5
        question = Question(question_string, validator, max_tries)

        try:
            with helpers.suppress_stdout(), helpers.send_input(f"{wrong_answer}\n" * max_tries):
                question.ask()
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False, "The expected ValueError was not raised.")
