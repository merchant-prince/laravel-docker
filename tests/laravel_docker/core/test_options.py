import os
from unittest import TestCase
from laravel_docker.core.options import Options
from scripting_utilities.cd import ChangeDirectory
from tests.utils import suppressed_stdout, send_input


class TestOptions(TestCase):


    def test_environment_uid_and_gid_are_correctly_set(self):
        options = Options()

        self.assertEqual(options.options["environment"]["uid"], os.geteuid())
        self.assertEqual(options.options["environment"]["gid"], os.getegid())


    def test_a_non_pascal_cased_project_name_is_rejected(self):
        options = Options()
        project_name = "project-one"
        max_tries = 3

        with suppressed_stdout(), send_input(f"{project_name}\n" * max_tries):
            self.assertRaises(ValueError, options._ask_for_project_name)


    def test_project_name_is_rejected_if_cwd_has_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectWithAnAwesomeName"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                options = Options()
                max_tries = 3

                with suppressed_stdout(), send_input(f"{project_name}\n" * max_tries):
                    self.assertRaises(ValueError, options._ask_for_project_name)
            finally:
                os.rmdir(project_name)


    def test_a_pascal_cased_non_existent_project_name_is_accepted(self):
        options = Options()
        project_name = "CorrectProjectName"

        with suppressed_stdout(), send_input(project_name):
            captured_project_name = options._ask_for_project_name()

        self.assertEqual(captured_project_name, project_name)


    def test_an_invalid_domain_is_not_accepted(self):
        options = Options()
        invalid_domain = "invalid domain.com"
        max_tries = 3

        with suppressed_stdout(), send_input(f"{invalid_domain}\n" * max_tries):
            self.assertRaises(ValueError, options._ask_for_domain_name)


    def test_a_valid_domain_name_is_accepted(self):
        options = Options()
        domain = "application.local"

        with suppressed_stdout(), send_input(domain):
            captured_domain = options._ask_for_domain_name()

        self.assertEqual(captured_domain, domain)


    def test_a_null_value_defaults_to_the_provided_domain(self):
        options = Options()
        domain = "admin.application.local"
        options.options["project"]["domain"] = domain

        with suppressed_stdout(), send_input("\n"):
            captured_domain = options._ask_for_domain_name()

        self.assertEqual(captured_domain, domain)


    def test_a_database_name_shorter_than_the_specified_length_is_not_accepted(self):
        pass

    def test_a_database_name_consisting_of_any_character_other_than_lowercase_alphabet_is_not_accepted(self):
        pass

    def test_when_a_null_value_is_provided_to_the_database_name_it_defaults_to_the_provided_database_name(self):
        pass

    def test_a_database_name_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
        pass

    # def test_a_database_name_shorter_than_the_specified_length_is_not_accepted(self):
    #     pass

    # def test_a_database_name_consisting_of_any_character_other_than_lowercase_alphabet_is_not_accepted(self):
    #     pass

    # def test_when_a_null_value_is_provided_to_the_database_name_it_defaults_to_the_provided_database_name(self):
    #     pass

    # def test_a_database_name_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
    #     pass

    # def test_a_database_name_shorter_than_the_specified_length_is_not_accepted(self):
    #     pass

    # def test_a_database_name_consisting_of_any_character_other_than_lowercase_alphabet_is_not_accepted(self):
    #     pass

    # def test_when_a_null_value_is_provided_to_the_database_name_it_defaults_to_the_provided_database_name(self):
    #     pass

    # def test_a_database_name_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
    #     pass
