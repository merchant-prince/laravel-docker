import os
import re
from subprocess import run
from laravel_docker.helpers import Question, Validation
from scripting_utilities.skeleton import CreateSkeleton


class ProjectEnvironment:


    def __init__(self):
        self._configuration = {
            "project": {
                "name": None,
                "domain": "application.local"
            },
            "environment": {
                "uid": os.geteuid(),
                "gid": os.getegid()
            }
        }


    def initialize(self):
        """
        Initialize the configuration dictionary. This is done by asking the
        user a few questions concerning the configuration options of the
        project.

        Returns:
            self
        """

        self._configuration["project"]["name"] = self._ask_for_project_name()
        self._configuration["project"]["domain"] = self._ask_for_domain_name()

        return self


    def get(self):
        """
        Get the current instance of the configuration dictionary.

        Returns:
            dict: The current configuration instance.
        """

        return self._configuration


    def _ask_for_project_name(self):
        return str(Question(
            "Enter the project name",
            [
                Validation.is_pascalcased,
                Validation.directory_existence
            ]
        ))


    def _ask_for_domain_name(self):
        return str(Question(
            "Enter the project domain",
            [Validation.is_url],
            self._configuration["project"]["domain"]
        ))




class ProjectConfiguration:


    def setup(self):
        pass




class LaravelInstaller:


    def __init__(self, project_configuration):
        self._project_configuration = project_configuration


    def pull(self):
        run([
            "docker", "run", "--rm",
                             "--interactive",
                             "--tty",
                             "--user", f"{self._project_configuration['environment']['uid']}:{self._project_configuration['environment']['gid']}",
                             "--mount", f"type=bind,source={os.getcwd()},target=/application",
                             "--workdir", "/application",
                             "composer", "create-project", "--prefer-dist",
                                                           "--ignore-platform-reqs",
                                                           "laravel/laravel", self._project_configuration["project"]["name"]
            ],
            check = True
        )
