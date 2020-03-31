import os
import re
from laravel_docker.helpers.query import Question


class Options:
    def __init__(self):
        self.options = {
            "project": {
                "name": None
            }
        }


    def get(self):
        self._ask_project_name()

        return self.options


    def _ask_project_name(self):

        project_name = str(Question(
            "Enter the project name: ",
            [
                lambda n: n if bool(re.match('^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', n)) else ValueError("The project name is not PascalCased."),
                lambda n: n if n not in os.listdir() or not os.path.isdir(n) else ValueError(f"Another project with the name '{n}' already exists in the current directory.")
            ]
        ))

        self.options["project"]["name"] = project_name
