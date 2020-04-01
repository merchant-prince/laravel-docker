import os
import re
from laravel_docker.helpers.query import Question
import laravel_docker.helpers.validation as validators


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
                validators.is_pascalcased,
                validators.directory_does_not_exist
            ]
        ))


    def _ask_for_domain_name(self):
        return str(Question(
            f"Enter the project domain [{self.options['project']['domain']}]: ",
            [validators.is_url],
            self.options["project"]["domain"]
        ))


    def _ask_for_database_name(self):
        return str(Question(
            f"Enter the database name [{self.options['database']['name']}]: ",
            [lambda n: n == '' or (validators.is_alphabetic(n) and validators.min_length(5)(n))],
            self.options["database"]["name"]
        ))


    def _ask_for_database_username(self):
        return str(Question(
            f"Enter the database name [{self.options['database']['username']}]: ",
            [lambda n: n == '' or (validators.is_alphabetic(n) and validators.min_length(5)(n))],
            self.options["database"]["username"]
        ))


    def _ask_for_database_password(self):
        return str(Question(
            f"Enter the database name [{self.options['database']['password']}]: ",
            [lambda n: n == '' or (validators.is_alphabetic(n) and validators.min_length(5)(n))],
            self.options["database"]["password"]
        ))
