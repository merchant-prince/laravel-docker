import os
import tests.utils as utils
from unittest import TestCase
from laravel_docker.core.options import Options
from scripting_utilities.cd import ChangeDirectory


class TestOptions(TestCase):


    def test_environment_uid_and_gid_are_correctly_set(self):
        options = Options()

        self.assertEqual(options.options["environment"]["uid"], os.geteuid())
        self.assertEqual(options.options["environment"]["gid"], os.getegid())


    def test_a_non_pascal_cased_project_name_is_rejected(self):
        options = Options()
        project_name = "project-one"
        max_tries = 3

        with utils.suppressed_stdout(), utils.send_input(f"{project_name}\n" * max_tries):
            self.assertRaises(ValueError, options._ask_for_project_name)


    def test_project_name_is_rejected_if_cwd_has_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectWithAnAwesomeName"

        with ChangeDirectory("/tmp"):
            try:
                os.mkdir(project_name)

                options = Options()
                max_tries = 3

                with utils.suppressed_stdout(), utils.send_input(f"{project_name}\n" * max_tries):
                    self.assertRaises(ValueError, options._ask_for_project_name)
            finally:
                os.rmdir(project_name)


    def test_a_pascal_cased_non_existent_project_name_is_accepted(self):
        options = Options()
        project_name = "CorrectProjectName"

        with utils.suppressed_stdout(), utils.send_input(project_name):
            options._ask_for_project_name()

        self.assertEquals(options.options["project"]["name"], project_name)
