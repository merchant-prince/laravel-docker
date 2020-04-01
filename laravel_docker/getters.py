import os
import re
from laravel_docker.helpers import Question, Validation


class Options:
    def __init__(self):
        self.options = {
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


    def get(self):
        self.options["project"]["name"] = self._ask_for_project_name()
        self.options["project"]["domain"] = self._ask_for_domain_name()

        self.options["database"]["name"] = self._ask_for_database_name()
        self.options["database"]["username"] = self._ask_for_database_username()
        self.options["database"]["password"] = self._ask_for_database_password()

        return self.options


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
            f"Enter the project domain [{self.options['project']['domain']}]: ",
            [Validation.is_url],
            self.options["project"]["domain"]
        ))


    def _ask_for_database_name(self):
        return str(Question(
            f"Enter the database name [{self.options['database']['name']}]: ",
            [lambda n: n == '' or (Validation.is_alphabetic(n) and Validation.min_length(5)(n))],
            self.options["database"]["name"]
        ))


    def _ask_for_database_username(self):
        return str(Question(
            f"Enter the database name [{self.options['database']['username']}]: ",
            [lambda n: n == '' or (Validation.is_alphabetic(n) and Validation.min_length(5)(n))],
            self.options["database"]["username"]
        ))


    def _ask_for_database_password(self):
        return str(Question(
            f"Enter the database name [{self.options['database']['password']}]: ",
            [lambda n: n == '' or (Validation.is_alphabetic(n) and Validation.min_length(5)(n))],
            self.options["database"]["password"]
        ))
