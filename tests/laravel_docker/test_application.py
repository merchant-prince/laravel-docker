import copy
from unittest import TestCase

from harivansh_scripting_utilities.helpers import capturestdout, injectstdin, tmpdir

from laravel_docker.application import Application
from laravel_docker.core import ProjectConfiguration, ProjectEnvironment


class TestProjectConfiguration(TestCase):

    def test_the_project_environment_configuration_is_not_altered_after_the_configuration_files_are_set(self):
        project_name = "One"
        domain_name = "application.one.com"

        with capturestdout(), injectstdin(f"{project_name}\n{domain_name}\n"):
            configuration = ProjectEnvironment().initialize().get()

        with tmpdir():
            with capturestdout():
                application = Application()
                application._configuration = copy.deepcopy(configuration)
                application._structure()

            project_configuration = ProjectConfiguration(copy.deepcopy(configuration))

            self.assertEqual(project_configuration._configuration, configuration)
