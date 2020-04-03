import os
import re
from collections.abc import Mapping
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




class Parser:


    def __init__(self):
        self._raw_template_string = None
        self._parsed_template_string = None


    @property
    def parsed_template_string(self):
        return self._parsed_template_string


    def read_template(self, template_path):
        with open(template_path) as template:
            self._raw_template_string = template.read()

        return self


    def add_template_string(self, template_string):
        self._raw_template_string = template_string

        return self


    def parse(self,variables, delimiters_creator = lambda variable_name: f"[[{variable_name}]]"):
        if not isinstance(variables, Mapping):
            raise ValueError("The variables argument should be a Mapping (dict).")

        if not callable(delimiters_creator):
            raise ValueError("The delimiters_creator argument should be a callable.")

        parsed_template = self._raw_template_string

        for name, value in variables.items():
            parsed_template = parsed_template.replace(delimiters_creator(name), value)

        if re.match(r'.*\[\[[A-Z][A-Z0-9_]+\]\].*', parsed_template) is not None:
            raise ValueError("There are still unparsed variables in the template.")

        self._parsed_template_string = parsed_template

        return self


    def output(self, file_path):
        if os.path.isfile(file_path):
            raise ValueError("Another file with the same name already exists.")

        with open(file_path, "w") as file:
            file.write(self._parsed_template_string)
