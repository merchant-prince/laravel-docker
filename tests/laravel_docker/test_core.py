import os
import shutil
from pathlib import Path
from unittest import TestCase
import tests.helpers as helpers
from laravel_docker.core import ProjectConfiguration, Parser
from scripting_utilities.cd import ChangeDirectory


class TestProjectConfiguration(TestCase):


    def test_environment_uid_and_gid_are_correctly_set(self):
        project_configuration = ProjectConfiguration()

        self.assertEqual(project_configuration.get()["environment"]["uid"], os.geteuid())
        self.assertEqual(project_configuration.get()["environment"]["gid"], os.getegid())


    def test_a_non_pascal_cased_project_name_is_rejected(self):
        project_configuration = ProjectConfiguration()
        project_name = "project-one"
        max_tries = 3

        with helpers.suppressed_stdout(), helpers.send_input(f"{project_name}\n" * max_tries):
            self.assertRaises(ValueError, project_configuration._ask_for_project_name)


    def test_project_name_is_rejected_if_cwd_has_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectWithAnAwesomeName"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                project_configuration = ProjectConfiguration()
                max_tries = 3

                with helpers.suppressed_stdout(), helpers.send_input(f"{project_name}\n" * max_tries):
                    self.assertRaises(ValueError, project_configuration._ask_for_project_name)
            finally:
                os.rmdir(project_name)


    def test_a_pascal_cased_non_existent_project_name_is_accepted(self):
        project_configuration = ProjectConfiguration()
        project_name = "CorrectProjectName"

        with helpers.suppressed_stdout(), helpers.send_input(project_name):
            captured_project_name = project_configuration._ask_for_project_name()

        self.assertEqual(captured_project_name, project_name)


    def test_an_invalid_domain_is_not_accepted(self):
        project_configuration = ProjectConfiguration()
        invalid_domain = "invalid domain.com"
        max_tries = 3

        with helpers.suppressed_stdout(), helpers.send_input(f"{invalid_domain}\n" * max_tries):
            self.assertRaises(ValueError, project_configuration._ask_for_domain_name)


    def test_a_valid_domain_name_is_accepted(self):
        project_configuration = ProjectConfiguration()
        domain = "application.local"

        with helpers.suppressed_stdout(), helpers.send_input(domain):
            captured_domain = project_configuration._ask_for_domain_name()

        self.assertEqual(captured_domain, domain)


    def test_a_null_value_defaults_to_the_provided_domain(self):
        project_configuration = ProjectConfiguration()
        domain = "admin.application.local"
        project_configuration._configuration["project"]["domain"] = domain

        with helpers.suppressed_stdout(), helpers.send_input("\n"):
            captured_domain = project_configuration._ask_for_domain_name()

        self.assertEqual(captured_domain, domain)


    def test_a_database_name_shorter_than_5_characters_is_not_accepted(self):
        project_configuration = ProjectConfiguration()
        database_name = {
            "wrong": "name",
            "correct": "database"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_name['wrong']}\n{database_name['correct']}"):
            project_configuration._ask_for_database_name()

        self.assertNotEqual(project_configuration.get()["database"]["name"], database_name["wrong"])


    def test_a_database_name_consisting_of_any_character_other_than_lowercase_alphabet_is_not_accepted(self):
        project_configuration = ProjectConfiguration()
        database_name = {
            "wrong": "WrongDbName223",
            "correct": "database"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_name['wrong']}\n{database_name['correct']}"):
            project_configuration._ask_for_database_name()

        self.assertNotEqual(project_configuration.get()["database"]["name"], database_name["wrong"])



    def test_when_a_null_value_is_provided_to_the_database_name_it_defaults_to_the_provided_database_name(self):
        project_configuration = ProjectConfiguration()
        default_answer = "databasename"
        project_configuration._configuration["database"]["name"] = default_answer
        answer = "\n"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            project_configuration._ask_for_database_name()

        self.assertEqual(project_configuration.get()["database"]["name"], default_answer)


    def test_a_database_name_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
        project_configuration = ProjectConfiguration()
        answer = "databasename"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            project_configuration._ask_for_database_name()


    def test_a_database_username_shorter_than_5_characters_is_not_accepted(self):
        project_configuration = ProjectConfiguration()
        database_username = {
            "wrong": "name",
            "correct": "username"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_username['wrong']}\n{database_username['correct']}"):
            project_configuration._ask_for_database_username()

        self.assertNotEqual(project_configuration.get()["database"]["username"], database_username["wrong"])


    def test_when_a_null_value_is_provided_to_the_database_username_it_defaults_to_the_provided_database_username(self):
        project_configuration = ProjectConfiguration()
        default_answer = "username"
        project_configuration._configuration["database"]["username"] = default_answer
        answer = "\n"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            project_configuration._ask_for_database_username()

        self.assertEqual(project_configuration.get()["database"]["username"], default_answer)


    def test_a_database_username_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
        project_configuration = ProjectConfiguration()
        answer = "username"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            project_configuration._ask_for_database_username()


    def test_a_database_password_shorter_than_5_characters_is_not_accepted(self):
        project_configuration = ProjectConfiguration()
        database_password = {
            "wrong": "lepass",
            "correct": "password"
        }

        with helpers.suppressed_stdout(), helpers.send_input(f"{database_password['wrong']}\n{database_password['correct']}"):
            project_configuration._ask_for_database_password()

        self.assertNotEqual(project_configuration.get()["database"]["name"], database_password["wrong"])


    def test_when_a_null_value_is_provided_to_the_database_password_it_defaults_to_the_provided_database_password(self):
        project_configuration = ProjectConfiguration()
        default_answer = "password"
        project_configuration._configuration["database"]["password"] = default_answer
        answer = "\n"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            project_configuration._ask_for_database_password()

        self.assertEqual(project_configuration.get()["database"]["password"], default_answer)


    def test_a_database_password_of_the_specified_length_consisting_of_lowercase_alphabets_only_is_accepted(self):
        project_configuration = ProjectConfiguration()
        answer = "password"

        with helpers.suppressed_stdout(), helpers.send_input(answer):
            project_configuration._ask_for_database_password()




class TestParser(TestCase):


    def test_a_template_is_read(self):
        project_name = "TheAwesomeProjectWithAnAwesomeName"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                with ChangeDirectory(project_name):
                    template_name = "template.txt"
                    template_string = "This is the template string."

                    with open(template_name, "w") as template:
                        template.write(template_string)

                    parser = Parser()
                    parser.read_template(template_name)

                    self.assertEqual(parser._raw_template_string, template_string)
            finally:
                shutil.rmtree(project_name)


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
        template_string = "This is the template string with [[LE_VAR]] and [[MORE_VARS]]."
        variables = {
            "LE_VAR": "this variable"
        }
        parser = Parser()

        parser.add_template_string(template_string)

        self.assertRaises(ValueError, parser.parse, variables)


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
        project_name = "TheAwesomeProjectWithAnAwesomeName"
        output_filename = "output.txt"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                with ChangeDirectory(project_name):
                    Path(output_filename).touch()

                    parser = Parser()

                    parser.add_template_string(template_string).parse(variables)

                    self.assertRaises(ValueError, parser.output, output_filename)
            finally:
                shutil.rmtree(project_name)


    def test_the_output_file_is_written_to_the_specified_path(self):
        template_string = "The user's name is [[NAME]] and his email is [[EMAIL]]."
        variables = {
            "NAME": "Harivansh",
            "EMAIL": "hello@harivan.sh"
        }
        expected_parsed_template_string = "The user's name is Harivansh and his email is hello@harivan.sh."
        project_name = "TheAwesomeProjectWithAnAwesomeName"
        output_filename = "output.txt"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                with ChangeDirectory(project_name):
                    (Parser()
                        .add_template_string(template_string)
                        .parse(variables)
                        .output(output_filename))

                    with open(output_filename) as output:
                        output_file_contents = output.read()

                    self.assertEqual(output_file_contents, expected_parsed_template_string)
            finally:
                shutil.rmtree(project_name)
