import os
from unittest import TestCase
import tests.helpers as helpers
from scripting_utilities import ChangeDirectory
from laravel_docker.core import ProjectConfiguration, ProjectEnvironment


class TestProjectEnvironment(TestCase):


    def test_environment_uid_and_gid_are_correctly_set(self):
        configuration = ProjectEnvironment()

        self.assertEqual(configuration.get()["environment"]["uid"], os.geteuid())
        self.assertEqual(configuration.get()["environment"]["gid"], os.getegid())


    def test_a_non_pascal_cased_project_name_is_rejected(self):
        configuration = ProjectEnvironment()
        project_name = "project-one"
        max_tries = 3

        with helpers.suppressed_stdout(), helpers.send_input(f"{project_name}\n" * max_tries):
            self.assertRaises(ValueError, configuration._query_project_name)


    def test_project_name_is_rejected_if_cwd_has_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectWithAnAwesomeName"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                configuration = ProjectEnvironment()
                max_tries = 3

                with helpers.suppressed_stdout(), helpers.send_input(f"{project_name}\n" * max_tries):
                    self.assertRaises(ValueError, configuration._query_project_name)
            finally:
                os.rmdir(project_name)


    def test_a_pascal_cased_non_existent_project_name_is_accepted(self):
        configuration = ProjectEnvironment()
        project_name = "CorrectProjectName"

        with helpers.suppressed_stdout(), helpers.send_input(project_name):
            captured_project_name = configuration._query_project_name()

        self.assertEqual(captured_project_name, project_name)


    def test_an_invalid_domain_is_not_accepted(self):
        configuration = ProjectEnvironment()
        invalid_domain = "invalid domain.com"
        max_tries = 3

        with helpers.suppressed_stdout(), helpers.send_input(f"{invalid_domain}\n" * max_tries):
            self.assertRaises(ValueError, configuration._query_domain_name)


    def test_a_valid_domain_name_is_accepted(self):
        configuration = ProjectEnvironment()
        domain = "application.local"

        with helpers.suppressed_stdout(), helpers.send_input(domain):
            captured_domain = configuration._query_domain_name()

        self.assertEqual(captured_domain, domain)


    def test_a_null_value_defaults_to_the_provided_domain(self):
        configuration = ProjectEnvironment()
        domain = "admin.application.local"
        configuration._configuration["project"]["domain"] = domain

        with helpers.suppressed_stdout(), helpers.send_input("\n"):
            captured_domain = configuration._query_domain_name()

        self.assertEqual(captured_domain, domain)
