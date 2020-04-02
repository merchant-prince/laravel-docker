import os
import re
from laravel_docker.helpers import Question, Validation
from scripting_utilities.skeleton import CreateSkeleton


class ProjectConfiguration:


    def __init__(self):
        self._configuration = {
            "project": {
                "name": None,
                "domain": "application.local"
            },
            "environment": {
                "uid": os.geteuid(),
                "gid": os.getegid()
            },
            "database": {
                "name": "application",
                "username": "username",
                "password": "password"
            }
        }


    def initialize(self):
        """
        Initialize the configuration dictionary. This is done by asking the
        user a few questions concerning the configuration options of the
        project.
        """

        self._configuration["project"]["name"] = self._ask_for_project_name()
        self._configuration["project"]["domain"] = self._ask_for_domain_name()

        self._configuration["database"]["name"] = self._ask_for_database_name()
        self._configuration["database"]["username"] = self._ask_for_database_username()
        self._configuration["database"]["password"] = self._ask_for_database_password()


    def get(self):
        """
        Get the current instance of the configuration dictionary.

        Returns:
            dict: The current configuration instance.
        """

        return self._configuration


    def _ask_for_project_name(self):
        return str(Question(
            "Enter the project name: ",
            [
                Validation.is_pascalcased,
                Validation.directory_existence
            ]
        ))


    def _ask_for_domain_name(self):
        return str(Question(
            f"Enter the project domain [{self._configuration['project']['domain']}]: ",
            [Validation.is_url],
            self._configuration["project"]["domain"]
        ))


    def _ask_for_database_name(self):
        return str(Question(
            f"Enter the database name [{self._configuration['database']['name']}]: ",
            [
                Validation.is_alphabetic,
                Validation.min_length(5)
            ],
            self._configuration["database"]["name"]
        ))


    def _ask_for_database_username(self):
        return str(Question(
            f"Enter the database name [{self._configuration['database']['username']}]: ",
            [Validation.min_length(5)],
            self._configuration["database"]["username"]
        ))


    def _ask_for_database_password(self):
        return str(Question(
            f"Enter the database name [{self._configuration['database']['password']}]: ",
            [Validation.min_length(5)],
            self._configuration["database"]["password"]
        ))




class Parse:


    TEMPLATE_DELIMITERS = "[[{}]]"


    def __init__(self, variables, template):
        parsed_template = template

        for name, value in variables.items():
            parsed_template = parsed_template.replace(Parse.TEMPLATE_DELIMITERS.format(name), value)

        self._parsed_template = parsed_template

        if re.match(r'.*\[\[[A-Z][A-Z0-9_]+\]\].*', self._parsed_template) is not None:
            raise ValueError("There are still unparsed variables in the template.")


    def __str__(self):
        return self._parsed_template
