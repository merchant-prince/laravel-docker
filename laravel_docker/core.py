import os
import stat
from subprocess import run
from scripting_utilities.cd import ChangeDirectory
from laravel_docker.helpers import Parser, Question, Validation


class ProjectEnvironment:
    """
    This class is responsible for asking the user questions about the project.

    Attributes:
        _configuration (dict):
            A mapping containing the project configuration.
    """


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

        self._configuration["project"]["name"] = self._query_project_name()
        self._configuration["project"]["domain"] = self._query_domain_name()

        return self


    def get(self):
        """
        Get the current instance of the configuration dictionary.

        Returns:
            dict: The current configuration instance.
        """

        return self._configuration


    def _query_project_name(self):
        return str(Question(
            "Enter the project name",
            [
                Validation.is_pascalcased,
                Validation.directory_existence
            ]
        ))


    def _query_domain_name(self):
        return str(Question(
            "Enter the project domain",
            [Validation.is_url],
            self._configuration["project"]["domain"]
        ))




class ProjectConfiguration:
    """
    This class is responsible for creating the appropriate project-level
    configuration files from the provided templates and the environment
    variables.

    Attributes:
        _configuration (dict):
            The configuration / environment variables of the project. This
            dict SHOULD NOT BE ALTERED.
    """


    def __init__(self, configuration):
        self._configuration = configuration


    def setup(self):
        """
        Set up the configuration files.
        """

        with ChangeDirectory(self._configuration["project"]["name"]):
            with ChangeDirectory("configuration"):
                with ChangeDirectory("nginx"):
                    # default.conf
                    (Parser().read_template(Parser.template_path("configuration/nginx/default.conf"))
                             .parse({
                                 "PROJECT_DOMAIN": self._configuration["project"]["domain"]
                             })
                             .output("default.conf"))

                    # utils.conf
                    (Parser().read_template(Parser.template_path("configuration/nginx/utils.conf"))
                             .parse({
                                 "PROJECT_DOMAIN": self._configuration["project"]["domain"]
                             })
                             .output("utils.conf"))

            with ChangeDirectory("dockerfiles"):
                with ChangeDirectory("php"):
                    # PHP Dockerfile
                    (Parser().read_template(Parser.template_path("dockerfiles/php/Dockerfile"))
                             .parse()
                             .output("Dockerfile"))

                    # entrypoint.sh
                    (Parser().read_template(Parser.template_path("dockerfiles/php/entrypoint.sh"))
                             .parse()
                             .output("entrypoint.sh"))

                    os.chmod("entrypoint.sh", os.stat("entrypoint.sh").st_mode | stat.S_IEXEC)

            # docker-compose.yml
            (Parser().read_template(Parser.template_path("docker-compose.yml"))
                     .parse()
                     .output("docker-compose.yml"))

            environment_variables = {
                "PROJECT_NAME": self._configuration["project"]["name"],
                "USER_ID": self._configuration["environment"]["uid"],
                "GROUP_ID": self._configuration["environment"]["gid"]
            }

            # .env (for docker-compose)
            (Parser().read_template(Parser.template_path("project.env"))
                     .parse(environment_variables)
                     .output(".env"))

            # .env.example
            (Parser().read_template(Parser.template_path("project.env"))
                     .parse({ name: "" for name in environment_variables })
                     .output(".env.example"))

            # run.py
            (Parser().read_template(Parser.template_path("run.py"))
                     .parse()
                     .output("run.py"))

            os.chmod("run.py", os.stat("run.py").st_mode | stat.S_IEXEC)

            # .gitignore
            (Parser().read_template(Parser.template_path("project.gitignore"))
                     .parse()
                     .output(".gitignore"))




class LaravelInstaller:
    """
    This class is responsible for pulling a fresh Laravel instance into the
    current project.

    Attributes:
        _configuration (dict):
            The configuration / environment variables of the project. This
            dict SHOULD NOT BE ALTERED.
    """


    def __init__(self, configuration):
        self._configuration = configuration


    def pull(self):
        """
        Pull a fresh Laravel application.
        """

        run([
            "docker", "run", "--rm",
                             "--interactive",
                             "--tty",
                             "--user", f"{self._configuration['environment']['uid']}:{self._configuration['environment']['gid']}",
                             "--mount", f"type=bind,source={os.getcwd()},target=/application",
                             "--workdir", "/application",
                             "composer", "create-project", "--prefer-dist",
                                                           "--ignore-platform-reqs",
                                                           "laravel/laravel", self._configuration["project"]["name"]
            ],
            check = True
        )




class Git:
    """
    Initialize a new git repository in the current directory.
    """


    @staticmethod
    def initialize():
        """
        Initialize, create the first commit, and checkout to a new development
        branch.
        """

        commands = [
            ["git", "init"],
            ["git", "add", "."],
            ["git", "commit", "-m", "initial commit"],
            ["git", "checkout", "-b", "development"]
        ]

        for command in commands:
            run(command, check = True)
