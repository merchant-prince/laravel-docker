import os
import re
from laravel_docker.helpers.query import Question


class Options:
    def __init__(self):
        self.options = {
            "project": {
                "name": None,
                "domain": None
            },
            "environment": {
                "uid": os.geteuid(),
                "gid": os.getegid()
            },
            "database": {
                "name": None,
                "user": None,
                "password": None
            }
        }


    def get(self):
        self._ask_for_project_name()
        self._ask_for_domain_name()
        self._ask_for_database_configuration()

        return self.options


    def _ask_for_project_name(self):

        project_name = str(Question(
            "Enter the project name: ",
            [
                lambda n: n if bool(re.match('^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', n)) else ValueError("The project name is not PascalCased."),
                lambda n: n if n not in os.listdir() or not os.path.isdir(n) else ValueError(f"Another project with the name '{n}' already exists in the current directory.")
            ]
        ))

        self.options["project"]["name"] = project_name


    def _ask_for_domain_name(self):
        pass


    def _ask_for_database_configuration(self):
        pass
