import os
import re
from laravel_docker.helpers import Question, Validation


class Configuration:
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
            [lambda n: n == '' or (Validation.is_alphabetic(n) and Validation.min_length(5)(n))],
            self._configuration["database"]["name"]
        ))


    def _ask_for_database_username(self):
        return str(Question(
            f"Enter the database name [{self._configuration['database']['username']}]: ",
            [lambda n: n == '' or (Validation.is_alphabetic(n) and Validation.min_length(5)(n))],
            self._configuration["database"]["username"]
        ))


    def _ask_for_database_password(self):
        return str(Question(
            f"Enter the database name [{self._configuration['database']['password']}]: ",
            [lambda n: n == '' or (Validation.is_alphabetic(n) and Validation.min_length(5)(n))],
            self._configuration["database"]["password"]
        ))
