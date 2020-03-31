import os
import re
from laravel_docker.helpers.query import Question


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
                "name": None,
                "user": None,
                "password": None
            }
        }


    def get(self):
        self.options["project"]["name"] = self._ask_for_project_name()
        self.options["project"]["domain"] = self._ask_for_domain_name()
        self._ask_for_database_configuration()

        return self.options


    def _ask_for_project_name(self):

        return str(Question(
            "Enter the project name: ",
            [
                lambda n: n if bool(re.match('^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', n)) else ValueError("The project name is not PascalCased."),
                lambda n: n if n not in os.listdir() or not os.path.isdir(n) else ValueError(f"Another project with the name '{n}' already exists in the current directory.")
            ]
        ))


    def _ask_for_domain_name(self):
        url_regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )

        domain = str(Question(
            f"Enter the project domain [default: '{self.options['project']['domain']}']: ",
            [
                lambda domain: domain if domain == '' or re.match(url_regex, f"http://{domain}") is not None else ValueError(f"The domain '{domain}' is invalid.")
            ]
        ))

        return domain if domain != '' else self.options["project"]["domain"]


    def _ask_for_database_configuration(self):
        pass
