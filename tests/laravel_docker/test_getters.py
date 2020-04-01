import os
from unittest import TestCase
import tests.helpers as helpers
from laravel_docker.getters import Configuration
from scripting_utilities.cd import ChangeDirectory


class TestConfiguration(TestCase):


    def test_environment_uid_and_gid_are_correctly_set(self):
        configuration = Configuration()

        self.assertEqual(configuration.get()["environment"]["uid"], os.geteuid())
        self.assertEqual(configuration.get()["environment"]["gid"], os.getegid())


    def test_a_non_pascal_cased_project_name_is_rejected(self):
        configuration = Configuration()
        project_name = "project-one"
        max_tries = 3

        with helpers.suppressed_stdout(), helpers.send_input(f"{project_name}\n" * max_tries):
            self.assertRaises(ValueError, configuration._ask_for_project_name)


    def test_project_name_is_rejected_if_cwd_has_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectWithAnAwesomeName"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                configuration = Configuration()
                max_tries = 3

                with helpers.suppressed_stdout(), helpers.send_input(f"{project_name}\n" * max_tries):
                    self.assertRaises(ValueError, configuration._ask_for_project_name)
            finally:
                os.rmdir(project_name)


    def test_a_pascal_cased_non_existent_project_name_is_accepted(self):
        configuration = Configuration()
        project_name = "CorrectProjectName"

        with helpers.suppressed_stdout(), helpers.send_input(project_name):
            captured_project_name = configuration._ask_for_project_name()

        self.assertEqual(captured_project_name, project_name)


    def test_an_invalid_domain_is_not_accepted(self):
        configuration = Configuration()
        invalid_domain = "invalid domain.com"
        max_tries = 3

        with helpers.suppressed_stdout(), helpers.send_input(f"{invalid_domain}\n" * max_tries):
            self.assertRaises(ValueError, configuration._ask_for_domain_name)


    def test_a_valid_domain_name_is_accepted(self):
        configuration = Configuration()
        domain = "application.local"

        with helpers.suppressed_stdout(), helpers.send_input(domain):
            captured_domain = configuration._ask_for_domain_name()

        self.assertEqual(captured_domain, domain)


    def test_a_null_value_defaults_to_the_provided_domain(self):
        configuration = Configuration()
        domain = "admin.application.local"
        configuration._configuration["project"]["domain"] = domain

        with helpers.suppressed_stdout(), helpers.send_input("\n"):
            captured_domain = configuration._ask_for_domain_name()

        self.assertEqual(captured_domain, domain)


    def test_a_database_name_shorter_than_5_characters_is_not_accepted(self):
        configuration = Configuration()
        database_name = {
            "wrong": "name",
            "correct": "database"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_name['wrong']}\n{database_name['correct']}"):
            configuration._ask_for_database_name()

        self.assertNotEqual(configuration.get()["database"]["name"], database_name["wrong"])


    def test_a_database_name_consisting_of_any_character_other_than_lowercase_alphabet_is_not_accepted(self):
        configuration = Configuration()
        database_name = {
            "wrong": "WrongDbName223",
            "correct": "database"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_name['wrong']}\n{database_name['correct']}"):
            configuration._ask_for_database_name()

        self.assertNotEqual(configuration.get()["database"]["name"], database_name["wrong"])



    def test_when_a_null_value_is_provided_to_the_database_name_it_defaults_to_the_provided_database_name(self):
        configuration = Configuration()
        default_answer = "databasename"
        configuration._configuration["database"]["name"] = default_answer
        answer = "\n"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            configuration._ask_for_database_name()

        self.assertEqual(configuration.get()["database"]["name"], default_answer)


    def test_a_database_name_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
        configuration = Configuration()
        answer = "databasename"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            configuration._ask_for_database_name()


    def test_a_database_username_shorter_than_5_characters_is_not_accepted(self):
        configuration = Configuration()
        database_username = {
            "wrong": "name",
            "correct": "username"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_username['wrong']}\n{database_username['correct']}"):
            configuration._ask_for_database_username()

        self.assertNotEqual(configuration.get()["database"]["username"], database_username["wrong"])


    def test_when_a_null_value_is_provided_to_the_database_username_it_defaults_to_the_provided_database_username(self):
        configuration = Configuration()
        default_answer = "username"
        configuration._configuration["database"]["username"] = default_answer
        answer = "\n"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            configuration._ask_for_database_username()

        self.assertEqual(configuration.get()["database"]["username"], default_answer)


    def test_a_database_username_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
        configuration = Configuration()
        answer = "username"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            configuration._ask_for_database_username()


    def test_a_database_password_shorter_than_5_characters_is_not_accepted(self):
        configuration = Configuration()
        database_password = {
            "wrong": "lepass",
            "correct": "password"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_password['wrong']}\n{database_password['correct']}"):
            configuration._ask_for_database_password()

        self.assertNotEqual(configuration.get()["database"]["name"], database_password["wrong"])


    def test_when_a_null_value_is_provided_to_the_database_password_it_defaults_to_the_provided_database_password(self):
        configuration = Configuration()
        default_answer = "password"
        configuration._configuration["database"]["password"] = default_answer
        answer = "\n"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            configuration._ask_for_database_password()

        self.assertEqual(configuration.get()["database"]["password"], default_answer)


    def test_a_database_password_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
        configuration = Configuration()
        answer = "password"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            configuration._ask_for_database_password()
