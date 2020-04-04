import os
import stat
from subprocess import run
from scripting_utilities.print import Print
from scripting_utilities.cd import ChangeDirectory
from scripting_utilities.skeleton import CreateSkeleton
from laravel_docker.core import ProjectConfiguration, Parser, LaravelInstaller


class Application:


    def __init__(self):
        Print.eol()
        Print.info("Setting up a new Laravel project.")
        Print.eol(2)

        self._project_configuration = None


    @property
    def project_configuration(self):
        return self._project_configuration


    def run(self):
        self._configure()

        self._structure()
        self._scaffold()

        self._laravel()
        self._git()


    def _configure(self):
        self._project_configuration = ProjectConfiguration().initialize().get()


    def _structure(self):
        CreateSkeleton({
            self.project_configuration["project"]["name"]: {
                "configuration": {
                    "nginx": {}
                },
                "dockerfiles": {
                    "php": {}
                },
                "application": {}
            }
        })


    def _scaffold(self):
        with ChangeDirectory(self.project_configuration["project"]["name"]):
            with ChangeDirectory("configuration"):
                with ChangeDirectory("nginx"):
                    # default.conf
                    (Parser().read_template(Parser.template_path("configuration/nginx/default.conf"))
                             .parse({
                                 "PROJECT_DOMAIN": self.project_configuration["project"]["domain"]
                             })
                             .output("default.conf"))

                    # utils.conf
                    (Parser().read_template(Parser.template_path("configuration/nginx/utils.conf"))
                             .parse({
                                 "PROJECT_DOMAIN": self.project_configuration["project"]["domain"]
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
                "PROJECT_NAME": self.project_configuration["project"]["name"],
                "USER_ID": self.project_configuration["environment"]["uid"],
                "GROUP_ID": self.project_configuration["environment"]["gid"]
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


    def _laravel(self):
        with ChangeDirectory(self.project_configuration["project"]["name"]):
            with ChangeDirectory("application"):
                LaravelInstaller(self.project_configuration).pull()


    def _git(self):
        with ChangeDirectory(self.project_configuration["project"]["name"]):
            commands = [
                ["git", "init"],
                ["git", "add", "."],
                ["git", "commit", "-m", "initial commit"],
                ["git", "checkout", "-b", "development"]
            ]

            for command in commands:
                run(command, check = True)
